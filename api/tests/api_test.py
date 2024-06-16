import json

import pytest
from django.core.files.base import ContentFile
from django.test import Client
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from rest_framework.test import APITestCase

from api.tests.conftest import rules_json
from loader.loaders import GmailLoader


@pytest.mark.django_db
class TestPingAPI:
    ENDPOINT = reverse("ping")

    def test_application_creation(self, client: Client) -> None:
        res = client.get(self.ENDPOINT)
        assert res.status_code == 200


class TestProcessEmailAPI(APITestCase):
    def setUp(self):
        self.payload = rules_json()

    def test_process_email(self) -> None:
        GmailLoader().load_data(10)

        json_payload = json.dumps(self.payload)

        json_file = ContentFile(json_payload, "metadata.json")

        encoded_data = encode_multipart(BOUNDARY, data=dict(file=json_file))

        url = "/api/email/process/"
        headers = {"Content-Type": MULTIPART_CONTENT}

        response = self.client.post(
            url, data=encoded_data, content_type=MULTIPART_CONTENT, headers=headers
        )

        self.assertEqual(response.status_code, 200)
