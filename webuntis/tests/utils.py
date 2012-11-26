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
    def callback(self, url, data, headers):
        jsondata = json.loads(data.decode('utf-8'))
        method = jsondata['method']
        try:
            method_mock = getattr(methods, method)
        except AttributeError:
            if not swallow_not_found:
                raise
            else:
                data = {'result': {}}
        else:
            if not hasattr(method_mock, 'calls'):
                method_mock.calls = []
            method_mock.calls.append((self, url, jsondata, headers))
            data = method_mock(self, url, jsondata, headers)

        d = {'id': jsondata['id']}
        d.update(data)

        
        return d

    return mock.patch(
        'webuntis.session.JSONRPCRequest._send_request',
        new=callback
    )
