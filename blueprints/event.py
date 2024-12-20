from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib import resources as impresources
from typing import cast

import marshmallow_dataclass
from dependency_injector.wiring import Provide
from flask import Blueprint, Response, request
from flask.views import MethodView

from containers import Container
from models import Action, Channel, Plan, Risk, Role
from repositories import MailRepository

from . import mails
from .util import class_route, json_response

blp = Blueprint('Event', __name__)

EVENT_PROCESSED = 'Event processed.'


@dataclass
class UserBody:
    id: str
    name: str
    email: str
    role: Role = field(metadata={'by_value': True})


@dataclass
class ClientBody:
    id: str
    name: str
    email_incidents: str
    plan: Plan = field(metadata={'by_value': True})


@dataclass
class HistoryBody:
    seq: int
    date: datetime
    action: Action = field(metadata={'by_value': True})
    description: str


@dataclass
class EventBody:
    id: str
    name: str
    channel: Channel = field(metadata={'by_value': True})
    language: str
    reported_by: UserBody
    created_by: UserBody
    assigned_to: UserBody
    history: list[HistoryBody]
    client: ClientBody
    risk: Risk | None = field(metadata={'by_value': True})


class ResponseMail:
    def __init__(
        self,
        sender: tuple[str | None, str],
        receiver: tuple[str | None, str],
        subject: str,
        reply_to: str | None,
        language: str,
    ) -> None:
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.reply_to = reply_to
        self.language = language

    def send(self, text: str, mail_repo: MailRepository = Provide[Container.mail_repo]) -> None:
        mail_repo.send(
            sender=self.sender,
            receiver=self.receiver,
            subject=self.subject,
            text=text,
            reply_to=self.reply_to,
        )

    def send_template(self, template: str, **kwargs: object) -> None:
        response_file = impresources.files(mails) / f'{template}.{self.language}.txt'
        with response_file.open('r') as f:
            response_text = f.read().format(**kwargs)

        self.send(response_text)


def load_event_data() -> EventBody:
    req_json = request.get_json(silent=True)
    if req_json is None:
        raise ValueError('Invalid JSON body')

    req_json['reported_by'] = req_json.pop('reportedBy')
    req_json['created_by'] = req_json.pop('createdBy')
    req_json['assigned_to'] = req_json.pop('assignedTo')
    req_json['client']['email_incidents'] = req_json['client'].pop('emailIncidents')

    event_schema = marshmallow_dataclass.class_schema(EventBody)()
    return cast(EventBody, event_schema.load(req_json))


@class_route(blp, '/api/v1/incident-update/notification')
class UpdateEvent(MethodView):
    init_every_request = False

    response = json_response({'message': EVENT_PROCESSED, 'code': 200}, 200)

    def mail_created(self, data: EventBody, mail: ResponseMail) -> None:
        if data.channel == Channel.EMAIL:
            return

        mail.send_template('created', client_name=data.client.name)

    def mail_updated(self, data: EventBody, mail: ResponseMail) -> None:
        state_translated = {
            Action.CREATED: {'es': 'creado', 'pt': 'criado'},
            Action.ESCALATED: {'es': 'escalado', 'pt': 'escalado'},
            Action.CLOSED: {'es': 'cerrado', 'pt': 'fechado'},
        }

        new_state = state_translated[data.history[-1].action][data.language]

        old_action = data.history[-2].action
        if old_action == Action.AI_RESPONSE:
            old_action = data.history[-3].action

        old_state = state_translated[old_action][data.language]

        mail.send_template(
            'updated',
            client_name=data.client.name,
            old_state=old_state,
            new_state=new_state,
            comment=data.history[-1].description,
        )

    def basic_mail(self, template_type: str, data: EventBody, mail: ResponseMail) -> None:
        mail.send_template(
            template_type,
            client_name=data.client.name,
            comment=data.history[-1].description,
        )

    def post(self) -> Response:
        data = load_event_data()

        mail = ResponseMail(
            sender=(data.client.name, data.client.email_incidents),
            receiver=(data.reported_by.name, data.reported_by.email),
            subject=f'Re: {data.name}',
            reply_to=None,
            language=data.language,
        )

        if data.history[-1].action == Action.CREATED:
            self.mail_created(data, mail)
        elif data.history[-1].action == Action.ESCALATED:
            self.mail_updated(data, mail)
        elif data.history[-1].action == Action.CLOSED:
            self.basic_mail('closed', data, mail)
        elif data.history[-1].action == Action.AI_RESPONSE:
            self.basic_mail('iaresponse', data, mail)

        return self.response


@class_route(blp, '/api/v1/incident-alert/notification')
class UpdateRiskEvent(MethodView):
    init_every_request = False

    response = json_response({'message': EVENT_PROCESSED, 'code': 200}, 200)

    def post(self) -> Response:
        data = load_event_data()

        mail = ResponseMail(
            sender=(data.client.name, data.client.email_incidents),
            receiver=(data.assigned_to.name, data.assigned_to.email),
            subject=f'Incidente urgente: {data.name}',
            reply_to=None,
            language=data.language,
        )

        time_elapsed = (datetime.now(UTC) - data.history[0].date.replace(tzinfo=UTC)).total_seconds() // 3600
        base_url = data.client.email_incidents.split('@')[1]

        mail.send_template(
            'urgent',
            client_name=data.client.name,
            description=data.history[0].description,
            time=time_elapsed,
            url=f'https://{base_url}/incidents/{data.id}',
        )

        return self.response


@class_route(blp, '/api/v1/incident-risk-updated/notification')
class AlertEvent(MethodView):
    init_every_request = False

    response = json_response({'message': EVENT_PROCESSED, 'code': 200}, 200)

    def post(self) -> Response:
        data = load_event_data()

        subject_text = {'es': 'Riesgo actualizado', 'pt': 'Risco atualizado'}

        risk_translated = {
            Risk.HIGH: {'es': 'Alto', 'pt': 'Alto'},
            Risk.MEDIUM: {'es': 'Medio', 'pt': 'Médio'},
            Risk.LOW: {'es': 'Bajo', 'pt': 'Baixo'},
        }

        mail = ResponseMail(
            sender=(data.client.name, data.client.email_incidents),
            receiver=(data.assigned_to.name, data.assigned_to.email),
            subject=f'{subject_text[data.language]}: {data.name}',
            reply_to=None,
            language=data.language,
        )

        base_url = data.client.email_incidents.split('@')[1]

        if data.risk is not None:
            mail.send_template(
                'updaterisk',
                incident_name=data.name,
                client_name=data.client.name,
                url=f'https://{base_url}/incidents/{data.id}',
                risk_level=risk_translated[data.risk][data.language],
            )

        return self.response
