import mock

import webuntis
from . import WebUntisTestCase, stub_session_parameters, \
    mock_results


class BasicUsage(WebUntisTestCase):
    def test_login_repeat_not_logged_in(self):
        s = webuntis.Session(**stub_session_parameters)
        retry_amount = 5
        calls = []

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
                'error': {'code': -8520, 'message': 'Not logged in!'}
            }

        def logout(url, jsondata, headers):
            calls.append(jsondata['method'])
            return {
                'result': {'bla': 'blub'}  # shouldn't matter
            }

        methods = {
            'authenticate': authenticate,
            'getCurrentSchoolyear': getCurrentSchoolyear,
            'logout': logout
        }

        with mock_results(methods):
            with mock.patch.dict(
                    s.config,
                    {'login_repeat': retry_amount}
            ):
                self.assertRaises(webuntis.errors.NotLoggedInError,
                                  s._request,
                                  'getCurrentSchoolyear')

        assert calls == expected_calls

    def test_logout_not_logged_in(self):
        session_params = dict(stub_session_parameters)
        del session_params['jsessionid']

        s = webuntis.Session(**session_params)

        self.assertRaises(webuntis.errors.NotLoggedInError, s.logout)
        s.logout(suppress_errors=True)

    def test_login_no_creds(self):
        session_params = dict(stub_session_parameters)
        del session_params['jsessionid']
        del session_params['username']
        del session_params['password']

        s = webuntis.Session(**session_params)
        self.assertRaises(webuntis.errors.AuthError, s.login)

    def test_login_successful(self):
        session_params = dict(stub_session_parameters)
        del session_params['jsessionid']

        s = webuntis.Session(**session_params)

        with mock.patch(
                'webuntis.Session._request',
                return_value={'sessionId': '123456'}
        ) as mock_obj:
            s.login()
            assert s.config['jsessionid'] == '123456'
            assert mock_obj.call_count == 1

    def test_login_no_response(self):
        session_params = dict(stub_session_parameters)
        del session_params['jsessionid']

        s = webuntis.Session(**session_params)

        with mock.patch(
                'webuntis.Session._request',
                return_value={}
        ) as mock_obj:
            self.assertRaises(webuntis.errors.AuthError, s.login)

    def test_context_manager(self):
        session_params = dict(stub_session_parameters)
        del session_params['jsessionid']
        s = webuntis.Session(**session_params)

        with s as mgr:
            assert mgr is s
            assert 'jsessionid' not in s.config

        sessionid = 'foobar_session'
        with mock.patch(
                'webuntis.Session._request',
                return_value={'sessionId': sessionid}
        ) as mock_obj:
            with s.login() as msg:
                assert mgr is s
                assert s.config['jsessionid'] == sessionid

    def test_custom_cachelen(self):
        s = webuntis.Session(cachelen=20, **stub_session_parameters)
        assert s.cache._maxlen == 20


class WrapperMethodTests(WebUntisTestCase):
    @staticmethod
    def noop_result_mock(methodname):
        def inner(url, jsondata, headers):
            return {'result': {}}

        return mock_results({methodname: inner})

    def test_departments(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock('getDepartments'):
            dep = s.departments()
            assert type(dep) is webuntis.objects.DepartmentList
            assert not dep

    def test_holidays(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock('getHolidays'):
            hol = s.holidays()
            assert type(hol) is webuntis.objects.HolidayList
            assert not hol

    def test_klassen(self):
        s = webuntis.Session(**stub_session_parameters)

        def getKlassen(url, jsondata, headers):
            assert not jsondata['params']
            return {'result': {}}

        with mock_results({'getKlassen': getKlassen}):
            kl = s.klassen()
            assert type(kl) is webuntis.objects.KlassenList
            assert not kl

    def test_klassen_with_schoolyear(self):
        s = webuntis.Session(**stub_session_parameters)
        yearid = 1232

        def getKlassen(url, jsondata, headers):
            assert jsondata['params']['schoolyearId'] == yearid
            return {'result': {}}

        with mock_results({'getKlassen': getKlassen}):
            kl = s.klassen(schoolyear=yearid)
            assert type(kl) is webuntis.objects.KlassenList
            assert not kl

    def test_timetable(self):
        s = webuntis.Session(**stub_session_parameters)

        startbase = 20120303
        endbase = 20120304

        idbase = 12330
        for i, name in enumerate((
                'klasse',
                'teacher',
                'subject',
                'room',
                'student'
        ), start=1):
            id = idbase + i
            start = startbase + i
            end = endbase + i

            def getTimetable(url, jsondata, headers):
                assert jsondata['params']['type'] == i
                assert jsondata['params']['id'] == id

                assert jsondata['params']['startDate'] == start
                assert jsondata['params']['endDate'] == end
                return {'result': {}}

            with mock_results({'getTimetable': getTimetable}):
                tt = s.timetable(start=start, end=end, **{name: id})
                assert type(tt) is webuntis.objects.PeriodList
                assert not tt
                assert type(tt.to_table()) is list

    def test_timetable_start_later_than_end(self):
        s = webuntis.Session(**stub_session_parameters)
        start = 20120308
        end = 20120303

        self.assertRaisesRegex(ValueError, 'later', s.timetable,
                               start=start, end=end, klasse=123)

    def test_timetable_invalid_obj_given(self):
        s = webuntis.Session(**stub_session_parameters)
        start = 20120303
        end = 20120304

        self.assertRaisesRegex(TypeError, 'by keyword', s.timetable,
                               start=start, end=end)
        self.assertRaisesRegex(TypeError, 'by keyword', s.timetable,
                               start=start, end=end, klasse=123, teacher=124)
        self.assertRaisesRegex(TypeError, 'by keyword', s.timetable,
                               start=start, end=end, foobar=128)

    def test_rooms(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock(u'getRooms'):
            ro = s.rooms()
            assert type(ro) is webuntis.objects.RoomList
            assert not ro

    def test_schoolyears(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock(u'getSchoolyears'):
            sch = s.schoolyears()
            assert type(sch) is webuntis.objects.SchoolyearList
            assert not sch

    def test_subjects(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock('getSubjects'):
            sb = s.subjects()
            assert type(sb) is webuntis.objects.SubjectList
            assert not sb

    def test_teachers(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock('getTeachers'):
            te = s.teachers()
            assert type(te) is webuntis.objects.TeacherList
            assert not te

    def test_statusdata(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock('getStatusData'):
            st = s.statusdata()
            assert type(st) is webuntis.objects.StatusData

    def test_lastImportTime(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock(u'getLatestImportTime'):
            li = s.last_import_time()
            assert type(li) is webuntis.objects.TimeStampObject

    def test_substitutions(self):
        s = webuntis.Session(**stub_session_parameters)

        def getSubstitutions(url, jsondata, headers):
            return {'result': []}

        with mock_results({'getSubstitutions': getSubstitutions}):
            start = 20120303
            end = 20120304
            st = s.substitutions(start=start, end=end)
            assert type(st) is webuntis.objects.SubstitutionList

    def test_timegridUnits(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock('getTimegridUnits'):
            st = s.timegrid_units()
            assert type(st) is webuntis.objects.TimegridObject

    def test_students(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock('getStudents'):
            st = s.students()
            assert type(st) is webuntis.objects.StudentsList
            assert len(st) == 0

    def test_examtype(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock(u'getExamTypes'):
            et = s.exam_types()
            assert type(et) is webuntis.objects.ExamTypeList

    def test_exams(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.noop_result_mock(u'getExams'):
            ex = s.exams(start=1, end=2, exam_type_id=1)
            assert type(ex) is webuntis.objects.ExamsList

    @staticmethod
    def absences_result_mock(methodname):
        def inner(url, jsondata, headers):
            return {"result": {u'periodsWithAbsences': []}}

        return mock_results({methodname: inner})

    def test_timetableWithAbsences(self):
        s = webuntis.Session(**stub_session_parameters)
        with self.absences_result_mock('getTimetableWithAbsences'):
            ex = s.timetable_with_absences(start=1, end=2)
            assert type(ex) is webuntis.objects.AbsencesList

    def test_use_cache(self):
        s = webuntis.Session(use_cache=True, **stub_session_parameters)
        assert webuntis.utils.result_wrapper.session_use_cache
        s = webuntis.Session(use_cache=False, **stub_session_parameters)
        assert not webuntis.utils.result_wrapper.session_use_cache
