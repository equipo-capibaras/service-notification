from typing import Any, cast
from unittest import TestCase
from unittest.mock import Mock

from faker import Faker

from app import create_app
from models import Action, Channel, Plan, Role
from repositories import MailRepository


class TestEvent(TestCase):
    def setUp(self) -> None:
        self.faker = Faker()

        self.app = create_app()
        self.client = self.app.test_client()

    def gen_random_event_data(self) -> dict[str, Any]:
        return {
            'id': cast(str, self.faker.uuid4()),
            'name': self.faker.sentence(3),
            'channel': self.faker.random_element(list(Channel)),
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
                {
                    'seq': 1,
                    'date': self.faker.past_datetime().isoformat().replace('+00:00', 'Z'),
                    'action': Action.ESCALATED,
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

    def test_health(self) -> None:
        mail_repo_mock = Mock(MailRepository)

        with self.app.container.mail_repo.override(mail_repo_mock):
            resp = self.client.post('/api/v1/incident-update/notification', json=self.gen_random_event_data())

        self.assertEqual(resp.status_code, 200)
