'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''


from __future__ import unicode_literals

import unittest
import mock
import os
import webuntis

class TestCaseBase(unittest.TestCase):
    tests_path = os.path.abspath(os.path.dirname(__file__))
    data_path = tests_path + '/static'


class OfflineTestCase(TestCaseBase):
    def setUp(self):
        self.request_patcher = patcher = mock.patch(
            'webuntis.Session._make_request',
            side_effect=Exception('This is an OFFLINE testsuite!')
        )
        patcher.start()

        self.session = webuntis.Session(useragent='foobar')

    def tearDown(self):
        self.request_patcher.stop()
        self.session = None
