'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''


from __future__ import unicode_literals

import unittest
import mock
import sys
import os
import json
import webuntis
import logging
from copy import deepcopy

try:
    from StringIO import StringIO  # Python 2
except ImportError:
    from io import BytesIO as StringIO  # Python 3

tests_path = os.path.abspath(os.path.dirname(__file__))
data_path = tests_path + '/static'


def get_json_resource(name):
        with open(os.path.join(data_path, name)) as f:
            return json.load(f)


class WebUntisTestCase(unittest.TestCase):
    def setUp(self):
        def cb(*args, **kwargs):  # pragma: no cover
            raise Exception('These are offline tests.')

        self.request_patcher = patcher = \
                mock.patch('webuntis.utils.remote._send_request', new=cb)
        patcher.start()

    def tearDown(self):
        try:
            self.request_patcher.stop()
        except RuntimeError:
            logging.warning(
                'Failed to tear the request_patcher down properly.')

    if sys.version_info < (3, 0, 0):
        def assertRaisesRegex(self, *a, **kw):
            return self.assertRaisesRegexp(*a, **kw)


stub_session_parameters = {
    'useragent': 'fooagent',
    'school': 'fooschool',
    'username': 'foouser',
    'password': 'hunter2',
    'server': 'fooboo_server',
    'jsessionid': 'FOOBOO_SESSION'
}


class OfflineTestCase(unittest.TestCase):
    def setUp(self):
        def cb(*args, **kwargs):  # pragma: no cover
            raise Exception('These are offline tests.')

        self.request_patcher = patcher = \
                mock.patch('webuntis.utils.remote._send_request', new=cb)
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
    '''Mock API methods more easily.

    :type methods: dict
    :param methods: A dictionary containing one callable for each API method.

    :type swallow_not_found: bool
    :param swallow_not_found: Whether to return {'result': {}} on unmocked API
        methods.
    '''
    def new(url, jsondata, headers):
        method = jsondata['method']
        try:
            method_mock = methods[method]
        except KeyError:  # pragma: no cover
            if not swallow_not_found:
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

        return deepcopy(d)

    return mock.patch('webuntis.utils.remote._send_request', new=new)


def raw_vs_object(jsondata, result):
    '''zip json data and results, but grouped by id instead of order. Also runs
    some checks that hashes are unique.'''
    raw_lookup = dict((x['id'], x) for x in jsondata)
    known_hashes = set()

    for obj in result:
        assert hash(obj) not in known_hashes, obj.id
        known_hashes.add(hash(obj))

        yield (raw_lookup[obj.id], obj)

    assert len(known_hashes) == len(jsondata) == len(result), \
        (len(known_hashes), len(jsondata), len(result))
