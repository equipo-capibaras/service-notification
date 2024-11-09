import json
from typing import cast
from unittest.mock import Mock

import responses
from faker import Faker
from requests import HTTPError
from unittest_parametrize import ParametrizedTestCase, parametrize

from repositories.rest import SendgridMailRepository, TokenProvider


class TestMail(ParametrizedTestCase):
    def setUp(self) -> None:
        self.faker = Faker()
        self.base_url = self.faker.url().rstrip('/')
        self.repo = SendgridMailRepository(None)

    def test_authenticated_post_without_token_provider(self) -> None:
        repo = SendgridMailRepository(None)

        with responses.RequestsMock() as rsps:
            rsps.post(self.base_url)
            repo.authenticated_post(self.base_url, json={})
            self.assertNotIn('Authorization', rsps.calls[0].request.headers)

    def test_authenticated_get_with_token_provider(self) -> None:
        token = self.faker.pystr()
        token_provider = Mock(TokenProvider)
        cast(Mock, token_provider.get_token).return_value = token

        repo = SendgridMailRepository(token_provider)

        with responses.RequestsMock() as rsps:
            rsps.post(self.base_url)
            repo.authenticated_post(self.base_url, json={})
            self.assertEqual(rsps.calls[0].request.headers['Authorization'], f'Bearer {token}')

    @parametrize(
        ('has_sender_name', 'has_receiver_name', 'reply_to'),
        [
            (False, False, None),
            (True, False, None),
            (False, True, None),
            (True, True, None),
            (False, False, '<S6HpplnTSkmW7zQ0Si7Z8A@geopod-ismtpd-4>'),
            (True, False, '<S6HpplnTSkmW7zQ0Si7Z8A@geopod-ismtpd-4>'),
            (False, True, '<S6HpplnTSkmW7zQ0Si7Z8A@geopod-ismtpd-4>'),
            (True, True, '<S6HpplnTSkmW7zQ0Si7Z8A@geopod-ismtpd-4>'),
        ],
    )
    def test_send(self, *, has_sender_name: bool, has_receiver_name: bool, reply_to: str | None) -> None:
        sender_email = self.faker.email()
        sender_name = self.faker.name()

        receiver_email = self.faker.email()
        receiver_name = self.faker.name()

        subject = self.faker.sentence(4)
        text = self.faker.text()

        with responses.RequestsMock() as rsps:
            rsps.post(
                'https://api.sendgrid.com/v3/mail/send',
                status=202,
            )

            self.repo.send(
                sender=(sender_name if has_sender_name else None, sender_email),
                receiver=(receiver_name if has_receiver_name else None, receiver_email),
                subject=subject,
                text=text,
                reply_to=reply_to,
            )

            body = cast(str | bytes, rsps.calls[0].request.body)
            req_json = json.loads(body)

            self.assertEqual(len(req_json['personalizations']), 1)
            self.assertEqual(len(req_json['personalizations'][0]['to']), 1)

            self.assertEqual(req_json['personalizations'][0]['to'][0]['email'], receiver_email)
            if has_receiver_name:
                self.assertEqual(req_json['personalizations'][0]['to'][0]['name'], receiver_name)
            else:
                self.assertNotIn('name', req_json['personalizations'][0]['to'][0])

            self.assertEqual(req_json['from']['email'], sender_email)
            if has_sender_name:
                self.assertEqual(req_json['from']['name'], sender_name)
            else:
                self.assertNotIn('name', req_json['from'])

            self.assertEqual(req_json['subject'], subject)

            self.assertEqual(req_json['content'][0]['type'], 'text/plain')
            self.assertEqual(req_json['content'][0]['value'], text)

            if reply_to is not None:
                self.assertEqual(req_json['headers']['In-Reply-To'], reply_to)
                self.assertEqual(req_json['headers']['References'], reply_to)

    @parametrize(
        ('status',),
        [
            (200,),
            (500,),
        ],
    )
    def test_send_error(self, status: int) -> None:
        sender_email = self.faker.email()
        sender_name = self.faker.name()

        receiver_email = self.faker.email()
        receiver_name = self.faker.name()

        subject = self.faker.sentence(4)
        text = self.faker.text()

        with responses.RequestsMock() as rsps:
            rsps.post(
                'https://api.sendgrid.com/v3/mail/send',
                status=status,
            )

            with self.assertRaises(HTTPError):
                self.repo.send(
                    sender=(sender_name, sender_email),
                    receiver=(receiver_name, receiver_email),
                    subject=subject,
                    text=text,
                    reply_to=None,
                )
