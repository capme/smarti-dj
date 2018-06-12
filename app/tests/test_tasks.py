from unittest.mock import patch, PropertyMock, ANY
from django.conf import settings
from django.test.testcases import TestCase
from django.db import DatabaseError
from celery.exceptions import Retry
from requests.exceptions import RequestException
from pickup.tasks import create_pickup, check_webhook, update_to_lazada_task
from pickup.tests.faker import fake
from pickup.models import PickUp
from datetime import timezone as dt_tz
from django.utils import timezone
from faker import Factory


fake_factory = Factory.create()


class TestCreatePickUp(TestCase):
    def setUp(self):
        super().setUp()

    def test_create_pickup(self):
        """Test task create new pickup data"""
        fake_data = fake.create_pickup_data()
        pickup, created = create_pickup(**fake_data)
        pickup_db = PickUp.objects.filter(pk=pickup).first()
        self.assertEquals(pickup_db.package_uuid, fake_data['package_uuid'])
        self.assertEquals(pickup_db.package_id, fake_data['package_id'])
        self.assertEquals(pickup_db.tracking_number, str(fake_data['tracking_number']))
        self.assertEquals(created, True)

    def test_create_pickup_already_exists(self):
        """Test create pickup already exists data"""
        fake_data = fake.create_pickup_another_data()
        fake.create_pickup_to_db()
        pickup, created = create_pickup(**fake_data)
        pickup_db = PickUp.objects.filter(pk=pickup).first()
        self.assertEquals(pickup_db.package_uuid, fake_data['package_uuid'])
        self.assertEquals(pickup_db.package_id, fake_data['package_id'])
        self.assertEquals(pickup_db.tracking_number, str(fake_data['tracking_number']))
        self.assertEquals(created, False)

    @patch('pickup.services.LazadaTPS.update_status')
    @patch('pickup.services.LazadaTPS.token', new_callable=PropertyMock, return_value='WAKWAWTOKEN')
    def test_update_to_lazada_ok(self, mock_token, mock_update):
        """Test update to lazada pickup status"""
        pickup = fake.create_pickup_to_db2()
        timestamp = timezone.now()
        status = 'IN_TRANSIT'
        update_to_lazada_task.delay(pickup.id, status=status, timestamp=timestamp)
        mock_update.assert_called_once_with(package_uuid=pickup.package_uuid, tracking_id=pickup.tracking_number,
                                            status=status, timestamp=timestamp, comments=ANY)


    @patch('pickup.services.LazadaTPS.update_status')
    @patch('pickup.services.LazadaTPS.token', new_callable=PropertyMock, return_value='WAKWAWTOKEN')
    @patch('pickup.tasks.PickUp.objects.get', side_effect=DatabaseError())
    def test_update_to_lazada_db_error(self, mock_dbget, mock_token, mock_update):
        """Database error should retry"""
        pickup = fake.create_pickup_to_db2()
        timestamp = timezone.now()
        status = 'IN_TRANSIT'
        with self.assertRaises(DatabaseError):
            update_to_lazada_task.delay(pickup.id, status=status, timestamp=timestamp)
        mock_update.assert_not_called()
        self.assertEqual(settings.LAZADA_UPDATE_RETRIES + 1, mock_dbget.call_count)

    @patch('pickup.services.LazadaTPS.update_status', side_effect=RequestException())
    @patch('pickup.services.LazadaTPS.token', new_callable=PropertyMock, return_value='WAKWAWTOKEN')
    def test_update_to_lazada_req_error(self, mock_token, mock_update):
        """Connection error should retry"""
        pickup = fake.create_pickup_to_db2()
        timestamp = timezone.now()
        status = 'IN_TRANSIT'
        with self.assertRaises(RequestException):
            update_to_lazada_task.delay(pickup.id, status=status, timestamp=timestamp)
        self.assertEqual(settings.LAZADA_UPDATE_RETRIES + 1, mock_update.call_count)


class TestCheckWebhook(TestCase):
    def setUp(self):
        self.pickup = fake.create_pickup_to_db()

    @patch('pickup.tasks.update_to_lazada_task.delay')
    def test_nonexisting_tracking(self, update_fn):
        """Test with non-existing tracking number in DB"""
        payload = {
            'orderId': '230948012',
            'partnerId': 786,
            'orderStatus': [
                {
                    'orderStatus': 'NEW',
                    'updatedTime': '2017-10-05T04:45:33Z',
                    'orderStatusDetail': None
                }
            ],
            'shipPackage': [{'trackingId': 'SM786624753046914659'}],
            'orderDetailedStatus': [
                {
                    'updatedTime': '2017-10-05T04:45:33Z',
                    'orderUpdatedTime': '2017-10-05T04:45:32Z',
                    'orderDetailedStatus': 'READY_TO_SHIP'
                }
            ]
        }
        ret = check_webhook(payload)
        self.assertFalse(ret)
        update_fn.assert_not_called()

    @patch('pickup.tasks.update_to_lazada_task.delay')
    def test_no_shippackage(self, update_fn):
        """Test payload with no shipPackage"""
        payload = {'orderId': '230948012', 'partnerId': 786, 'orderStatus': [
            {'orderStatus': 'NEW', 'updatedTime': '2017-10-05T00:12:03Z', 'orderStatusDetail': None}],
                   'shipPackage': [], 'orderDetailedStatus': [
                {'updatedTime': '2017-10-05T00:12:03Z', 'orderUpdatedTime': '2017-10-05T00:12:03Z',
                 'orderDetailedStatus': 'NEW'}]}
        ret = check_webhook(payload)
        self.assertFalse(ret)
        update_fn.assert_not_called()

    @patch('pickup.tasks.update_to_lazada_task.delay')
    def test_no_orderdetailedstatus(self, update_fn):
        """Test payload with no orderDetailedStatus"""
        payload = {'partnerId': 786, 'orderId': '230948012', 'shipPackage': [{'trackingId': 'SM786624753046914659',
                                                                              'statusHistory': [
                                                                                  {'shippingStatus': 'IN_TRANSIT',
                                                                                   'shippingLocation': 'Singapore',
                                                                                   'shippingDetail': 'On the way to deliver',
                                                                                   'updatedTime': '2017-10-06T06:30:59Z',
                                                                                   'shippingUpdatedTime': '2017-10-06T05:54:10Z'}]}]}
        ret = check_webhook(payload)
        self.assertFalse(ret)
        update_fn.assert_not_called()

    @patch('pickup.tasks.update_to_lazada_task.delay')
    def test_statuses(self, update_fn):
        """Check against statuses"""
        statuses = [
            'NEW',
            'READY_TO_PICK',
            'READY_TO_SHIP',
            'IN_TRANSIT',
            'COMPLETED',
            'FAILED_TO_DELIVER',
            'CANCELLED',
            'REJECTED',
        ]
        for status in statuses:
            update_fn.reset_mock()
            pickup = PickUp.objects.create(
                package_uuid=fake_factory.uuid4(),
                package_id=fake.ean13()+status,
                tracking_number="030010405038-status-"+status,
                package_created_at=fake.date_time_between(start_date="-30d", end_date="-15d", tzinfo=dt_tz.utc)
            )
            payload = {
                'orderId': fake.ean()+'-'+status,
                'partnerId': 786,
                'orderStatus': [
                    {
                        'orderStatus': status,
                        'updatedTime': fake.date_time_between(start_date="-14d", end_date="now", tzinfo=dt_tz.utc).isoformat(),
                        'orderStatusDetail': None
                    }
                ],
                'shipPackage': [{'trackingId': pickup.tracking_number}],
                'orderDetailedStatus': [
                    {
                        'updatedTime': fake.date_time_between(start_date="-14d", end_date="now", tzinfo=dt_tz.utc).isoformat(),
                        'orderUpdatedTime': fake.date_time_between(start_date="-14d", end_date="now", tzinfo=dt_tz.utc).isoformat(),
                        'orderDetailedStatus': status
                    }
                ]
            }
            ret = check_webhook(payload)
            self.assertEqual(ret, pickup.id)
            pickup.refresh_from_db()
            self.assertEqual(pickup.order_id, payload['orderId'])
            self.assertEqual(pickup.last_status, status)
            self.assertEqual(pickup.status_history[status], payload['orderDetailedStatus'][0]['updatedTime'])
            if status == 'COMPLETED':
                self.assertTrue(pickup.is_delivered)
            else:
                self.assertFalse(pickup.is_delivered)
            if status in settings.UPDATE_LAZADA_STATUSES:
                update_fn.assert_called_once_with(pickup.id, status=status,
                                                  timestamp=payload['orderDetailedStatus'][0]['updatedTime'],
                                                  tracking_number=pickup.tracking_number)
            else:
                update_fn.assert_not_called()

    @patch('pickup.tasks.update_to_lazada_task.delay')
    def test_no_duplicate_update(self, update_fn):
        """Should not send update with the same status more than once"""
        # READY_TO_SHIP have been sent previously
        status = 'READY_TO_SHIP'
        self.pickup.status_history[status] = '2017-10-05T03:45:33Z'
        self.pickup.save()
        payload = {
            'orderId': '230948012',
            'partnerId': 786,
            'orderStatus': [
                {
                    'orderStatus': 'NEW',
                    'updatedTime': '2017-10-05T04:45:33Z',
                    'orderStatusDetail': None
                }
            ],
            'shipPackage': [{'trackingId': self.pickup.tracking_number}],
            'orderDetailedStatus': [
                {
                    'updatedTime': '2017-10-05T04:45:33Z',
                    'orderUpdatedTime': '2017-10-05T04:45:32Z',
                    'orderDetailedStatus': status
                }
            ]
        }
        ret = check_webhook(payload)
        self.pickup.refresh_from_db()
        self.assertEqual(ret, self.pickup.id)
        self.assertEqual(payload['orderDetailedStatus'][0]['updatedTime'], self.pickup.status_history[status])
        update_fn.assert_not_called()

    @patch('pickup.tasks.PickUp.objects.select_for_update')
    @patch('pickup.tasks.check_webhook.retry')
    def test_db_error(self, retry_fn, select_fn):
        """Database error should retry"""
        select_fn.side_effect = DatabaseError()
        retry_fn.side_effect = Retry()
        payload = {
            'orderId': '230948012',
            'partnerId': 786,
            'orderStatus': [
                {
                    'orderStatus': 'NEW',
                    'updatedTime': '2017-10-05T04:45:33Z',
                    'orderStatusDetail': None
                }
            ],
            'shipPackage': [{'trackingId': self.pickup.tracking_number}],
            'orderDetailedStatus': [
                {
                    'updatedTime': '2017-10-05T04:45:33Z',
                    'orderUpdatedTime': '2017-10-05T04:45:32Z',
                    'orderDetailedStatus': 'NEW'
                }
            ]
        }
        with self.assertRaises(Retry):
            check_webhook.delay(payload)
        self.assertEqual(1, retry_fn.call_count)
