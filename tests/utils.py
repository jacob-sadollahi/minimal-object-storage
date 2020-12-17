import json
import string
import random
import urllib.request as req
from urllib.error import HTTPError, URLError


def send_request(url, method, body=None, headers=None):
    if body is None:
        body = {}
    req_client = req.Request(url)
    req_client.add_header('Content-Type', 'application/json; charset=utf-8')
    # additional headers
    try:
        if headers:
            for header_key, header_value in headers.items():
                req_client.add_header(header_key, header_value)
        if method == "post":
            json_data = json.dumps(body)
            json_data_as_bytes = json_data.encode('utf-8')  # needs to be bytes
            req_client.add_header('Content-Length', str(len(json_data_as_bytes)))
            response = req.urlopen(req_client, json_data_as_bytes)
        elif method == "get":
            response = req.urlopen(req_client)
        else:
            raise ValueError('This method currently not supported.')
        try:
            result = json.loads(response.read())
        except json.decoder.JSONDecodeError:
            result = response.read().decode()
        code = response.getcode()
    except HTTPError as e:
        if e.code in [500, 400]:
            result = e.read().decode()
        else:
            result = json.loads(e.read())
        code = e.code
    except URLError:
        result = "Url is not correct"
        code = 404
    return result, code


class S3Response:
    res_409 = {"message": "BucketAlreadyExists", "error": 409}
    res_422 = {"message": "InvalidArgumentsInName", "error": 422}
    res_400 = {"message": "TooManyBuckets", "error": 400}
    res_200 = {"body": {"data": {"status": "200", "result": "created"}}}

