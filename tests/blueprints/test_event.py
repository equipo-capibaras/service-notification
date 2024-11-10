from unittest import TestCase

from app import create_app


class TestHealth(TestCase):
    def setUp(self) -> None:
        app = create_app()
        self.client = app.test_client()

    def test_health(self) -> None:
        resp = self.client.post('/api/v1/incident-update/notification', json={})

        self.assertEqual(resp.status_code, 200)
