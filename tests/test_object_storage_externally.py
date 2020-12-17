import utils
import secrets
import unittest
from unittest.mock import patch, MagicMock


class TestObjectStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.base_url = "http://localhost:5000"

    def register_me(self):
        url = f"{self.base_url}/middleware/api/v1/user/register"
        random_mail = secrets.token_urlsafe(16)
        random_password = secrets.token_urlsafe(16)
        data = {
            "email": f"{random_mail}@gmail.com",
            "password": f"{random_password}",
            "allowed_prefixes": ["aws", "arvan"]
        }
        utils.send_request(url, "post", data)
        return random_mail, random_password

    def authenticate(self):
        res, re_code = ({"token": "mockToken"}, 200)  # send_request(url, "post", data)
        return res.get('token')

    def test_register(self):
        url = f"{self.base_url}/middleware/api/v1/user/register"
        random_mail = secrets.token_urlsafe(16)
        random_password = secrets.token_urlsafe(16)
        data = {
            "email": f"{random_mail}@gmail.com",
            "password": f"{random_password}",
            "allowed_prefixes": ["aws", "arvan"]
        }
        res, re_code = utils.send_request(url, "post", data)
        self.assertEqual(re_code, 201)

    def test_try_duplicate_registration(self):
        url = f"{self.base_url}/middleware/api/v1/user/register"
        random_mail = secrets.token_urlsafe(16)
        random_password = secrets.token_urlsafe(16)
        data = {
            "email": f"{random_mail}@gmail.com",
            "password": f"{random_password}example09245",
            "allowed_prefixes": ["aws", "arvan"]
        }
        utils.send_request(url, "post", data)
        res, re_code = utils.send_request(url, "post", data)
        self.assertEqual(re_code, 400)
        self.assertIn("This email already exist", str(res))

    def test_auth(self):
        random_mail, random_password = self.register_me()
        url = f"{self.base_url}/middleware/api/v1/user/auth"
        data = {
            "email": f"{random_mail}@gmail.com",
            "password": f"{random_password}"
        }
        res, re_code = utils.send_request(url, "post", data)
        self.assertEqual(re_code, 200)
        self.assertEqual(list(res.keys())[0], "token")

    def test_wrong_email_password_auth(self):
        random_mail, random_password = self.register_me()
        url = f"{self.base_url}/middleware/api/v1/user/auth"
        data = {
            "email": random_mail + "xyz",
            "password": random_password
        }
        res, re_code = utils.send_request(url, "post", data)
        self.assertEqual(re_code, 400)
        self.assertIn("Email or password is not correct.", res)

    @patch('utils.send_request', MagicMock(return_value=(utils.S3Response.res_200, 200)))
    def test_create_bucket(self):
        token = self.authenticate()
        bucket_name = "example" + secrets.token_urlsafe(16).replace('-', '').replace('_', '').lower()
        url = f"{self.base_url}/resty-api/bucket/{bucket_name}"
        headers = {
            "Authorization": token
        }
        res, re_code = utils.send_request(url, "post", body=None, headers=headers)
        self.assertEqual(re_code, 200)
        self.assertEqual(res, {'body': {'data': {'status': '200', 'result': 'created'}}})

    @patch('utils.send_request', MagicMock(return_value=(utils.S3Response.res_409, 409)))
    def test_create_bucket_with_duplcated_name(self):
        token = self.authenticate()
        bucket_name = "example" + secrets.token_urlsafe(16).replace('-', '').replace('_', '').lower()
        url = f"{self.base_url}/resty-api/bucket/{bucket_name}"
        headers = {
            "Authorization": token
        }
        utils.send_request(url, "post", body=None, headers=headers)
        res, re_code = utils.send_request(url, "post", body=None, headers=headers)
        self.assertEqual(re_code, 409)
        self.assertEqual(res, {'message': 'BucketAlreadyExists', 'error': 409})

    @patch('utils.send_request', MagicMock(return_value=(utils.S3Response.res_422, 422)))
    def test_create_bucket_with_invalid_params(self):
        token = self.authenticate()
        bucket_name = "exampleAW.Quws" + secrets.token_urlsafe(16).replace('-', '').replace('_', '').lower()
        url = f"{self.base_url}/resty-api/bucket/{bucket_name}"
        headers = {
            "Authorization": token
        }
        res, re_code = utils.send_request(url, "post", body=None, headers=headers)
        self.assertEqual(re_code, 422)
        self.assertEqual(res, {'message': 'InvalidArgumentsInName', 'error': 422})

    @patch('utils.send_request', MagicMock(return_value=(utils.S3Response.res_400, 400)))
    def test_create_too_many_buckets(self):
        token = self.authenticate()
        bucket_name = "example" + secrets.token_urlsafe(16).replace('-', '').replace('_', '').lower()
        url = f"{self.base_url}/resty-api/bucket/{bucket_name}"
        headers = {
            "Authorization": token
        }
        res, re_code = utils.send_request(url, "post", body=None, headers=headers)
        self.assertEqual(re_code, 400)
        self.assertEqual(res, {'message': 'TooManyBuckets', 'error': 400})
