'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
import unittest
import mock
import os
import sys
import webuntis
from webuntis.utils import timetable_utils, datetime_utils, option_utils
import webuntis.utils as utils
import datetime
import json
import logging

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
        ) as test_mock:
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
        ) as test_mock:
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
        ) as test_mock:
            klassen = self.session.klassen()
            for klasse_raw, klasse in zip(jsonstr, klassen):
                self.assertEqual(klasse_raw['longName'], klasse.long_name)
                self.assertEqual(klasse_raw['name'], klasse.name)
                self.assertEqual(klasse_raw['id'], klasse.id)

            self.assertEqual(klassen.filter(id=129)[0].id, 129)
            self.assertEqual(
                [129,130,137],
                sorted(
                    kl.id for kl in 
                    klassen.filter(id=(129,130,137))
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
        ) as test_mock:
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
        ) as test_mock:
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
        ) as test_mock:
            schoolyears = self.session.schoolyears()

        with mock.patch.object(
            webuntis.session.Session,
            '_request',
            return_value=current_json
        ) as test_mock:
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
        ) as test_mock:
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
        ) as test_mock:
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
        ) as test_mock:
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
        ) as test_mock:
            statusdata = self.session.statusdata()
            for lstype_raw, lstype in zip(jsonstr['lstypes'],
                                          statusdata.lession_types):
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
        ) as test_mock:
            self.assertEqual(caching_data, self.session._request('example_method')) 

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
        ) as test_mock:
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
            ('webuntis.grupet.at', 'http://webuntis.grupet.at/WebUntis/jsonrpc.do'),
            ('https://webuntis.grupet.at', 'https://webuntis.grupet.at/WebUntis/jsonrpc.do'),
            ('webuntis.grupet.at:8080', 'http://webuntis.grupet.at:8080/WebUntis/jsonrpc.do'),
            ('webuntis.grupet.at/a/b/c', 'http://webuntis.grupet.at/a/b/c'),
            ('webuntis.grupet.at/', 'http://webuntis.grupet.at/'),
            ('!"$%', None)
        ]

        for parser_input, expected_output in tests:
            self.assertEqual(
                webuntis.utils.option_utils.server_parser(parser_input),
                expected_output
            )

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
        ) as test_mock:
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


class RemoteTests(TestCaseBase):
    '''
    DEPRECATED. This only should be used if you want to test the library
    actually against a public test-server, which will take a very long time and
    will stress that server unneccessarily.
    '''
    def setUp(self):
        self.session = webuntis.session.Session(
            school='demo_inf',
            server='webuntis.grupet.at:8080',
            username='api',
            password='api',
            useragent='WebUntis Unittests'
        ).login()
        print('\n' + '*' * 100)

    def tearDown(self):
        try:
            self.session.logout()
        except:
            logging.warning('Was not able to log out!')
        finally:
            self.session = None

    def test_timetableutils_table_emptyinput(self):
        self.assertEqual(len(webuntis.utils.timetable_utils.table([])), 0)

    ## OBJECTS

    def test_getdepartments(self):
        self.session.departments()

    def test_getholidays(self):
        self.session.holidays()

    def test_getklassen(self):
        print('TEST_GETKLASSEN')
        klassen = self.session.klassen()

        for klasse in klassen:
            self.assertEqual(klasse.__class__,
                             webuntis.objects.KlassenObject)

            klasse.id
            klasse.name
            klasse.long_name

    def test_getrooms(self):
        self.session.rooms()

    def test_getschoolyears(self):
        self.session.schoolyears()

    def test_getsubjects(self):
        self.session.subjects()

    def test_getteachers(self):
        print('TEST_GETTEACHERS')
        teachers = self.session.teachers()

        for teacher in teachers:
            self.assertEqual(teacher.__class__,
                             webuntis.objects.TeacherObject)

            teacher.fore_name
            teacher.name
            teacher.surname
            teacher.long_name
            teacher.id

    def test_gettimeunits(self):
        self.session.timeunits()

    def test_gettimetables(self):
        print('TEST_GETTIMETABLES')
        timetables = []
        for i, klasse in enumerate(self.session.klassen()):
            if i > 5:
                break
            timetable = self.session.timetable(klasse=klasse)
            print('Length of timetable: ' + str(len(timetable)))
            timetables.append(timetable)

    ## /OBJECTS

    def test_emptyfilter(self):
        print('TEST_EMPTYFILTER')
        for klasse, klasse_filtered, i in zip(
            self.session.klassen(),
            self.session.klassen().filter(),
            range(len(self.session.klassen()))
        ):
            self.assertEqual(klasse.id, klasse_filtered.id)

    def test_loggedout(self):
        self.session.logout()
        creds = self.session.options['credentials']
        self.assertFalse('jsessionid' in creds)
        self.assertRaises(webuntis.errors.AuthError, self.session.klassen)



def suite_from_cases(*cases):
    return unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
        cases))

# This is the test suite that should cover everything. Should.
usual_tests = suite_from_cases(BasicUsageTests, InternalTests)

# This is a deprecated test suite whose test cases, for example, just use the
# API with an actual server and just check if it didn't raise exceptions.
deprecated_tests = suite_from_cases(RemoteTests)

# This includes all of the above.
all_tests = unittest.TestSuite((usual_tests, deprecated_tests))


def get_suite(names):
    '''Builds a suite from the list of case/suite names'''
    suite = unittest.TestSuite([globals()[name] for name in names])
    return suite


def main():
    suite = get_suite(sys.argv[1:] or ['usual_tests'])
    result = unittest.TextTestRunner(verbosity=2).run(suite) 
    if result.errors or result.failures:
        sys.exit(1)

if __name__ == '__main__':
    main()
