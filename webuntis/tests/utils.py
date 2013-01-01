'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''


from __future__ import unicode_literals

import unittest
import mock
import os
import json
import webuntis
import logging

try:
    from StringIO import StringIO  # Python 2
except ImportError:
    from io import BytesIO as StringIO  # Python 3

tests_path = os.path.abspath(os.path.dirname(__file__))
data_path = tests_path + '/static'


def get_json_resource(name):
        with open(os.path.join(data_path, name)) as f:
            return json.load(f)


class TestCaseBase(unittest.TestCase):
    pass

stub_session_parameters = {
    'useragent': 'fooagent',
    'school': 'fooschool',
    'username': 'foouser',
    'password': 'hunter2',
    'server': 'fooboo_server',
    'jsessionid': 'FOOBOO_SESSION'
}


class OfflineTestCase(TestCaseBase):
    def setUp(self):
        class methods(object):
            '''This eliminates any remote access.'''
            pass

        self.request_patcher = patcher = mock_results(methods)
        patcher.start()

        self.session = webuntis.Session(**stub_session_parameters)

    def tearDown(self):
        try:
            self.request_patcher.stop()
        except RuntimeError:
            logging.warning(
                'Failed to tear the request_patcher down properly.')

        self.session = None


def mock_results(methods, swallow_not_found=False):
    def callback(url, jsondata, headers):
        method = jsondata['method']
        try:
            method_mock = methods[method]
        except KeyError:
            if not swallow_not_found:  # pragma: no cover
                raise
            else:
                data = {'result': {}}
        else:
            if not hasattr(method_mock, 'calls'):
                method_mock.calls = []
            method_mock.calls.append((url, jsondata, headers))
            data = method_mock(url, jsondata, headers)

        d = {'id': jsondata['id']}
        d.update(data)

        return d

    return mock.patch(
        'webuntis.utils.remote._send_request',
        new=callback
    )


def raw_vs_object(jsonstr, result):
    known_hashes = set()
    for raw, obj in zip(jsonstr, result):
        assert hash(obj) not in known_hashes
        known_hashes.add(hash(obj))
        yield (raw, obj)

    assert len(known_hashes) == len(jsonstr) == len(result), \
        (len(known_hashes), len(jsonstr), len(result))


def mock_urlopen(data, expected_url, expected_data, expected_headers):
    def mocking_func(requestobj):
        given_url = requestobj.get_full_url()
        given_data = requestobj.data
        given_headers = dict(requestobj.header_items())

        assert given_url == expected_url, given_url
        assert given_data == expected_data, given_data
        assert given_headers == expected_headers, given_headers

        if isinstance(data, Exception):
            raise data

        io = StringIO(data)
        return io

    return mock.patch(
        'webuntis.utils.third_party.urlrequest.urlopen',
        new=mocking_func
    )
