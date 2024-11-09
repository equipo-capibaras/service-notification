from typing import Any, cast

import requests

from repositories import MailRepository

from .base import RestBaseRepository
from .util import TokenProvider


class SendgridMailRepository(MailRepository, RestBaseRepository):
    def __init__(self, token_provider: TokenProvider | None) -> None:
        RestBaseRepository.__init__(self, '', token_provider)

    def send(
        self, sender: tuple[str | None, str], receiver: tuple[str | None, str], subject: str, text: str, reply_to: str | None
    ) -> None:
        receiver_dict = {'email': receiver[1]}
        if receiver[0] is not None:
            receiver_dict['name'] = receiver[0]

        sender_dict = {'email': sender[1]}
        if sender[0] is not None:
            sender_dict['name'] = sender[0]

        data = {
            'personalizations': [
                {
                    'to': [receiver_dict],
                }
            ],
            'from': sender_dict,
            'headers': {},
            'subject': subject,
            'content': [{'type': 'text/plain', 'value': text}],
        }

        if reply_to is not None:
            cast(dict[str, Any], data['headers'])['In-Reply-To'] = reply_to
            cast(dict[str, Any], data['headers'])['References'] = reply_to

        resp = self.authenticated_post('https://api.sendgrid.com/v3/mail/send', json=data)

        if resp.status_code == requests.codes.accepted:
            return

        self.unexpected_error(resp)
