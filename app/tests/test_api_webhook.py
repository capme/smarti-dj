import json
from rest_framework.test import APITestCase
from faker import Factory
from pickup.views import get_hexdigest
from collections import OrderedDict
from django.conf import settings

fake = Factory.create()

class TestAPIWebhook(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.secret_string = settings.WEBHOOK_SECRET_KEY
        cls.cpms_channel_id = settings.CHANNEL_ID

    def test_valid_webhook(self):
        """Calling this webhook with a valid signature"""
        data = json.loads("""{"orderId": "101023207", "orderStatus": [{"orderStatusDetail": null, "updatedTime": "2017-02-03T10:33:31Z", "orderStatus": "IN_PROGRESS"}], "partnerId": 1074, "orderDetailedStatus": [{"updatedTime": "2017-02-03T10:33:31Z", "orderUpdatedTime": "2017-02-03T10:30:00Z", "orderDetailedStatus": "IN_TRANSIT"}], "shipPackage": [{"trackingId": "1074000015974910"}]}""", object_pairs_hook=OrderedDict)
        body = json.dumps(data, separators=(',', ':'))
        signature = get_hexdigest(body, self.secret_string)
        resp = self.client.post('/hook',
                         data, format='json', HTTP_X_ACOMM_SIGNATURE=signature)
        self.assertEqual(resp.status_code, 200)

    def test_nosignature(self):
        """Calling this webhook with an invalid signature"""
        data = json.loads(
            """{"orderId": "101023207", "orderStatus": [{"orderStatusDetail": null, "updatedTime": "2017-02-03T10:33:31Z", "orderStatus": "IN_PROGRESS"}], "partnerId": 1074, "orderDetailedStatus": [{"updatedTime": "2017-02-03T10:33:31Z", "orderUpdatedTime": "2017-02-03T10:30:00Z", "orderDetailedStatus": "IN_TRANSIT"}], "shipPackage": [{"trackingId": "1074000015974910"}]}""",
            object_pairs_hook=OrderedDict)
        body = json.dumps(data, separators=(',', ':'))
        signature = get_hexdigest(body, 'Invalid key')
        resp = self.client.post('/hook',
                                data, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_invalid_webhook(self):
        """Calling this webhook with an invalid signature"""
        data = json.loads(
            """{"orderId": "101023207", "orderStatus": [{"orderStatusDetail": null, "updatedTime": "2017-02-03T10:33:31Z", "orderStatus": "IN_PROGRESS"}], "partnerId": 1074, "orderDetailedStatus": [{"updatedTime": "2017-02-03T10:33:31Z", "orderUpdatedTime": "2017-02-03T10:30:00Z", "orderDetailedStatus": "IN_TRANSIT"}], "shipPackage": [{"trackingId": "1074000015974910"}]}""",
            object_pairs_hook=OrderedDict)
        body = json.dumps(data, separators=(',', ':'))
        signature = get_hexdigest(body, 'Invalid key')
        resp = self.client.post('/hook',
                                data, format='json', HTTP_X_ACOMM_SIGNATURE=signature)
        self.assertEqual(resp.status_code, 401)