'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals

import mock
import webuntis
import datetime

from webuntis.tests.utils import OfflineTestCase, mock_results, \
    get_json_resource, stub_session_parameters, raw_vs_object, mock_urlopen


class DataFetchingTests(OfflineTestCase):
    '''Test all Result objects from a high level.'''

    def test_getdepartments(self):
        jsonstr = get_json_resource('getdepartments_mock.json')

        def getDepartments(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getDepartments': getDepartments}

        with mock_results(methods):
            for dep_raw, dep in raw_vs_object(
                    jsonstr, self.session.departments()):
                self.assertEqual(dep_raw['id'], dep.id)
                self.assertEqual(dep_raw['longName'], dep.long_name)
                self.assertEqual(dep_raw['name'], dep.name)

    def test_getholidays(self):
        jsonstr = get_json_resource('getholidays_mock.json')

        def getHolidays(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getHolidays': getHolidays}

        with mock_results(methods):
            for holiday_raw, holiday in raw_vs_object(
                    jsonstr, self.session.holidays()):
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

        def getKlassen(url, jsondata, headers):
            if len(methods['getKlassen'].calls) == 2:
                self.assertEqual(jsondata['params']['schoolyearId'],
                                 schoolyear_id)

            self.assertFalse(len(methods['getKlassen'].calls) > 2)
            return {'result': jsonstr}

        methods = {'getKlassen': getKlassen}

        with mock_results(methods):
            klassen = self.session.klassen()
            for klasse_raw, klasse in raw_vs_object(jsonstr, klassen):
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

        def getTimetable(url, jsondata, headers):
            return {'result': jsonstr}

        def getKlassen(url, jsondata, headers):
            return {'result': jsonstr_kl}

        def getTeachers(url, jsondata, headers):
            return {'result': jsonstr_te}

        def getSubjects(url, jsondata, headers):
            return {'result': jsonstr_su}

        def getRooms(url, jsondata, headers):
            return {'result': jsonstr_ro}

        methods = {
            'getTimetable': getTimetable,
            'getKlassen': getKlassen,
            'getTeachers': getTeachers,
            'getSubjects': getSubjects,
            'getRooms': getRooms
        }

        with mock_results(methods):
            tt = self.session.timetable(klasse=114, start='20120301', end='20120301')

            for period_raw, period in raw_vs_object(jsonstr, tt):
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

                if 'lstype' in period_raw:
                    self.assertEqual(period_raw['lstype'], period.type)
                else:
                    self.assertEqual(period.type, 'ls')

                self.assertEqual(len(period_raw['kl']), len(period.klassen))
                for klasse_raw, klasse in raw_vs_object(
                        period_raw['kl'], period.klassen):
                    self.assertEqual(klasse.id, klasse_raw['id'])

                self.assertEqual(len(period_raw['te']), len(period.teachers))
                for teacher_raw, teacher in raw_vs_object(
                        period_raw['te'], period.teachers):
                    self.assertEqual(teacher.id, teacher_raw['id'])

                self.assertEqual(len(period_raw['su']), len(period.subjects))
                for subject_raw, subject in raw_vs_object(
                        period_raw['su'], period.subjects):
                    self.assertEqual(subject.id, subject_raw['id'])

                self.assertEqual(len(period_raw['ro']), len(period.rooms))
                for room_raw, room in raw_vs_object(
                        period_raw['ro'], period.rooms):
                    self.assertEqual(room.id, room_raw['id'])

            def validate_table(periods, width=None):
                counter = 0
                table = periods.to_table(width=width)
                for time, row in table:
                    if width is not None:
                        row = list(row)
                        self.assertEqual(len(row), width)
                    for date, cell in row:
                        for hour in cell:
                            counter += 1

                self.assertEqual(counter, len(periods))

            validate_table(tt)
            validate_table(tt, width=999)
            self.assertRaises(ValueError, validate_table, tt, width=0)

            self.assertEqual(len(webuntis.utils.timetable_utils.table([])), 0)

    def test_gettimetables_invalid_type_and_id(self):
        self.assertRaises(TypeError, self.session.timetable,
                          start=None, end=None, klasse=123, teacher=123)
        self.assertRaises(TypeError, self.session.timetable,
                          start=None, end=None)
        self.assertRaises(TypeError, self.session.timetable,
                          start=None, end=None, foo=123)

    def test_gettimetables_start_later_than_end(self):
        start = datetime.datetime.strptime('20130101', '%Y%m%d')
        end = datetime.datetime.strptime('20120101', '%Y%m%d')

        self.assertRaises(ValueError, self.session.timetable,
                          start=start, end=end, klasse=123)

    def test_gettimetables_start_and_end_are_none(self):
        self.assertRaises(TypeError, self.session.timetable,
                          start=None, end=None, klasse=123)

    def test_getrooms(self):
        jsonstr = get_json_resource('getrooms_mock.json')

        def getRooms(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getRooms': getRooms}

        with mock_results(methods):
            for room_raw, room in raw_vs_object(jsonstr, self.session.rooms()):
                self.assertEqual(room_raw['longName'], room.long_name)
                self.assertEqual(room_raw['name'], room.name)
                self.assertEqual(room_raw['id'], room.id)

    def test_getschoolyears(self):
        jsonstr = get_json_resource('getschoolyears_mock.json')
        current_json = jsonstr[3]

        def getSchoolyears(url, jsondata, headers):
            return {'result': jsonstr}

        def getCurrentSchoolyear(url, jsondata, headers):
            return {'result': current_json}

        methods = {
            'getSchoolyears': getSchoolyears,
            'getCurrentSchoolyear': getCurrentSchoolyear
        }

        with mock_results(methods):
            schoolyears = self.session.schoolyears()

            self.assertEqual(current_json['id'], schoolyears.current.id)
            self.assertTrue(schoolyears.current.is_current)
            current_count = 0
            for year_raw, year in raw_vs_object(jsonstr, schoolyears):
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

        def getSubjects(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getSubjects': getSubjects}

        with mock_results(methods):
            for subj_raw, subj in raw_vs_object(
                    jsonstr, self.session.subjects()):
                self.assertEqual(subj_raw['id'], subj.id)
                self.assertEqual(subj_raw['name'], subj.name)
                self.assertEqual(subj_raw['longName'], subj.long_name)

    def test_getteachers(self):
        jsonstr = get_json_resource('getteachers_mock.json')

        def getTeachers(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getTeachers': getTeachers}

        with mock_results(methods):
            for t_raw, t in raw_vs_object(jsonstr, self.session.teachers()):
                self.assertEqual(t_raw['longName'], t.long_name)
                self.assertEqual(t_raw['longName'], t.surname)
                self.assertEqual(t_raw['foreName'], t.fore_name)
                self.assertEqual(t_raw['name'], t.name)

    def test_gettimegrid(self):
        jsonstr = get_json_resource('gettimegrid_mock.json')

        def getTimegridUnits(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getTimegridUnits': getTimegridUnits}

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

        def getStatusData(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getStatusData': getStatusData}

        def validate_statusdata(raw, processed):
            name = list(raw.items())[0][0]
            colors = raw[name]
            self.assertEqual(name, processed.name)
            self.assertEqual(colors['foreColor'], processed.forecolor)
            self.assertEqual(colors['backColor'], processed.backcolor)

        with mock_results(methods):
            statusdata = self.session.statusdata()
            for lstype_raw, lstype in zip(
                    jsonstr['lstypes'], statusdata.lesson_types):
                validate_statusdata(lstype_raw, lstype)

            for code_raw, code in zip(
                    jsonstr['codes'], statusdata.period_codes):
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

        def authenticate(url, jsondata, headers):
            calls.append(jsondata['method'])
            return {
                'result': {'sessionId': 'Foobar_session_' + jsondata['id']}
            }

        def getCurrentSchoolyear(url, jsondata, headers):
            calls.append(jsondata['method'])
            return {
                'error': {'code': -8520, 'message': 'Not Logged In!'}
            }

        def logout(url, jsondata, headers):
            calls.append(jsondata['method'])
            return {
                'result': {'bla': 'blub'}
            }

        methods = {
            'authenticate': authenticate,
            'getCurrentSchoolyear': getCurrentSchoolyear,
            'logout': logout
        }

        with mock_results(methods):
            with mock.patch.dict(
                self.session.config,
                {'login_repeat': retry_amount}
            ):
                self.assertRaises(
                    webuntis.errors.NotLoggedInError, self.session._request,
                    'getCurrentSchoolyear')

        self.assertEqual(calls, expected_calls)

    def test_login_repeat_not_logged_in(self):
        retry_amount = 1
        calls = []

        # This produces a list of 5 * ['getCurrentSchoolyear'] with ['logout',
        # 'authenticate'] between each.
        expected_calls = ['authenticate', 'getCurrentSchoolyear']

        def authenticate(url, jsondata, headers):
            calls.append(jsondata['method'])
            return {
                'id': jsondata['id'],
                'result': {'sessionId': 'Foobar_session_' + jsondata['id']}
            }

        def _nope(url, jsondata, headers):
            calls.append(jsondata['method'])
            return {
                'id': jsondata['id'],
                'error': {'code': -8520, 'message': 'Not Logged In!'}
            }

        methods = {
            'authenticate': authenticate,
            'getCurrentSchoolyear': _nope,
            'logout': _nope
        }

        with mock_results(methods):
            with mock.patch.dict(
                self.session.config,
                {'login_repeat': retry_amount, 'jsessionid': None}
            ):
                self.assertRaises(
                    webuntis.errors.NotLoggedInError, self.session._request,
                    'getCurrentSchoolyear')

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
            side_effect=Exception('Testing if login method raises AuthError '
                                  'due to invalid creds...')
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
            self.assertEqual(s.config['jsessionid'], '123456')
            self.assertEqual(request_mock.call_count, 1)
            assert_call(request_mock)

            del s.config['jsessionid']

            self.assertRaises(webuntis.errors.AuthError, s.login)
            self.assertTrue('jsessionid' not in s.config)
            self.assertEqual(request_mock.call_count, 2)
            assert_call(request_mock)

    def test_custom_cachelen(self):
        cachelen = 13
        params = stub_session_parameters.copy()
        params['cachelen'] = cachelen
        s = webuntis.Session(**params)
        self.assertEqual(s.cache._maxlen, cachelen)
        self.assertTrue('cachelen' not in s.config)


class InternalTests(OfflineTestCase):
    '''Test certain internal interfaces, such as utils'''

    def test_config_invalidattribute(self):
        self.assertFalse('nigglywiggly' in self.session.config)
        self.assertRaises(
            KeyError,
            self.session.config.__getitem__,
            'nigglywiggly'
        )

    def test_datetime_utils(self):
        obj = webuntis.utils.datetime_utils.parse_datetime(20121005, 0)
        self.assertEqual(obj.year, 2012)
        self.assertEqual(obj.month, 10)
        self.assertEqual(obj.day, 5)
        self.assertEqual(obj.hour, 0)
        self.assertEqual(obj.minute, 0)
        self.assertEqual(obj.second, 0)

    def test_filterdict_basic(self):
        store = webuntis.utils.FilterDict({
            'whatever': lambda x: x,
            'always_whoop': lambda x: 'whoop'
        })
        store['whatever'] = 'lel'
        self.assertEqual(store['whatever'], 'lel')

        store['always_whoop'] = 'what'
        self.assertEqual(store['always_whoop'], 'whoop')

    def test_filterdict_deletion_successful(self):
        store = webuntis.utils.FilterDict({
            'whatever': lambda x: x
        })

        store['whatever'] = 'HUE'

        del store['whatever']
        self.assertTrue('whatever' not in store)
        self.assertRaises(KeyError, store.__getitem__, 'whatever')

    def test_filterdict_assigning_none_deletes(self):
        store = webuntis.utils.FilterDict({
            'whatever': lambda x: x
        })

        store['whatever'] = 'HUE'
        self.assertTrue('whatever' in store)
        store['whatever'] = None
        self.assertTrue('whatever' not in store)
        self.assertRaises(KeyError, store.__getitem__, 'whatever')

    def test_filterdict_getting_none_from_filter_deletes(self):
        return_val = True
        store = webuntis.utils.FilterDict({
            'whatever': lambda x: return_val
        })

        store['whatever'] = 'HUE'
        self.assertEqual(store['whatever'], True)
        self.assertTrue('whatever' in store)

        return_val = None
        store['whatever'] = 'HUE'
        self.assertTrue('whatever' not in store)
        self.assertRaises(KeyError, store.__getitem__, 'whatever')

    def test_session_invalidattribute(self):
        self.assertRaises(AttributeError, getattr, self.session, 'foobar')
        self.assertFalse(hasattr(self.session, 'foobar'))

    def test_requestcaching_no_io_on_second_time(self):
        jsonstr = get_json_resource('getklassen_mock.json')

        def getKlassen(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getKlassen': getKlassen}

        with mock_results(methods):
            self.session.klassen(from_cache=True)

        self.session.klassen(from_cache=True)

        self.assertEqual(len(getKlassen.calls), 1)

    def test_requestcaching_no_caching_without_being_told_so(self):
        jsonstr = get_json_resource('getklassen_mock.json')

        def getKlassen(url, jsondata, headers):
            return {'result': jsonstr}

        class ThisVeryCustomException(Exception):
            pass

        def blow_up(*args, **kwargs):
            raise ThisVeryCustomException

        methods = {'getKlassen': getKlassen}

        failing_methods = {'getKlassen': blow_up}

        with mock_results(methods):
            self.session.klassen()
            self.session.klassen()

        self.assertEqual(len(getKlassen.calls), 2)

        with mock_results(failing_methods):
            self.assertRaises(ThisVeryCustomException, self.session.klassen)

    def test_no_cache_argument_in_caching_key(self):
        '''Any result wrapper method takes a ``cache`` arg which activates the
        cache if True. This test ensures that this arg doesn't show up in the
        cache dict key at the end.'''

        jsonstr = get_json_resource('getklassen_mock.json')

        def getKlassen(url, jsondata, headers):
            return {'result': jsonstr}

        with mock_results({'getKlassen': getKlassen}):
            self.session.klassen(from_cache='LELE')  # should be True-ish
            self.session.klassen(from_cache='YESPLS')  # should be too

        self.assertEqual(len(getKlassen.calls), 1)
        self.assertEqual(len(self.session.cache), 1)

    def test_listitem(self):
        session = self.session
        parent = None
        data = {'id': 42}
        item = webuntis.objects.ListItem(session=session, parent=parent,
                                         data=data)

        self.assertEqual(item._session, session)
        self.assertEqual(item._parent, parent)
        self.assertEqual(item._data, data)
        self.assertEqual(item.id, data['id'])
        self.assertEqual(int(item), item.id)

    def test_configkeys_server(self):
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
                webuntis.utils.config.server(parser_input),
                expected_output
            )

        self.assertRaises(ValueError, webuntis.utils.config.server, '!"$%')

    def test_resultclass_invalid_arguments(self):
        self.assertRaises(TypeError, webuntis.objects.Result,
                          session=self.session, kwargs={}, data="LELELE")
        self.assertRaises(TypeError, webuntis.objects.Result)
        self.assertRaises(TypeError, webuntis.objects.Result,
                          session=self.session)

    def test_jsonrpcrequest_parse_result_invalid_request_id_returned(self):
        method = 'getThingsNotExisting'
        params = {'are': 'you', 'seri': 'ous'}

        self.assertRaises(
            webuntis.errors.RemoteError,
            webuntis.utils.remote._parse_result,
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
                webuntis.utils.remote._parse_error_code,
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

    def test_jsonrpcrequest_send_request_valid_request(self):
        self.request_patcher.stop()

        url = 'http://example.com'
        headers = {'User-agent': 'Netscape'}

        with mock_urlopen(b'{"ret": "VAL"}', expected_url=url,
                          expected_data=b'{"la": "LU"}',
                          expected_headers=headers):
            self.assertEqual(
                webuntis.utils.remote._send_request(
                    url,
                    {'la': 'LU'},
                    headers
                ),
                {'ret': 'VAL'}
            )

    def test_jsonrpcrequest_send_request_invalid_json_response(self):
        self.request_patcher.stop()

        url = 'http://example.com'
        headers = {'User-agent': 'Netscape'}

        with mock_urlopen(b'LOL DUDE', expected_url=url,
                          expected_data=b'{"la": "LU"}',
                          expected_headers=headers):
            self.assertRaises(
                webuntis.errors.RemoteError,
                webuntis.utils.remote._send_request,
                url,
                {'la': 'LU'},
                headers
            )

    def test_jsonrpcrequest_send_request_invalid_json_input(self):
        self.request_patcher.stop()

        url = 'http://example.com'
        headers = {'User-agent': 'Netscape'}

        with mock_urlopen(Exception('No.'), expected_url=url,
                          expected_data='Does not matter',
                          expected_headers=headers):
            self.assertRaises(
                TypeError,
                webuntis.utils.remote._send_request,
                url,
                object(),
                headers
            )

    def test_resultobject_invalid_params(self):
        valid_result = webuntis.objects.Result(data={}, parent=None,
                                               session=self.session)
        self.assertRaises(TypeError, webuntis.objects.Result, data={},
                          parent='WAT')
        self.assertRaises(TypeError, webuntis.objects.Result, data={},
                          parent=valid_result, session=self.session)

    def test_datetime_utils_date(self):
        dateint = 20121212
        datestr = str(dateint)
        dateobj = datetime.datetime.strptime(datestr, '%Y%m%d')
        self.assertEqual(webuntis.utils.datetime_utils.parse_date(dateint),
                         dateobj)
        self.assertEqual(webuntis.utils.datetime_utils.parse_date(datestr),
                         dateobj)
        self.assertEqual(webuntis.utils.datetime_utils.format_date(dateobj),
                         dateint)

    def test_datetime_utils_time(self):
        timeint = 1337
        timestr = str(timeint)
        timeobj = datetime.datetime.strptime(timestr, '%H%M')

        self.assertEqual(webuntis.utils.datetime_utils.parse_time(timeint),
                         timeobj)
        self.assertEqual(webuntis.utils.datetime_utils.parse_time(timestr),
                         timeobj)
        self.assertEqual(webuntis.utils.datetime_utils.format_time(timeobj),
                         timeint)

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

    def test_sessioncache_clear_by_method(self):
        d = webuntis.utils.SessionCache(maxlen=5)

        d[webuntis.utils.cache_key('timetable', {})] = 'POOP'
        d[webuntis.utils.cache_key('timetable', {'A': 'B'})] = 'POOP2'
        d[webuntis.utils.cache_key('klassen', {})] = 'POOP3'

        d.clear('timetable')
        self.assertEqual(len(d), 1)
        self.assertTrue(webuntis.utils.cache_key('klassen', {}) in d)
        self.assertEqual(d[webuntis.utils.cache_key('klassen', {})], 'POOP3')

        d.clear()
        self.assertEqual(len(d), 0)

        # is that even used?
        self.assertEqual(type(self.session.cache), webuntis.utils.SessionCache)

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

    def test_sessioncachekey_is_unique(self):
        Key = webuntis.utils.cache_key

        a = Key('klassen', {})
        a1 = Key('klassen', {})
        b = Key('klassen', {'g': 'G'})
        c = Key('teachers', {})

        self.assertEqual(a, a1)
        self.assertEqual(hash(a), hash(a1))

        self.assertNotEqual(a, b)
        self.assertNotEqual(hash(a), hash(b))

        self.assertNotEqual(a, c)
        self.assertNotEqual(hash(a), hash(c))

    def test_sessioncachekey_is_hashable(self):
        now = datetime.datetime.now()
        today = datetime.date.today()
        key = webuntis.utils.cache_key

        # The hash builtin will take care of us if the results aren't hashable.
        hash(key('getStuff', {'foo': 'bar'}))
        hash(key('getStuff', {}))
        hash(key('getStuff', None))
        hash(key('fooBar', {'start': now}))
        hash(key('fooBar', {'start': today}))

    def test_dont_cache_the_same_thing(self):
        jsonstr = get_json_resource('gettimetables_mock.json')
        today = datetime.datetime.now()
        today2 = datetime.datetime.now()

        self.assertNotEqual(today, today2)

        def getTimetable(url, jsondata, headers):
            return {'result': jsonstr}

        with mock_results({'getTimetable': getTimetable}):
            self.session.timetable(start=today, end=today, klasse=123,
                                   from_cache=True)
            self.assertEqual(len(getTimetable.calls), 1)
            self.session.timetable(start=today2, end=today2, klasse=123,
                                   from_cache=True)
            self.assertEqual(len(getTimetable.calls), 1)
