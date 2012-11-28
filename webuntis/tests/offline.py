'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals

import mock
import webuntis
import webuntis.utils as utils
import datetime
try:
    from StringIO import StringIO  # Python 2
except ImportError:
    from io import BytesIO as StringIO  # Python 3

from webuntis.tests.utils import OfflineTestCase, mock_results, \
    get_json_resource, stub_session_parameters

class DataFetchingTests(OfflineTestCase):
    '''Test all Result objects from a high level.'''

    def test_getdepartments(self):
        jsonstr = get_json_resource('getdepartments_mock.json')

        class methods(object):
            @staticmethod
            def getDepartments(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for dep_raw, dep in zip(jsonstr, self.session.departments()):
                self.assertEqual(dep_raw['id'], dep.id)
                self.assertEqual(dep_raw['longName'], dep.long_name)
                self.assertEqual(dep_raw['name'], dep.name)

    def test_getholidays(self):
        jsonstr = get_json_resource('getholidays_mock.json')

        class methods(object):
            @staticmethod
            def getHolidays(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for holiday_raw, holiday in zip(jsonstr, self.session.holidays()):
                self.assertEqual(holiday_raw['id'], holiday.id)
                self.assertEqual(holiday_raw['name'], holiday.short_name)
                self.assertEqual(holiday_raw['longName'], holiday.name)

                self.assertEqual(
                    holiday_raw['startDate'],
                    int(holiday.start.strftime('%Y%m%d'))
                )
                self.assertEqual(
                    holiday_raw['endDate'],
                    int(holiday.end.strftime('%Y%m%d'))
                )

    def test_getklassen(self):
        jsonstr = get_json_resource('getklassen_mock.json')
        schoolyear_id = 123

        class methods(object):
            @staticmethod
            def getKlassen(session, url, jsondata, headers):
                if len(methods.getKlassen.calls) == 2:
                    self.assertEqual(jsondata['params']['schoolyearId'], schoolyear_id)

                self.assertFalse(len(methods.getKlassen.calls) > 2)
                return {'result': jsonstr}

        with mock_results(methods):
            klassen = self.session.klassen()
            for klasse_raw, klasse in zip(jsonstr, klassen):
                self.assertEqual(klasse_raw['id'], klasse.id)
                self.assertEqual(klasse_raw['name'], klasse.name)
                self.assertEqual(klasse_raw['longName'], klasse.long_name)

            self.assertEqual(klassen.filter(id=129)[0].id, 129)
            self.assertEqual(
                [129, 130, 137],
                sorted(
                    kl.id for kl in
                    klassen.filter(id=set([129, 130, 137]))
                )
            )

            self.assertTrue({'id': 129} in klassen)
            self.assertTrue({'name': '6A'} in klassen)

            # calling a second time for validating the schoolyear
            self.session.klassen(schoolyear=schoolyear_id)

    def test_gettimetables(self):
        jsonstr = get_json_resource('gettimetables_mock.json')
        jsonstr_kl = get_json_resource('getklassen_mock.json')
        jsonstr_te = get_json_resource('getteachers_mock.json')
        jsonstr_su = get_json_resource('getsubjects_mock.json')
        jsonstr_ro = get_json_resource('getrooms_mock.json')

        class methods(object):
            @staticmethod
            def getTimetable(self, url, jsondata, headers):
                return {'result': jsonstr}

            @staticmethod
            def getKlassen(self, url, jsondata, headers):
                return {'result': jsonstr_kl}

            @staticmethod
            def getTeachers(self, url, jsondata, headers):
                return {'result': jsonstr_te}

            @staticmethod
            def getSubjects(self, url, jsondata, headers):
                return {'result': jsonstr_su}

            @staticmethod
            def getRooms(self, url, jsondata, headers):
                return {'result': jsonstr_ro}

        with mock_results(methods):
            tt = self.session.timetable(klasse=114)

            for period_raw, period in zip(jsonstr, tt):
                self.assertEqual(
                    int(period.start.strftime('%H%M')),
                    period_raw['startTime']
                )
                self.assertEqual(
                    int(period.start.strftime('%Y%m%d')),
                    period_raw['date']
                )

                self.assertEqual(
                    int(period.end.strftime('%H%M')),
                    period_raw['endTime']
                )
                self.assertEqual(
                    int(period.end.strftime('%H%M')),
                    period_raw['endTime']
                )
                if 'code' in period_raw:
                    self.assertEqual(period_raw['code'], period.code)
                else:
                    self.assertEqual(period.code, None)

                if 'type' in period_raw:
                    self.assertEqual(period_raw['lstype'], period.type)
                else:
                    self.assertEqual(period.type, 'ls')

                self.assertEqual(len(period_raw['kl']), len(period.klassen))
                for klasse_raw, klasse in zip(period_raw['kl'], period.klassen):
                    self.assertEqual(klasse.id, klasse_raw['id'])

                self.assertEqual(len(period_raw['te']), len(period.teachers))
                for teacher_raw, teacher in zip(period_raw['te'], period.teachers):
                    self.assertEqual(teacher.id, teacher_raw['id'])

                self.assertEqual(len(period_raw['su']), len(period.subjects))
                for subject_raw, subject in zip(period_raw['su'], period.subjects):
                    self.assertEqual(subject.id, subject_raw['id'])

                self.assertEqual(len(period_raw['ro']), len(period.rooms))
                for room_raw, room in zip(period_raw['ro'], period.rooms):
                    self.assertEqual(room.id, room_raw['id'])


            def validate_table(periods, width=None):
                counter = 0
                table = periods.to_table(width=width)
                for time, row in table:
                    if width is not None:
                        row = list(row)
                        self.assertEqual(len(row), width)
                    for weekday_number, cell in row:
                        for hour in cell:
                            counter += 1

                self.assertEqual(counter, len(periods))

            validate_table(tt)
            validate_table(tt, width=999)
            self.assertRaises(ValueError, validate_table, tt, width=0)

            self.assertEqual(len(webuntis.utils.timetable_utils.table([])), 0)

    def test_gettimetables_invalid_type_and_id(self):
        self.assertRaises(TypeError, self.session.timetable, start=None, end=None, klasse=123, teacher=123)
        self.assertRaises(TypeError, self.session.timetable, start=None, end=None)
        self.assertRaises(TypeError, self.session.timetable, start=None, end=None, foo=123)

    def test_gettimetables_start_xor_end(self):
        some_date = datetime.datetime.now()
        with mock_results(None, swallow_not_found=True):
            self.session.timetable(start=some_date, end=None, klasse=123)
            self.session.timetable(start=None, end=some_date, klasse=123)

    def test_getrooms(self):
        jsonstr = get_json_resource('getrooms_mock.json')

        class methods(object):
            @staticmethod
            def getRooms(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for room_raw, room in zip(jsonstr, self.session.rooms()):
                self.assertEqual(room_raw['longName'], room.long_name)
                self.assertEqual(room_raw['name'], room.name)
                self.assertEqual(room_raw['id'], room.id)

    def test_getschoolyears(self):
        jsonstr = get_json_resource('getschoolyears_mock.json')
        current_json = jsonstr[3]

        class methods(object):
            @staticmethod
            def getSchoolyears(self, url, jsondata, headers):
                return {'result': jsonstr}

            @staticmethod
            def getCurrentSchoolyear(self, url, jsondata, headers):
                return {'result': current_json}

        with mock_results(methods):
            schoolyears = self.session.schoolyears()

            self.assertEqual(current_json['id'], schoolyears.current.id)
            self.assertTrue(schoolyears.current.is_current)
            current_count = 0
            for year_raw, year in zip(jsonstr, schoolyears):
                self.assertEqual(year_raw['id'], year.id)
                self.assertEqual(year_raw['name'], year.name)

                self.assertEqual(
                    year_raw['startDate'],
                    int(year.start.strftime('%Y%m%d'))
                )
                self.assertEqual(
                    year_raw['endDate'],
                    int(year.end.strftime('%Y%m%d'))
                )
                if year.is_current:
                    self.assertEqual(year, schoolyears.current)
                    current_count += 1
                    self.assertEqual(current_count, 1)

    def test_getsubjects(self):
        jsonstr = get_json_resource('getsubjects_mock.json')

        class methods(object):
            @staticmethod
            def getSubjects(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for subj_raw, subj in zip(jsonstr, self.session.subjects()):
                self.assertEqual(subj_raw['id'], subj.id)
                self.assertEqual(subj_raw['name'], subj.name)
                self.assertEqual(subj_raw['longName'], subj.long_name)

    def test_getteachers(self):
        jsonstr = get_json_resource('getteachers_mock.json')

        class methods(object):
            @staticmethod
            def getTeachers(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for t_raw, t in zip(jsonstr, self.session.teachers()):
                self.assertEqual(t_raw['longName'], t.long_name)
                self.assertEqual(t_raw['longName'], t.surname)
                self.assertEqual(t_raw['foreName'], t.fore_name)
                self.assertEqual(t_raw['name'], t.name)

    def test_gettimegrid(self):
        jsonstr = get_json_resource('gettimegrid_mock.json')

        class methods(object):
            @staticmethod
            def getTimegridUnits(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for t_raw, t in zip(jsonstr, self.session.timegrid()):
                self.assertEqual(t_raw['day'], t.day)
                for t2_raw, t2 in zip(t_raw['timeUnits'], t.times):
                    self.assertEqual(t2_raw['startTime'],
                                     int(t2[0].strftime('%H%M')))
                    self.assertEqual(t2_raw['endTime'],
                                     int(t2[1].strftime('%H%M')))

    def test_getstatusdata(self):
        jsonstr = get_json_resource('getstatusdata_mock.json')

        class methods(object):
            @staticmethod
            def getStatusData(self, url, jsondata, headers):
                return {'result': jsonstr}

        def validate_statusdata(raw, processed):
            name = list(raw.items())[0][0]
            colors = raw[name]
            self.assertEqual(name, processed.name)
            self.assertEqual(colors['foreColor'], processed.forecolor)
            self.assertEqual(colors['backColor'], processed.backcolor)

        with mock_results(methods):
            statusdata = self.session.statusdata()
            for lstype_raw, lstype in zip(jsonstr['lstypes'],
                                          statusdata.lesson_types):
                validate_statusdata(lstype_raw, lstype)

            for code_raw, code in zip(jsonstr['codes'], statusdata.period_codes):
                validate_statusdata(code_raw, code)


class SessionUsageTests(OfflineTestCase):
    '''Test features of webuntis.Session.'''
    def test_login_repeat_invalid_session(self):
        retry_amount = 5
        calls = []

        # This produces a list of 5 * ['getCurrentSchoolyear'] with ['logout',
        # 'authenticate'] between each.
        expected_calls = (
            ['getCurrentSchoolyear', 'logout', 'authenticate']
            * (retry_amount + 1)
        )[:-2]

        class methods(object):
            @staticmethod
            def authenticate(self, url, jsondata, headers):
                calls.append(jsondata['method'])
                return {
                    'result': {'sessionId': 'Foobar_session_' + jsondata['id']}
                }

            @staticmethod
            def getCurrentSchoolyear(self, url, jsondata, headers):
                calls.append(jsondata['method'])
                return {
                    'error': {'code': -8520, 'message': 'Not Logged In!'}
                }

            @staticmethod
            def logout(self, url, jsondata, headers):
                calls.append(jsondata['method'])
                return {
                    'result': {'bla': 'blub'}
                }

        with mock_results(methods):
            with mock.patch.dict(
                self.session.options,
                {'login_repeat': retry_amount}
            ):
                self.assertRaises(webuntis.errors.NotLoggedInError,
                                  self.session._request, 'getCurrentSchoolyear')

        self.assertEqual(calls, expected_calls)

    def test_login_repeat_not_logged_in(self):
        retry_amount = 1
        calls = []

        # This produces a list of 5 * ['getCurrentSchoolyear'] with ['logout',
        # 'authenticate'] between each.
        expected_calls = ['authenticate', 'getCurrentSchoolyear']

        class methods(object):
            @staticmethod
            def authenticate(self, url, jsondata, headers):
                calls.append(jsondata['method'])
                return {
                    'id': jsondata['id'],
                    'result': {'sessionId': 'Foobar_session_' + jsondata['id']}
                }

            @staticmethod
            def _nope(self, url, jsondata, headers):
                calls.append(jsondata['method'])
                return {
                    'id': jsondata['id'],
                    'error': {'code': -8520, 'message': 'Not Logged In!'}
                }

            getCurrentSchoolyear = logout = _nope
            del _nope

        with mock_results(methods):
            with mock.patch.dict(
                self.session.options,
                {'login_repeat': retry_amount, 'jsessionid': None}
            ):
                self.assertRaises(webuntis.errors.NotLoggedInError,
                                  self.session._request, 'getCurrentSchoolyear')

        self.assertEqual(calls, expected_calls)

    def test_session_contextmanager(self):
        s = webuntis.Session(**stub_session_parameters)

        with mock.patch('webuntis.Session.logout') as logout:
            with mock.patch('webuntis.Session.login', return_value=s) as login:
                assert webuntis.Session.login is login
                assert webuntis.Session.logout is logout

                with s.login():
                    pass

                login.assert_called_once_with()
                logout.assert_called_once_with(suppress_errors=True)

    def test_logout_not_logged_in(self):
        session_parameters = stub_session_parameters.copy()
        del session_parameters['jsessionid']

        s = webuntis.Session(**session_parameters)

        self.assertRaises(webuntis.errors.NotLoggedInError, s.logout)
        s.logout(suppress_errors=True)  # should not raise

        with mock.patch(
            'webuntis.Session._request'
        ):
            self.assertRaises(webuntis.errors.NotLoggedInError, s.logout)
            s.logout(suppress_errors=True)  # should not raise

    def test_login_no_creds(self):
        session_parameters = stub_session_parameters.copy()
        del session_parameters['jsessionid']
        del session_parameters['username']
        del session_parameters['password']

        s = webuntis.Session(**session_parameters)

        with mock.patch(
            'webuntis.Session._request',
            side_effect=Exception('Testing if login method raises AuthError due to invalid creds...')
        ):
            self.assertRaises(webuntis.errors.AuthError, s.login)

    def test_login_response_with_sessionid_and_without(self):
        session_parameters = stub_session_parameters.copy()
        del session_parameters['jsessionid']

        s = webuntis.Session(**session_parameters)

        def assert_call(request_mock):
            request_mock.assert_called_with(
                'authenticate',
                {
                    'user': session_parameters['username'],
                    'password': session_parameters['password'],
                    'client': session_parameters['useragent']
                },
                use_login_repeat=False
            )

        with mock.patch(
            'webuntis.Session._request',
            side_effect=[{'sessionId': '123456'}, {}]
        ) as request_mock:
            s.login()
            self.assertEqual(s.options['jsessionid'], '123456')
            self.assertEqual(request_mock.call_count, 1)
            assert_call(request_mock)

            del s.options['jsessionid']

            self.assertRaises(webuntis.errors.AuthError, s.login)
            self.assertTrue('jsessionid' not in s.options)
            self.assertEqual(request_mock.call_count, 2)
            assert_call(request_mock)

    def test_custom_cachelen(self):
        cachelen = 13
        params = stub_session_parameters.copy()
        params['cachelen'] = cachelen
        s = webuntis.Session(**params)
        self.assertEqual(s.cache._maxlen, cachelen)
        self.assertTrue('cachelen' not in s.options)


class InternalTests(OfflineTestCase):
    '''Test certain internal interfaces, such as utils'''

    def test_make_cache_key(self):
        key = webuntis.utils.SessionCacheKey
        # The hash builtin will take care of us if the results aren't hashable.
        hash(key('getStuff', {'foo': 'bar'}))
        hash(key('getStuff', {}))
        hash(key('getStuff', None))

    def test_is_iterable_util(self):
        tests = [
            ((), True),
            (None, False),
            ([], True),
            ({}, True),
            ("FOO", False),
            (str("FOO"), False),
            (123, False)
        ]

        for given_input, expected_output in tests:
            self.assertEqual(utils.is_iterable(given_input), expected_output)

    def test_options_invalidattribute(self):
        self.assertFalse('nigglywiggly' in self.session.options)
        self.assertRaises(
            KeyError,
            self.session.options.__getitem__,
            'nigglywiggly'
        )

    def test_datetime_utils(self):
        obj = utils.datetime_utils.parse_datetime(20121005, 0)
        self.assertEqual(obj.year, 2012)
        self.assertEqual(obj.month, 10)
        self.assertEqual(obj.day, 5)
        self.assertEqual(obj.hour, 0)
        self.assertEqual(obj.minute, 0)
        self.assertEqual(obj.second, 0)

    def test_filterdict(self):
        store = utils.FilterDict({
            'whatever': lambda x: x,
            'always_whoop': lambda x: 'whoop'
        })
        store['whatever'] = 'lel'
        self.assertEqual(store['whatever'], 'lel')

        store['always_whoop'] = 'what'
        self.assertEqual(store['always_whoop'], 'whoop')

        del store['whatever']
        self.assertRaises(KeyError, store.__getitem__, 'whatever')

        del store['always_whoop']
        self.assertRaises(KeyError, store.__getitem__, 'always_whoop')

    def test_session_invalidattribute(self):
        self.assertRaises(AttributeError, getattr, self.session, 'foobar')
        self.assertFalse(hasattr(self.session, 'foobar'))

    def test_requestcaching(self):
        jsonstr = get_json_resource('getklassen_mock.json')

        def result_mock(s, method, params=None, use_login_repeat=None):
            self.assertEqual(method, 'getKlassen')
            return jsonstr

        with mock.patch(
            'webuntis.session.Session._request',
            new=result_mock
        ):
            self.session.klassen()

        with mock.patch(
            'webuntis.session.Session._request',
            side_effect=Exception('CHUCK TESTA')
        ):
            self.session.klassen()

    def test_listitem(self):
        session = self.session
        parent = None
        data = {'id': 42}
        item = webuntis.objects.ListItem(session=session, parent=parent, data=data)

        self.assertEqual(item._session, session)
        self.assertEqual(item._parent, parent)
        self.assertEqual(item._data, data)
        self.assertEqual(item.id, data['id'])
        self.assertEqual(int(item), item.id)

    def test_optionparsers_server(self):
        tests = [
            ('webuntis.grupet.at',
                'http://webuntis.grupet.at/WebUntis/jsonrpc.do'),
            ('https://webuntis.grupet.at',
                'https://webuntis.grupet.at/WebUntis/jsonrpc.do'),
            ('webuntis.grupet.at:8080',
                'http://webuntis.grupet.at:8080/WebUntis/jsonrpc.do'),
            ('webuntis.grupet.at/a/b/c', 'http://webuntis.grupet.at/a/b/c'),
            ('webuntis.grupet.at/', 'http://webuntis.grupet.at/'),
        ]

        for parser_input, expected_output in tests:
            self.assertEqual(
                webuntis.utils.option_utils.server(parser_input),
                expected_output
            )

        self.assertRaises(ValueError, webuntis.utils.option_utils.server, '!"$%')

    def test_resultclass_invalid_arguments(self):
        self.assertRaises(TypeError, webuntis.objects.Result, session=self.session, kwargs={}, data="LELELE")
        self.assertRaises(TypeError, webuntis.objects.Result)
        self.assertRaises(TypeError, webuntis.objects.Result, session=self.session)

    def test_jsonrpcrequest_parse_result_invalid_request_id_returned(self):
        method = 'getThingsNotExisting'
        params = {'are': 'you', 'seri': 'ous'}

        self.assertRaises(
            webuntis.errors.RemoteError,
            webuntis.session.JSONRPCRequest._parse_result,
            {
                'jsonrpc': '2.0',
                'method': method,
                'params': params,
                'id': '2012-03-14 13:37:12.345678'
            }, {
                'jsonrpc': '2.0',
                'id': 'COMPLETELYUNRELATED',
                'result': [1, 2, 3]
            }
        )

    def test_jsonrpcrequest_parse_error_code(self):
        method = 'getThingsNotExisting'
        params = {'are': 'you', 'seri': 'ous'}
        reqid = '2012-03-14 13:37:12.345678'

        def check():
            self.assertRaises(
                webuntis.errors.RemoteError,
                webuntis.session.JSONRPCRequest._parse_error_code,
                request_data, result_data
            )

        request_data = {
            'jsonrpc': '2.0',
            'id': reqid,
            'method': method,
            'params': params
        }

        result_data = {
            'jsonrpc': '2.0',
            'id': reqid,
            'error': {
                'code': 234567854323456789876543,
                'message': 'I am a teapot.'
            }
        }
        check()

        del result_data['error']
        check()

    def test_jsonrpcrequest_send_request(self):
        self.request_patcher.stop()

        def mock_urlopen(data, expected_url, expected_data, expected_headers):
            def mocking_func(requestobj):
                self.assertEqual(requestobj.get_full_url(), expected_url)
                self.assertEqual(requestobj.data, expected_data)
                self.assertEqual(dict(requestobj.header_items()), expected_headers)

                io = StringIO(data)
                return io
            return mocking_func

        url = 'http://example.com'
        decoded_data = {'le': 'LE'}
        data = b'{"le": "LE"}'
        headers = {'User-agent': 'Netscape'}

        with mock.patch(
            'webuntis.session.urlrequest.urlopen',
            new=mock_urlopen(data, expected_url=url, expected_data=data, expected_headers=headers)
        ):
            self.assertEqual(
                webuntis.session.JSONRPCRequest._send_request(
                    url,
                    data,
                    headers
                ),
                decoded_data
            )

        invalid_data = b'LELELE'

        with mock.patch(
            'webuntis.session.urlrequest.urlopen',
            new=mock_urlopen(invalid_data,
                             # actually not expected, since the method will crash
                             expected_url=url,
                             expected_data=invalid_data,
                             expected_headers=headers)
        ):
            self.assertRaises(
                webuntis.errors.RemoteError,
                webuntis.session.JSONRPCRequest._send_request,
                url,
                invalid_data,
                headers
            )

    def test_resultobject_invalid_params(self):
        valid_result = webuntis.objects.Result(data={}, parent=None, session=self.session)
        self.assertRaises(TypeError, webuntis.objects.Result, data={}, parent='WAT')
        self.assertRaises(TypeError, webuntis.objects.Result, data={}, parent=valid_result, session=self.session)

    def test_datetime_utils_date(self):
        dateint = 20121212
        datestr = str(dateint)
        dateobj = datetime.datetime.strptime(datestr, '%Y%m%d')
        self.assertEqual(webuntis.utils.datetime_utils.parse_date(dateint), dateobj)
        self.assertEqual(webuntis.utils.datetime_utils.parse_date(datestr), dateobj)
        self.assertEqual(webuntis.utils.datetime_utils.format_date(dateobj), dateint)

    def test_datetime_utils_time(self):
        timeint = 1337
        timestr = str(timeint)
        timeobj = datetime.datetime.strptime(timestr, '%H%M')

        self.assertEqual(webuntis.utils.datetime_utils.parse_time(timeint), timeobj)
        self.assertEqual(webuntis.utils.datetime_utils.parse_time(timestr), timeobj)
        self.assertEqual(webuntis.utils.datetime_utils.format_time(timeobj), timeint)

    def test_lrudict(self):
        d = webuntis.utils.LruDict(maxlen=3)
        d['foo'] = 2
        d['bar'] = 3
        d['baz'] = 4
        d['blah'] = 5
        self.assertEqual(len(d), 3)
        self.assertTrue('foo' not in d)
        self.assertTrue('bar' in d)
        self.assertTrue('baz' in d)
        self.assertTrue('blah' in d)

    def test_lazyproperty_from_instance(self):
        meth_calls = []
        class FooBoo(object):
            @webuntis.utils.lazyproperty
            def some_method(self):
                meth_calls.append(True)
                return 42


        boo = FooBoo()
        self.assertEqual(boo.some_method, 42)
        self.assertTrue(boo.some_method is 42)
        self.assertEqual(len(meth_calls), 1)

    def test_lazyproperty_from_instance(self):
        '''Test that the decorator only works on instances' methods.'''
        meth_calls = []
        class FooBoo(object):
            @webuntis.utils.lazyproperty
            def some_method(self):
                meth_calls.append(True)
                return 42


        self.assertNotEqual(FooBoo.some_method, 42)
        self.assertTrue(FooBoo.some_method is not 42)
        self.assertEqual(len(meth_calls), 0)

