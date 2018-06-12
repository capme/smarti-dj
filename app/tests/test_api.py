from django.conf import settings
from lazacom_auth.tests.test_api import AuthTestCase
from pickup.models import PickUp
from pickup.tests.faker import fake
from unittest import mock
import pendulum


class TestAPIPickupNotValidusername(AuthTestCase):
    @mock.patch('pickup.tasks.create_pickup.delay')
    def test_pickup(self, crt_pickup):
        """Test create new pickup data"""
        response = self.client.post('/pickup', format='json', data=fake.create_pickup_data())
        self.assertEquals(response.status_code, 401)
        self.assertFalse(crt_pickup.called)


class TestAPIPickup(AuthTestCase):

    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_X_USER_NAME=settings.PUBLICAPI_USERNAME)

    @mock.patch('pickup.tasks.create_pickup.run')
    def test_pickup(self, crt_pickup):
        """Test create new pickup data"""
        response = self.client.post('/pickup', format='json', data=fake.create_pickup_data())
        self.assertEquals(response.status_code, 201)
        self.assertTrue(crt_pickup.called)

    @mock.patch('pickup.tasks.create_pickup.run')
    def test_pickup_already_exist(self, crt_pickup):
        """Test create pickup already exists"""
        fake.create_pickup_to_db()
        data = fake.create_pickup_another_data()
        get_packageid = PickUp.objects.filter(package_id=data['package_id'])
        resp = self.client.post('/pickup', data, format='json')
        self.assertEquals(resp.status_code, 201)
        self.assertEquals(1, len(get_packageid))

        crt_pickup.assert_called_once_with(
            package_uuid=data['package_uuid'],
            package_id=data['package_id'],
            tracking_number=data['tracking_number'],
            package_created_at=pendulum.parse(data['package_created_at']),
        )

    @mock.patch('pickup.tasks.create_pickup.delay')
    def test_pickup_invalid_payload(self, crt_pickup):
        """Test create pickup with invalid data"""
        data = {}
        resp = self.client.post('/pickup', data, format='json')
        self.assertEquals(resp.status_code, 400)
        self.assertEqual(crt_pickup.call_count, 0)

    @mock.patch('pickup.tasks.create_pickup.delay')
    def test_pickup_invalid_date(self, crt_pickup):
        """Test create pickup with invalid data"""
        data = {
            "package_uuid": "lazada-package-id",
            "package_id": "MPDS-12456722396-098",
            "tracking_number": "0300123456781",
            "package_created_at": "THISISNOTAVALIDDATEYO"
        }
        resp = self.client.post('/pickup', data, format='json')
        self.assertEquals(resp.status_code, 400)
        self.assertEqual(crt_pickup.call_count, 0)