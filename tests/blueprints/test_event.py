from typing import Any, cast
from unittest.mock import Mock

from faker import Faker
from unittest_parametrize import ParametrizedTestCase, parametrize

from app import create_app
from models import Action, Channel, Plan, Role
from repositories import MailRepository


class TestEvent(ParametrizedTestCase):
    def setUp(self) -> None:
        self.faker = Faker()

        self.app = create_app()
        self.client = self.app.test_client()

    def gen_random_event_data(self, channel: Channel | None = None) -> dict[str, Any]:
        return {
            'id': cast(str, self.faker.uuid4()),
            'name': self.faker.sentence(3),
            'channel': channel or self.faker.random_element(list(Channel)),
            'language': self.faker.random_element(['es', 'pt']),
            'reportedBy': {
                'id': cast(str, self.faker.uuid4()),
                'name': self.faker.name(),
                'email': self.faker.email(),
                'role': Role.USER,
            },
            'createdBy': {
                'id': cast(str, self.faker.uuid4()),
                'name': self.faker.name(),
                'email': self.faker.email(),
                'role': Role.USER,
            },
            'assignedTo': {
                'id': cast(str, self.faker.uuid4()),
                'name': self.faker.name(),
                'email': self.faker.email(),
                'role': Role.AGENT,
            },
            'history': [
                {
                    'seq': 0,
                    'date': self.faker.past_datetime().isoformat().replace('+00:00', 'Z'),
                    'action': Action.CREATED,
                    'description': self.faker.text(200),
                },
            ],
            'client': {
                'id': cast(str, self.faker.uuid4()),
                'name': self.faker.name(),
                'emailIncidents': self.faker.email(),
                'plan': self.faker.random_element(list(Plan)),
            },
        }

    @parametrize(
        ('state', 'channel', 'expect_mail'),
        [
            ('created', Channel.EMAIL, False),
            ('created', Channel.WEB, True),
            ('created', Channel.MOBILE, True),
            ('escalated', None, True),
            ('closed', None, True),
        ],
    )
    def test_update(self, *, state: str, channel: Channel | None, expect_mail: bool) -> None:
        mail_repo_mock = Mock(MailRepository)

        data = self.gen_random_event_data(channel=channel)
        if state != 'created':
            data['history'].append(
                {
                    'seq': 1,
                    'date': self.faker.past_datetime().isoformat().replace('+00:00', 'Z'),
                    'action': Action.ESCALATED if state == 'escalated' else Action.CLOSED,
                    'description': self.faker.text(200),
                },
            )

        with self.app.container.mail_repo.override(mail_repo_mock):
            resp = self.client.post('/api/v1/incident-update/notification', json=data)

        if expect_mail:
            cast(Mock, mail_repo_mock.send).assert_called_once()
        else:
            cast(Mock, mail_repo_mock.send).assert_not_called()

        self.assertEqual(resp.status_code, 200)
