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
import json
import logging

class WebUntisTests:
    tests_path = os.path.abspath(os.path.dirname(__file__))
    data_path = tests_path + '/static'


class WebUntisOfflineTests(unittest.TestCase, WebUntisTests):
    '''
    Mocking tests. New tests should be written here.
    '''
    def setUp(self):
        self.request_patcher = patcher = mock.patch(
            'webuntis.Session._request',
            side_effect=Exception('This is an OFFLINE testsuite!')
        )
        patcher.start()

        self.session = webuntis.Session()

    def tearDown(self):
        self.request_patcher.stop()
        self.session = None

    def test_options_invalidattribute(self):
        self.assertFalse('nigglywiggly' in self.session.options)
        self.assertRaises(
            KeyError,
            self.session.options.__getitem__,
            'nigglywiggly'
        )

    def test_options_isempty(self):
        self.assertEqual(self.session.options, {})

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

            self.assertEqual(self.session.klassen().filter(id=129)[0].id, 129)
            self.assertEqual(
                {129,130,137},
                set(
                    kl.id for kl in
                    klassen.filter(id={129,130,137})
                )
            )
            self.assertEqual(
                {129,130,137},
                set(
                    kl.id for kl in
                    klassen.filter(id=[129,130,137])
                )
            )
            self.assertEqual(
                {129,130,137},
                set(
                    kl.id for kl in 
                    klassen.filter(id=(129,130,137))
                )
            )

    def test_gettimetables_mock(self):
        jsonstr = json.load(
            open(self.data_path + '/gettimetables_mock.json')
        )
        periodlist_class = webuntis.objects.PeriodList

        with mock.patch.object(
            periodlist_class,
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
        with mock.patch.object(
            webuntis.objects.SchoolyearList,
            '_get_data',
            return_value=jsonstr
        ) as test_mock:
            for year_raw, year in zip(jsonstr, self.session.schoolyears()):
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



class WebUntisRemoteTests(unittest.TestCase, WebUntisTests):
    '''
    DEPRECATED. This only should be used if you want to test the library
    against actually against a public test-server, which will take a very long
    time and will stress that server unneccessarily.
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


def main():
    try:
        raw_input  # check if we have python2
    except NameError:
        prompt = input
    else:
        prompt = raw_input

    def load(test):
        suite = unittest.TestLoader().loadTestsFromTestCase(test)
        unittest.TextTestRunner(verbosity=2).run(suite)

    tests = [WebUntisOfflineTests, WebUntisRemoteTests]

    if len(sys.argv) == 1:
        print('ERROR: No tests specified.\nAdd a number to the command-line arguments to execute the test:\n')
        for i, test in enumerate(tests):
            print('###{}: {}'.format(i, test.__name__))
            print(test.__doc__)
        exit(1)

    checked_tests = [tests[int(x)] for x in sys.argv[1:]]

    for test in checked_tests:
        prompt('Hit enter to continue.')
        load(test)

if __name__ == '__main__':
    main()
