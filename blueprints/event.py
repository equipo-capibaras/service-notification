from dataclasses import dataclass, field
from datetime import datetime

import marshmallow_dataclass
from flask import Blueprint, Response, current_app, request
from flask.views import MethodView

from models import Action, Channel, Plan, Role

from .util import class_route, json_response

blp = Blueprint('Event', __name__)


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


@class_route(blp, '/api/v1/incident-update/notification')
class UpdateEvent(MethodView):
    init_every_request = False

    response = json_response({'message': 'Event processed.', 'code': 200}, 200)

    def post(self) -> Response:
        current_app.logger.error(request.headers)
        current_app.logger.error(request.data.decode('utf-8'))

        req_json = request.get_json(silent=True)
        if req_json is None:
            raise ValueError('Invalid JSON body')

        req_json['reported_by'] = req_json.pop('reportedBy')
        req_json['created_by'] = req_json.pop('createdBy')
        req_json['assigned_to'] = req_json.pop('assignedTo')
        req_json['client']['email_incidents'] = req_json['client'].pop('emailIncidents')

        event_schema = marshmallow_dataclass.class_schema(EventBody)()
        data: EventBody = event_schema.load(req_json)

        current_app.logger.error(str(data))

        return self.response
