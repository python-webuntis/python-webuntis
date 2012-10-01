'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals

import webuntis
import logging

from webuntis.tests.utils import TestCaseBase


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
