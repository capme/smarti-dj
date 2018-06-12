import unittest
from lazacom_auth.tests.test_api import AuthTestCase
from unittest.mock import patch, PropertyMock, ANY
from pickup.services import LazadaTPS, LazadaInvalidAuthException, \
    LazadaTrackingNotFound, LazadaServiceError, _parse_pickup_file, GetPickupCsv
from django.utils import timezone
import pendulum


class TestServices(AuthTestCase):
    def setUp(self):
        super().setUp()

    @patch('pickup.services.requests.post')
    @patch('pickup.services.cache')
    def test_token_ok(self, mock_cache, mock_post):
        """Successfully logged in"""
        mock_token = 'wakwawtoken'
        mock_cache.get.return_value = None
        mock_post.return_value.json.return_value = dict(token=mock_token)
        mock_post.return_value.status_code = 200
        username = 'myuser'
        password = 'sshmysecret'
        base_url = 'http://some.url'
        lzd = LazadaTPS(username=username, password=password, base_url=base_url)
        self.assertEqual(lzd.token, mock_token)

    @patch('pickup.services.requests.post')
    @patch('pickup.services.cache')
    def test_invalid_user(self, mock_cache, mock_post):
        """Invalid credential"""
        mock_token = 'wakwawtoken'
        mock_cache.get.return_value = None
        mock_post.return_value.json.return_value = dict(token=mock_token)
        mock_post.return_value.status_code = 401
        username = 'myuser'
        password = 'sshmysecret'
        base_url = 'http://some.url'
        lzd = LazadaTPS(username=username, password=password, base_url=base_url)
        with self.assertRaises(LazadaInvalidAuthException):
            lzd.token

    @patch('pickup.services.requests.post')
    @patch('pickup.services.cache')
    def test_invalid_json(self, mock_cache, mock_post):
        """Server returned 200 but doesn't contain token"""
        mock_cache.get.return_value = None
        mock_post.return_value.json.return_value = {}
        mock_post.return_value.status_code = 200
        username = 'myuser'
        password = 'sshmysecret'
        base_url = 'http://some.url'
        lzd = LazadaTPS(username=username, password=password, base_url=base_url)
        with self.assertRaises(LazadaServiceError):
            lzd.token

    @patch('pickup.services.requests.post')
    @patch('pickup.services.LazadaTPS.token', new_callable=PropertyMock, return_value='WAKWAWTOKEN')
    def test_update_status_ok(self, mock_token, mock_post):
        """Test connector to update status success"""
        mock_post.return_value.status_code = 202
        payload = {
            "package_uuid":"cccddcd0-1123-499b-8e9e-f78b80f5def31",
            "tracking_id" : "59101195427073",
            "status":"READY_TO_SHIP",
            "timestamp": pendulum.parse('2017-10-19T08:28:08.261807+00:00'),
            "comments":"Ready to ship"
        }
        lzd = LazadaTPS(username='someuser', password='somesecret', base_url='http://some.url')
        self.assertTrue(lzd.update_status(**payload))
        expected_json = {**payload}
        expected_json['status'] = lzd.acom_to_lzd_status(payload['status'])
        expected_json['timestamp'] = '2017-10-19 15:28:08'
        mock_post.assert_called_once_with(ANY, headers=ANY, json=expected_json)

    @patch('pickup.services.requests.post')
    @patch('pickup.services.LazadaTPS.token', new_callable=PropertyMock, return_value='WAKWAWTOKEN')
    def test_update_status_invalid_token(self, mock_token, mock_post):
        """Test connector to update status fail"""
        mock_post.return_value.status_code = 401
        payload = {
            "package_uuid": "cccddcd0-1123-499b-8e9e-f78b80f5def31",
            "tracking_id": "59101195427073",
            "status": "READY_TO_SHIP",
            "timestamp": timezone.now(),
            "comments": "Ready to ship"
        }
        lzd = LazadaTPS(username='someuser', password='somesecret', base_url='http://some.url')
        with self.assertRaises(LazadaInvalidAuthException):
            lzd.update_status(**payload)

    @patch('pickup.services.requests.post')
    @patch('pickup.services.LazadaTPS.token', new_callable=PropertyMock, return_value='WAKWAWTOKEN')
    def test_update_status_invalid_tracking(self, mock_token, mock_post):
        """Test connector to update status fail"""
        mock_post.return_value.status_code = 422
        payload = {
            "package_uuid": "cccddcd0-1123-499b-8e9e-f78b80f5def31",
            "tracking_id": "59101195427073",
            "status": "READY_TO_SHIP",
            "timestamp": timezone.now(),
            "comments": "Ready to ship"
        }
        lzd = LazadaTPS(username='someuser', password='somesecret', base_url='http://some.url')
        with self.assertRaises(LazadaTrackingNotFound):
            lzd.update_status(**payload)

    @patch('pickup.services.requests.post')
    @patch('pickup.services.LazadaTPS.token', new_callable=PropertyMock, return_value='WAKWAWTOKEN')
    def test_update_status_unknown_err(self, mock_token, mock_post):
        """Test connector to update status fail"""
        mock_post.return_value.status_code = 500
        payload = {
            "package_uuid": "cccddcd0-1123-499b-8e9e-f78b80f5def31",
            "tracking_id": "59101195427073",
            "status": "READY_TO_SHIP",
            "timestamp": timezone.now(),
            "comments": "Ready to ship"
        }
        lzd = LazadaTPS(username='someuser', password='somesecret', base_url='http://some.url')
        with self.assertRaises(LazadaServiceError):
            lzd.update_status(**payload)


class ParsePickupFileTest(unittest.TestCase):
    def test_sc(self):
        str = '20171208_035513_1806.csv'
        dt = pendulum.parse('2017-12-08 03:55:13')
        parsed_date, count_lines = _parse_pickup_file(str)
        self.assertEqual(dt, parsed_date)
        self.assertEqual(1806, count_lines)

    def test_uc(self):
        str = '20171208_035513_1807.CSV'
        dt = pendulum.parse('2017-12-08 03:55:13')
        parsed_date, count_lines = _parse_pickup_file(str)
        self.assertEqual(dt, parsed_date)
        self.assertEqual(1807, count_lines)

    def test_fail(self):
        str = '20171208_035513_1806.txt'
        with self.assertRaises(TypeError):
            _, _ = _parse_pickup_file(str)


class GetPickupCsvTest(unittest.TestCase):
    @patch('pickup.services.pysftp.Connection')
    def test_pickup_files(self, sftp_conn):
        sftp = sftp_conn.return_value
        mock_files = [
            '20171208_035513_1806.csv',
            '20171209_030244_2155.csv'
        ]
        sftp.listdir.return_value = mock_files[:]

        result_files = []

        with GetPickupCsv() as pickup_csv:
            for f in pickup_csv:
                result_files.append(f.name)

        sftp.listdir.assert_called_once()
        self.assertListEqual(result_files, mock_files)

    @patch('pickup.services.pysftp.Connection')
    def test_pickup_csv(self, sftp_conn):
        sftp = sftp_conn.return_value
        sftp.listdir.return_value = [
            '20171209_030244_2155.csv'
        ]

        def sftp_get_sideffect(src, dest):
            with open(dest, 'wt') as f:
                f.write("""package_uuid,package_id,tracking_number,package_created_at
6d537502-97ac-4eaa-8e4d-a55e9cda2728,MPDS-3435643932-9147,SM884733601288436167,2017-12-06T21:49:23Z
9fae5fb7-e8fa-483d-af43-95c09cda40eb,MPDS-3795645932-3182,SM882302935415662487,2017-12-06T08:42:14Z""")

        sftp.get.side_effect = sftp_get_sideffect

        pickups = []

        with GetPickupCsv() as pickup_csv:
            for f in pickup_csv:
                for p in pickup_csv.get_pickups(f):
                    pickups.append(p)

        self.assertEqual(2, len(pickups))
        self.assertDictEqual(pickups[0], dict(package_uuid='6d537502-97ac-4eaa-8e4d-a55e9cda2728',
                                              package_id='MPDS-3435643932-9147',
                                              tracking_number='SM884733601288436167',
                                              package_created_at='2017-12-06T21:49:23Z'))
        self.assertDictEqual(pickups[1], dict(package_uuid='9fae5fb7-e8fa-483d-af43-95c09cda40eb',
                                              package_id='MPDS-3795645932-3182',
                                              tracking_number='SM882302935415662487',
                                              package_created_at='2017-12-06T08:42:14Z'))


