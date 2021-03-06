# Copyright 2015 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import mock
import requests


class TestConnection(unittest.TestCase):
    @staticmethod
    def _get_target_class():
        from google.cloud.bigquery._http import Connection

        return Connection

    def _make_one(self, *args, **kw):
        return self._get_target_class()(*args, **kw)

    def test_build_api_url_no_extra_query_params(self):
        conn = self._make_one(object())
        URI = "/".join([conn.API_BASE_URL, "bigquery", conn.API_VERSION, "foo"])
        self.assertEqual(conn.build_api_url("/foo"), URI)

    def test_build_api_url_w_extra_query_params(self):
        from six.moves.urllib.parse import parse_qsl
        from six.moves.urllib.parse import urlsplit

        conn = self._make_one(object())
        uri = conn.build_api_url("/foo", {"bar": "baz"})
        scheme, netloc, path, qs, _ = urlsplit(uri)
        self.assertEqual("%s://%s" % (scheme, netloc), conn.API_BASE_URL)
        self.assertEqual(path, "/".join(["", "bigquery", conn.API_VERSION, "foo"]))
        parms = dict(parse_qsl(qs))
        self.assertEqual(parms["bar"], "baz")

    def test_user_agent(self):
        from google.cloud import _http as base_http

        http = mock.create_autospec(requests.Session, instance=True)
        response = requests.Response()
        response.status_code = 200
        data = b"brent-spiner"
        response._content = data
        http.request.return_value = response
        client = mock.Mock(_http=http, spec=["_http"])

        conn = self._make_one(client)
        conn.USER_AGENT = "my-application/1.2.3"
        req_data = "req-data-boring"
        result = conn.api_request("GET", "/rainbow", data=req_data, expect_json=False)
        self.assertEqual(result, data)

        expected_headers = {
            "Accept-Encoding": "gzip",
            base_http.CLIENT_INFO_HEADER: conn.USER_AGENT,
            "User-Agent": conn.USER_AGENT,
        }
        expected_uri = conn.build_api_url("/rainbow")
        http.request.assert_called_once_with(
            data=req_data, headers=expected_headers, method="GET", url=expected_uri
        )
        self.assertIn("my-application/1.2.3", conn.USER_AGENT)

    def test_extra_headers(self):
        from google.cloud import _http as base_http

        http = mock.create_autospec(requests.Session, instance=True)
        response = requests.Response()
        response.status_code = 200
        data = b"brent-spiner"
        response._content = data
        http.request.return_value = response
        client = mock.Mock(_http=http, spec=["_http"])

        conn = self._make_one(client)
        conn._EXTRA_HEADERS["x-test-header"] = "a test value"
        req_data = "req-data-boring"
        result = conn.api_request("GET", "/rainbow", data=req_data, expect_json=False)
        self.assertEqual(result, data)

        expected_headers = {
            "Accept-Encoding": "gzip",
            base_http.CLIENT_INFO_HEADER: conn.USER_AGENT,
            "User-Agent": conn.USER_AGENT,
            "x-test-header": "a test value",
        }
        expected_uri = conn.build_api_url("/rainbow")
        http.request.assert_called_once_with(
            data=req_data, headers=expected_headers, method="GET", url=expected_uri
        )

    def test_extra_headers_replace(self):
        from google.cloud import _http as base_http

        http = mock.create_autospec(requests.Session, instance=True)
        response = requests.Response()
        response.status_code = 200
        data = b"brent-spiner"
        response._content = data
        http.request.return_value = response
        client = mock.Mock(_http=http, spec=["_http"])

        conn = self._make_one(client)
        conn._EXTRA_HEADERS = {"x-test-header": "a test value"}
        req_data = "req-data-boring"
        result = conn.api_request("GET", "/rainbow", data=req_data, expect_json=False)
        self.assertEqual(result, data)

        expected_headers = {
            "Accept-Encoding": "gzip",
            base_http.CLIENT_INFO_HEADER: conn.USER_AGENT,
            "User-Agent": conn.USER_AGENT,
            "x-test-header": "a test value",
        }
        expected_uri = conn.build_api_url("/rainbow")
        http.request.assert_called_once_with(
            data=req_data, headers=expected_headers, method="GET", url=expected_uri
        )
