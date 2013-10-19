import webuntis
import mock
from webuntis.utils.third_party import json
from webuntis.tests import WebUntisTestCase, BytesIO

class BasicUsage(WebUntisTestCase):
    def test_parse_result(self):
        x = webuntis.utils.remote._parse_result

        a = {'id': 2}
        b = {'id': 3}
        self.assertRaisesRegex(webuntis.errors.RemoteError,
                               'Request ID', x, a, b)

        a = b = {'id': 2}
        self.assertRaisesRegex(webuntis.errors.RemoteError,
                               'no information', x, a, b)

        a = {'id': 2}
        b = {'id': 2, 'result': 'YESSIR'}
        assert x(a, b) == 'YESSIR'

    def test_parse_error_code(self):
        x = webuntis.utils.remote._parse_error_code

        a = b = {}
        self.assertRaisesRegex(webuntis.errors.RemoteError,
                               'no information', x, a, b)

        b = {'error': {'code': 0, 'message': 'hello world'}}
        self.assertRaisesRegex(webuntis.errors.RemoteError,
                               'hello world', x, a, b)

        for code, exc in webuntis.utils.remote._errorcodes.items():
            self.assertRaises(exc, x, a, {
                'error': {'code': code, 'message': 'hello'}
            })
