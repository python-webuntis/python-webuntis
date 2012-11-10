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


class TestCaseBase(unittest.TestCase):
    tests_path = os.path.abspath(os.path.dirname(__file__))
    data_path = tests_path + '/static'


class OfflineTestCase(TestCaseBase):
    def setUp(self):
        class methods(object):
            '''This eliminates any remote access.'''
            pass

        self.request_patcher = patcher = mock_results(methods)
        patcher.start()

        init_params = {
            'useragent': 'fooagent',
            'school': 'fooschool',
            'username': 'foouser',
            'password': 'hunter2',
            'server': 'fooboo_server',
            'jsessionid': 'CHUCK_TESTA'
        }

        self._session_init_params = init_params

        self.session = webuntis.Session(**init_params)

    def tearDown(self):
        self.request_patcher.stop()
        self.session = None

def mock_results(methods, use_original=False):
    orig = webuntis.session.JSONRPCRequest._send_request

    def callback(self, url, data, headers):
        jsondata = json.loads(data.decode('utf-8'))
        method = jsondata['method']

        data = getattr(methods, method)(self, url, jsondata, headers)
        d = {'id': jsondata['id']}
        d.update(data)
        return d

    return mock.patch(
        'webuntis.session.JSONRPCRequest._send_request',
        new=callback
    )

