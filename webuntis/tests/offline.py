'''
    This file is part of python-webuntis

    :copyright: (c) 2013 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
import mock
import webuntis
import datetime

from webuntis.tests._utils import OfflineTestCase, mock_results, \
    get_json_resource, stub_session_parameters, raw_vs_object, mock_urlopen

from nose.tools import eq_, assert_not_equal, assert_raises


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
                eq_(dep_raw['id'], dep.id)
                eq_(dep_raw['longName'], dep.long_name)
                eq_(dep_raw['name'], dep.name)

    def test_getholidays(self):
        jsonstr = get_json_resource('getholidays_mock.json')

        def getHolidays(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getHolidays': getHolidays}

        with mock_results(methods):
            for holiday_raw, holiday in raw_vs_object(
                    jsonstr, self.session.holidays()):
                eq_(holiday_raw['id'], holiday.id)
                eq_(holiday_raw['name'], holiday.short_name)
                eq_(holiday_raw['longName'], holiday.name)

                eq_(holiday_raw['startDate'],
                    int(holiday.start.strftime('%Y%m%d')))
                eq_(holiday_raw['endDate'],
                    int(holiday.end.strftime('%Y%m%d')))

    def test_getklassen(self):
        jsonstr = get_json_resource('getklassen_mock.json')
        schoolyear_id = 123

        def getKlassen(url, jsondata, headers):
            if len(methods['getKlassen'].calls) == 2:
                eq_(jsondata['params']['schoolyearId'], schoolyear_id)

            assert len(methods['getKlassen'].calls) <= 2
            return {'result': jsonstr}

        methods = {'getKlassen': getKlassen}

        with mock_results(methods):
            klassen = self.session.klassen()
            for klasse_raw, klasse in raw_vs_object(jsonstr, klassen):
                eq_(klasse_raw['id'], klasse.id)
                eq_(klasse_raw['name'], klasse.name)
                eq_(klasse_raw['longName'], klasse.long_name)

            eq_(klassen.filter(id=129)[0].id, 129)
            eq_([129, 130, 137], sorted(
                kl.id for kl in
                klassen.filter(id=set([129, 130, 137]))
                ))

            assert {'id': 129} in klassen
            assert {'name': '6A'} in klassen

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
            tt = self.session.timetable(klasse=114,
                                        start='20120301', end='20120301')

            for period_raw, period in raw_vs_object(jsonstr, tt):
                eq_(int(period.start.strftime('%H%M')),
                    period_raw['startTime'])
                eq_(int(period.start.strftime('%Y%m%d')),
                    period_raw['date'])
                eq_(int(period.end.strftime('%H%M')),
                    period_raw['endTime'])
                eq_(int(period.end.strftime('%H%M')),
                    period_raw['endTime'])

                if 'code' in period_raw:
                    eq_(period_raw['code'], period.code)
                else:
                    eq_(period.code, None)

                if 'lstype' in period_raw:
                    eq_(period_raw['lstype'], period.type)
                else:
                    eq_(period.type, 'ls')

                eq_(len(period_raw['kl']), len(period.klassen))
                for klasse_raw, klasse in raw_vs_object(
                        period_raw['kl'], period.klassen):
                    eq_(klasse.id, klasse_raw['id'])

                eq_(len(period_raw['te']), len(period.teachers))
                for teacher_raw, teacher in raw_vs_object(
                        period_raw['te'], period.teachers):
                    eq_(teacher.id, teacher_raw['id'])

                eq_(len(period_raw['su']), len(period.subjects))
                for subject_raw, subject in raw_vs_object(
                        period_raw['su'], period.subjects):
                    eq_(subject.id, subject_raw['id'])

                eq_(len(period_raw['ro']), len(period.rooms))
                for room_raw, room in raw_vs_object(
                        period_raw['ro'], period.rooms):
                    eq_(room.id, room_raw['id'])

            def validate_table(periods):
                counter = 0
                table = periods.to_table()
                for time, row in table:
                    for date, cell in row:
                        for hour in cell:
                            counter += 1

                eq_(counter, len(periods))

            validate_table(tt)
            eq_(len(webuntis.utils.timetable_utils.table([])), 0)

    def test_gettimetables_invalid_type_and_id(self):
        assert_raises(TypeError, self.session.timetable,
                      start=None, end=None, klasse=123, teacher=123)
        assert_raises(TypeError, self.session.timetable,
                      start=None, end=None)
        assert_raises(TypeError, self.session.timetable,
                      start=None, end=None, foo=123)

    def test_gettimetables_start_later_than_end(self):
        start = datetime.datetime.strptime('20130101', '%Y%m%d')
        end = datetime.datetime.strptime('20120101', '%Y%m%d')

        assert_raises(ValueError, self.session.timetable,
                      start=start, end=end, klasse=123)

    def test_gettimetables_start_and_end_are_none(self):
        assert_raises(TypeError, self.session.timetable,
                      start=None, end=None, klasse=123)

    def test_getrooms(self):
        jsonstr = get_json_resource('getrooms_mock.json')

        def getRooms(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getRooms': getRooms}

        with mock_results(methods):
            for room_raw, room in raw_vs_object(jsonstr, self.session.rooms()):
                eq_(room_raw['longName'], room.long_name)
                eq_(room_raw['name'], room.name)
                eq_(room_raw['id'], room.id)

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

            eq_(current_json['id'], schoolyears.current.id)
            assert schoolyears.current.is_current
            current_count = 0
            for year_raw, year in raw_vs_object(jsonstr, schoolyears):
                eq_(year_raw['id'], year.id)
                eq_(year_raw['name'], year.name)

                eq_(
                    year_raw['startDate'],
                    int(year.start.strftime('%Y%m%d'))
                )
                eq_(
                    year_raw['endDate'],
                    int(year.end.strftime('%Y%m%d'))
                )
                if year.is_current:
                    eq_(year, schoolyears.current)
                    current_count += 1
                    eq_(current_count, 1)

    def test_getsubjects(self):
        jsonstr = get_json_resource('getsubjects_mock.json')

        def getSubjects(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getSubjects': getSubjects}

        with mock_results(methods):
            for subj_raw, subj in raw_vs_object(
                    jsonstr, self.session.subjects()):
                eq_(subj_raw['id'], subj.id)
                eq_(subj_raw['name'], subj.name)
                eq_(subj_raw['longName'], subj.long_name)

    def test_getteachers(self):
        jsonstr = get_json_resource('getteachers_mock.json')

        def getTeachers(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getTeachers': getTeachers}

        with mock_results(methods):
            for t_raw, t in raw_vs_object(jsonstr, self.session.teachers()):
                eq_(t_raw['longName'], t.long_name)
                eq_(t_raw['longName'], t.surname)
                eq_(t_raw['foreName'], t.fore_name)
                eq_(t_raw['name'], t.name)

    def test_gettimegrid(self):
        jsonstr = get_json_resource('gettimegrid_mock.json')

        def getTimegridUnits(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getTimegridUnits': getTimegridUnits}

        with mock_results(methods):
            for t_raw, t in zip(jsonstr, self.session.timegrid()):
                assert t_raw['day'] == t.day == t.id
                for t2_raw, t2 in zip(t_raw['timeUnits'], t.times):
                    eq_(t2_raw['startTime'], int(t2[0].strftime('%H%M')))
                    eq_(t2_raw['endTime'], int(t2[1].strftime('%H%M')))

    def test_getstatusdata(self):
        jsonstr = get_json_resource('getstatusdata_mock.json')

        def getStatusData(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getStatusData': getStatusData}

        def validate_statusdata(raw, processed):
            name = list(raw.items())[0][0]
            colors = raw[name]
            eq_(name, processed.name)
            eq_(colors['foreColor'], processed.forecolor)
            eq_(colors['backColor'], processed.backcolor)
            assert type(processed.id) is int

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
                assert_raises(
                    webuntis.errors.NotLoggedInError, self.session._request,
                    'getCurrentSchoolyear')

        eq_(calls, expected_calls)

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
                assert_raises(
                    webuntis.errors.NotLoggedInError, self.session._request,
                    'getCurrentSchoolyear')

        eq_(calls, expected_calls)

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

        assert_raises(webuntis.errors.NotLoggedInError, s.logout)
        s.logout(suppress_errors=True)  # should not raise

        with mock.patch(
            'webuntis.Session._request'
        ):
            assert_raises(webuntis.errors.NotLoggedInError, s.logout)
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
            assert_raises(webuntis.errors.AuthError, s.login)

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
            eq_(s.config['jsessionid'], '123456')
            eq_(request_mock.call_count, 1)
            assert_call(request_mock)

            del s.config['jsessionid']

            assert_raises(webuntis.errors.AuthError, s.login)
            assert 'jsessionid' not in s.config
            eq_(request_mock.call_count, 2)
            assert_call(request_mock)

    def test_custom_cachelen(self):
        cachelen = 13
        params = stub_session_parameters.copy()
        params['cachelen'] = cachelen
        s = webuntis.Session(**params)
        eq_(s.cache._maxlen, cachelen)
        assert 'cachelen' not in s.config


class InternalTests(OfflineTestCase):
    '''Test certain internal interfaces, such as utils'''

    def test_config_invalidattribute(self):
        assert 'nigglywiggly' not in self.session.config
        assert_raises(
            KeyError,
            self.session.config.__getitem__,
            'nigglywiggly'
        )

    def test_datetime_utils(self):
        obj = webuntis.utils.datetime_utils.parse_datetime(20121005, 0)
        eq_(obj.year, 2012)
        eq_(obj.month, 10)
        eq_(obj.day, 5)
        eq_(obj.hour, 0)
        eq_(obj.minute, 0)
        eq_(obj.second, 0)

    def test_filterdict_basic(self):
        store = webuntis.utils.FilterDict({
            'whatever': lambda x: x,
            'always_whoop': lambda x: 'whoop'
        })
        store['whatever'] = 'lel'
        eq_(store['whatever'], 'lel')

        store['always_whoop'] = 'what'
        eq_(store['always_whoop'], 'whoop')

    def test_filterdict_deletion_successful(self):
        store = webuntis.utils.FilterDict({
            'whatever': lambda x: x
        })

        store['whatever'] = 'HUE'

        del store['whatever']
        assert 'whatever' not in store
        assert_raises(KeyError, store.__getitem__, 'whatever')

    def test_filterdict_assigning_none_deletes(self):
        store = webuntis.utils.FilterDict({
            'whatever': lambda x: x
        })

        store['whatever'] = 'HUE'
        assert 'whatever' in store
        store['whatever'] = None
        assert 'whatever' not in store
        assert_raises(KeyError, store.__getitem__, 'whatever')

    def test_filterdict_getting_none_from_filter_deletes(self):
        return_val = True
        store = webuntis.utils.FilterDict({
            'whatever': lambda x: return_val
        })

        store['whatever'] = 'HUE'
        eq_(store['whatever'], True)
        assert 'whatever' in store

        return_val = None
        store['whatever'] = 'HUE'
        assert 'whatever' not in store
        assert_raises(KeyError, store.__getitem__, 'whatever')

    def test_session_invalidattribute(self):
        assert_raises(AttributeError, getattr, self.session, 'foobar')
        assert not hasattr(self.session, 'foobar')

    def test_requestcaching_no_io_on_second_time(self):
        jsonstr = get_json_resource('getklassen_mock.json')

        def getKlassen(url, jsondata, headers):
            return {'result': jsonstr}

        methods = {'getKlassen': getKlassen}

        with mock_results(methods):
            self.session.klassen(from_cache=True)

        self.session.klassen(from_cache=True)

        eq_(len(getKlassen.calls), 1)

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

        eq_(len(getKlassen.calls), 2)

        with mock_results(failing_methods):
            assert_raises(ThisVeryCustomException, self.session.klassen)

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

        eq_(len(getKlassen.calls), 1)
        eq_(len(self.session.cache), 1)

    def test_listitem(self):
        session = self.session
        parent = None
        data = {'id': 42}
        item = webuntis.objects.ListItem(session=session, parent=parent,
                                         data=data)

        eq_(item._session, session)
        eq_(item._parent, parent)
        eq_(item._data, data)
        eq_(item.id, data['id'])
        eq_(int(item), item.id)

    def test_userinput_server(self):
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
            eq_(
                webuntis.utils.userinput.server(parser_input),
                expected_output
            )

        assert_raises(ValueError, webuntis.utils.userinput.server, '!"$%')
        assert_raises(ValueError, webuntis.utils.userinput.server, '')

    def test_userinput_string(self):
        s = webuntis.utils.userinput.string
        try:
            string = unicode
        except NameError:  # pragma: no cover
            string = str

        assert type(s('foo')) is string

    def test_resultclass_invalid_arguments(self):
        assert_raises(TypeError, webuntis.objects.Result, session=self.session,
                      kwargs={}, data="LELELE")
        assert_raises(TypeError, webuntis.objects.Result)
        assert_raises(TypeError, webuntis.objects.Result, session=self.session)

    def test_jsonrpcrequest_parse_result_invalid_request_id_returned(self):
        method = 'getThingsNotExisting'
        params = {'are': 'you', 'seri': 'ous'}

        assert_raises(
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
            assert_raises(
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
            eq_(
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
            assert_raises(
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
            assert_raises(
                TypeError,
                webuntis.utils.remote._send_request,
                url,
                object(),
                headers
            )

    def test_resultobject_invalid_params(self):
        valid_result = webuntis.objects.Result(data={}, parent=None,
                                               session=self.session)
        assert_raises(TypeError, webuntis.objects.Result, data={},
                      parent='WAT')
        assert_raises(TypeError, webuntis.objects.Result, data={},
                      parent=valid_result, session=self.session)

    def test_datetime_utils_date(self):
        dateint = 20121212
        datestr = str(dateint)
        dateobj = datetime.datetime.strptime(datestr, '%Y%m%d')
        eq_(webuntis.utils.datetime_utils.parse_date(dateint), dateobj)
        eq_(webuntis.utils.datetime_utils.parse_date(datestr), dateobj)
        eq_(webuntis.utils.datetime_utils.format_date(dateobj), dateint)

    def test_datetime_utils_time(self):
        timeint = 1337
        timestr = str(timeint)
        timeobj = datetime.datetime.strptime(timestr, '%H%M')

        eq_(webuntis.utils.datetime_utils.parse_time(timeint), timeobj)
        eq_(webuntis.utils.datetime_utils.parse_time(timestr), timeobj)
        eq_(webuntis.utils.datetime_utils.format_time(timeobj), timeint)

    def test_lrudict(self):
        d = webuntis.utils.LruDict(maxlen=3)
        d['foo'] = 2
        d['bar'] = 3
        d['baz'] = 4
        d['blah'] = 5
        eq_(len(d), 3)
        assert 'foo' not in d
        assert 'bar' in d
        assert 'baz' in d
        assert 'blah' in d

    def test_sessioncache_clear_by_method(self):
        d = webuntis.utils.SessionCache(maxlen=5)

        d[webuntis.utils.cache_key('timetable', {})] = 'POOP'
        d[webuntis.utils.cache_key('timetable', {'A': 'B'})] = 'POOP2'
        d[webuntis.utils.cache_key('klassen', {})] = 'POOP3'

        d.clear('timetable')
        eq_(len(d), 1)
        assert webuntis.utils.cache_key('klassen', {}) in d
        eq_(d[webuntis.utils.cache_key('klassen', {})], 'POOP3')

        d.clear()
        eq_(len(d), 0)

        # is that even used?
        eq_(type(self.session.cache), webuntis.utils.SessionCache)

    def test_lazyproperty_from_instance(self):
        meth_calls = []

        class FooBoo(object):
            @webuntis.utils.lazyproperty
            def some_method(self):
                meth_calls.append(True)
                return 42

        boo = FooBoo()
        eq_(boo.some_method, 42)
        assert boo.some_method is 42
        eq_(len(meth_calls), 1)

    def test_sessioncachekey_is_unique(self):
        Key = webuntis.utils.cache_key

        a = Key('klassen', {})
        a1 = Key('klassen', {})
        b = Key('klassen', {'g': 'G'})
        c = Key('teachers', {})

        eq_(a, a1)
        eq_(hash(a), hash(a1))

        assert_not_equal(a, b)
        assert_not_equal(hash(a), hash(b))

        assert_not_equal(a, c)
        assert_not_equal(hash(a), hash(c))

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

        assert_not_equal(today, today2)

        def getTimetable(url, jsondata, headers):
            return {'result': jsonstr}

        with mock_results({'getTimetable': getTimetable}):
            self.session.timetable(start=today, end=today, klasse=123,
                                   from_cache=True)
            eq_(len(getTimetable.calls), 1)
            self.session.timetable(start=today2, end=today2, klasse=123,
                                   from_cache=True)
            eq_(len(getTimetable.calls), 1)
