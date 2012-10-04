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
import json

from webuntis.tests.utils import OfflineTestCase


class BasicUsageTests(OfflineTestCase):
    '''Mocks the _get_data method of all result objects and tests the package
    against basic usage.'''
    def test_getdepartments_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/getdepartments_mock.json')
        )

        with mock.patch.object(
            webuntis.objects.DepartmentList,
            '_get_data',
            return_value=jsonstr
        ):
            for dep_raw, dep in zip(jsonstr, self.session.departments()):
                self.assertEqual(dep_raw['id'], dep.id)
                self.assertEqual(dep_raw['longName'], dep.long_name)
                self.assertEqual(dep_raw['name'], dep.name)

    def test_getholidays_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/getholidays_mock.json')
        )

        with mock.patch.object(
            webuntis.objects.HolidayList,
            '_get_data',
            return_value=jsonstr
        ):
            for holiday_raw, holiday in zip(jsonstr, self.session.holidays()):
                self.assertEqual(
                    holiday_raw['startDate'],
                    int(holiday.start.strftime('%Y%m%d'))
                )
                self.assertEqual(
                    holiday_raw['endDate'],
                    int(holiday.end.strftime('%Y%m%d'))
                )
                self.assertEqual(
                    holiday_raw['id'],
                    holiday.id
                )
                self.assertEqual(
                    holiday_raw['name'],
                    holiday.short_name
                )
                self.assertEqual(
                    holiday_raw['longName'],
                    holiday.name
                )

    def test_getklassen_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/getklassen_mock.json')
        )

        with mock.patch.object(
            webuntis.objects.KlassenList,
            '_get_data',
            return_value=jsonstr
        ):
            klassen = self.session.klassen()
            for klasse_raw, klasse in zip(jsonstr, klassen):
                self.assertEqual(klasse_raw['longName'], klasse.long_name)
                self.assertEqual(klasse_raw['name'], klasse.name)
                self.assertEqual(klasse_raw['id'], klasse.id)

            self.assertEqual(klassen.filter(id=129)[0].id, 129)
            self.assertEqual(
                [129, 130, 137],
                sorted(
                    kl.id for kl in
                    klassen.filter(id=(129, 130, 137))
                )
            )

    def test_gettimetables_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/gettimetables_mock.json')
        )
        with mock.patch.object(
            webuntis.objects.PeriodList,
            '_get_data',
            return_value=jsonstr
        ):
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

    def test_getrooms_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/getrooms_mock.json')
        )
        with mock.patch.object(
            webuntis.objects.RoomList,
            '_get_data',
            return_value=jsonstr
        ):
            for room_raw, room in zip(jsonstr, self.session.rooms()):
                self.assertEqual(room_raw['longName'], room.long_name)
                self.assertEqual(room_raw['name'], room.name)
                self.assertEqual(room_raw['id'], room.id)

    def test_getschoolyears_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/getschoolyears_mock.json')
        )
        current_json = jsonstr[3]

        with mock.patch.object(
            webuntis.objects.SchoolyearList,
            '_get_data',
            return_value=jsonstr
        ):
            schoolyears = self.session.schoolyears()

        with mock.patch.object(
            webuntis.session.Session,
            '_request',
            return_value=current_json
        ):
            self.assertEqual(current_json['id'], schoolyears.current.id)
            self.assertTrue(schoolyears.current.is_current)
            for year_raw, year in zip(jsonstr, schoolyears):
                self.assertEqual(
                    year_raw['startDate'],
                    int(year.start.strftime('%Y%m%d'))
                )
                self.assertEqual(
                    year_raw['endDate'],
                    int(year.end.strftime('%Y%m%d'))
                )
                self.assertEqual(year_raw['name'], year.name)
                self.assertEqual(year_raw['id'], year.id)
                if year.is_current:
                    self.assertEqual(year, schoolyears.current)

    def test_getsubjects_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/getsubjects_mock.json')
        )
        with mock.patch.object(
            webuntis.objects.SubjectList,
            '_get_data',
            return_value=jsonstr
        ):
            for subj_raw, subj in zip(jsonstr, self.session.subjects()):
                self.assertEqual(subj_raw['id'], subj.id)
                self.assertEqual(subj_raw['longName'], subj.long_name)
                self.assertEqual(subj_raw['name'], subj.name)

    def test_getteachers_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/getteachers_mock.json')
        )
        with mock.patch.object(
            webuntis.objects.TeacherList,
            '_get_data',
            return_value=jsonstr
        ):
            for t_raw, t in zip(jsonstr, self.session.teachers()):
                self.assertEqual(t_raw['longName'], t.long_name)
                self.assertEqual(t_raw['longName'], t.surname)
                self.assertEqual(t_raw['foreName'], t.fore_name)
                self.assertEqual(t_raw['name'], t.name)

    def test_gettimegrid_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/gettimegrid_mock.json')
        )
        with mock.patch.object(
            webuntis.objects.TimeunitList,
            '_get_data',
            return_value=jsonstr
        ):
            for t_raw, t in zip(jsonstr, self.session.timegrid()):
                self.assertEqual(t_raw['day'], t.day)
                for t2_raw, t2 in zip(t_raw['timeUnits'], t.times):
                    self.assertEqual(t2_raw['startTime'],
                                     int(t2[0].strftime('%H%M')))
                    self.assertEqual(t2_raw['endTime'],
                                     int(t2[1].strftime('%H%M')))

    def test_getstatusdata_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/getstatusdata_mock.json')
        )
        with mock.patch.object(
            webuntis.objects.StatusData,
            '_get_data',
            return_value=jsonstr
        ):
            statusdata = self.session.statusdata()
            for lstype_raw, lstype in zip(jsonstr['lstypes'],
                                          statusdata.lesson_types):
                name = list(lstype_raw.items())[0][0]
                colors = lstype_raw[name]
                self.assertEqual(name, lstype.name)
                self.assertEqual(colors['foreColor'], lstype.forecolor)
                self.assertEqual(colors['backColor'], lstype.backcolor)


class InternalTests(OfflineTestCase):
    '''Tests certain areas of the whole package, such as the utils'''
    def test_options_invalidattribute(self):
        self.assertFalse('nigglywiggly' in self.session.options)
        self.assertRaises(
            KeyError,
            self.session.options.__getitem__,
            'nigglywiggly'
        )

    def test_options_isempty(self):
        self.assertEqual(self.session.options, {'useragent': 'foobar'})

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

    def test_requestcaching(self):
        caching_data = [
            {'foo': 'bar'},
            {'boo': 'far'}
        ]

        def make_request_mock(session, method, params=None):
            self.assertEqual(method, 'example_method')
            return caching_data

        with mock.patch.object(
            webuntis.session.Session,
            '_make_request',
            new=make_request_mock
        ):
            self.assertEqual(caching_data,
                    self.session._request('example_method'))

        self.assertEqual(caching_data, self.session._request('example_method'))

    def test_listitem(self):
        session = None
        parent = None
        data = {'id': 42}
        item = webuntis.objects.ListItem(session, parent, data)

        self.assertEqual(item._session, session)
        self.assertEqual(item._parent, parent)
        self.assertEqual(item._data, data)
        self.assertEqual(item.id, data['id'])
        self.assertEqual(int(item), item.id)

    def test_result_object_without_parameters_method(self):
        with mock.patch.object(
            webuntis.objects.Result,
            '_jsonrpc_parameters',
            new=False
        ):
            self.assertRaises(
                NotImplementedError,
                webuntis.objects.Result, None, {}
            )

    def test_optionparsers_credentials(self):
        jsessionid = {'jsessionid': '123ABC'}
        void_jsessionid = {'jsessionid': None}
        user_and_pwd = {'username': 'markus', 'password': 'hunter2'}
        void_user_and_pwd = {'username': None, 'password': 'hunter2'}
        user_and_void_pwd = {'username': 'markus', 'password': None}
        void_user_and_void_pwd = {'username': None, 'password': None}

        tests = [
            (jsessionid, jsessionid),
            (void_jsessionid, {}),
            (user_and_pwd, user_and_pwd),
            (void_user_and_pwd, {}),
            (user_and_void_pwd, {}),
            (void_user_and_void_pwd, {}),
            (dict(user_and_pwd, **void_jsessionid), user_and_pwd)
        ]

        for parser_input, expected_output in tests:
            self.assertEqual(
                webuntis.utils.option_utils.credentials_parser(parser_input),
                expected_output
            )

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
                webuntis.utils.option_utils.server_parser(parser_input),
                expected_output
            )

        self.assertRaises(ValueError,
                webuntis.utils.option_utils.server_parser, '!"$%')

    def test_resultobject_get_data(self):
        kwargs = {}
        testclass = webuntis.objects.DepartmentList
        testobj = testclass(self.session, kwargs)

        def request_mock(session, method, params):
            self.assertEqual(method, testclass._jsonrpc_method)
            self.assertEqual(method, testobj._jsonrpc_method)
            self.assertEqual(params, testobj._jsonrpc_parameters(**kwargs))
            return {}

        with mock.patch.object(
            webuntis.session.Session,
            '_request',
            new=request_mock
        ):
            testobj.store_data()

    def helper_jsonrpc_parameters(self, resultclass):
        '''A wrapper for the _jsonrpc_parameters method of any result-type
        class.'''
        def jsonrpc_parameters(kwargs):
            return resultclass(
                self.session,
                {}
            )._jsonrpc_parameters(
                **kwargs
            )

        return jsonrpc_parameters

    def test_objects_klassenlist_jsonrpc_parameters(self):
        tests = [
            ({'schoolyear': 13}, {'schoolyearId': 13}),
            ({'schoolyear': "123"}, {'schoolyearId': 123})
        ]

        for given_input, expected_output in tests:
            self.assertEqual(
                self.helper_jsonrpc_parameters(webuntis.objects.KlassenList)(given_input),
                expected_output
            )

    def test_objects_periodlist_jsonrpc_parameters(self):
        parambuilder = self.helper_jsonrpc_parameters(webuntis.objects.PeriodList)
        dtobj = datetime.datetime.now()
        dtobj_formatted = int(dtobj.strftime('%Y%m%d'))
        tests = [
            ({'start': None, 'end': None, 'klasse': 123},
                {'id': 123, 'type': 1}),
            ({'start': None, 'end': None, 'teacher': 124},
                {'id': 124, 'type': 2}),
            ({'start': None, 'end': None, 'subject': 154},
                {'id': 154, 'type': 3}),
            ({'start': None, 'end': dtobj, 'subject': 1337},
                {
                    'id': 1337,
                    'type': 3,
                    'startDate': dtobj_formatted,
                    'endDate': dtobj_formatted
                }),
            ({'end': None, 'start': dtobj, 'subject': 1337},
                {
                    'id': 1337,
                    'type': 3,
                    'startDate': dtobj_formatted,
                    'endDate': dtobj_formatted
                })
        ]
        for given_input, expected_output in tests:
            self.assertEqual(
                parambuilder(given_input),
                expected_output
            )

        self.assertRaises(ValueError, parambuilder, {})
        self.assertRaises(ValueError, parambuilder, {'foobar': 123})
