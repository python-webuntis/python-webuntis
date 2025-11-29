"""
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
"""
from webuntis import utils, objects, errors
from webuntis.utils import result_wrapper, log, rpc_request
from webuntis.utils.userinput import unicode_string


class JSONRPCSession(object):
    """Lower-level version of :py:class:`Session`. Do not use this."""

    config = None
    '''Dictionary with configuration.'''

    def __init__(self, **kwargs):
        self.config = utils.FilterDict(utils.config_keys)
        config = {
            'server': None,
            'school': None,
            'useragent': None,
            'username': None,
            'password': None,
            'jsessionid': None,
            'login_repeat': 0,
            '_http_session': None
        }
        config.update(kwargs)
        self.config.update(config)

    def __enter__(self):
        """Context-manager"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context-manager -- the only thing we need to clean up is to log out
        """
        self.logout(suppress_errors=True)

    def logout(self, suppress_errors=False):
        """
        Log out of session

        :type suppress_errors: bool
        :param suppress_errors: Whether to suppress errors.

        :raises: :py:class:`webuntis.errors.NotLoggedInError` -- Can't log out
            because not logged in. Raised unless ``suppress_errors`` is
            ``True``.
        """

        def throw_errors():
            if not suppress_errors:
                raise errors.NotLoggedInError('We already were logged out.')

        try:
            # Send a JSON-RPC 'logout' method without parameters to log out
            self._request('logout')
        except errors.NotLoggedInError:
            throw_errors()

        try:
            del self.config['jsessionid']
        except KeyError:
            throw_errors()

    def login(self):
        """Initializes an authentication, provided we have the credentials for
        it.

        :returns: The session. This is useful for jQuery-like command
            chaining::

                s = webuntis.Session(...).login()

        :raises: :py:class:`webuntis.errors.BadCredentialsError` --
            Username/Password missing or invalid.
        :raises: :py:class:`webuntis.errors.AuthError` -- Didn't receive a
            session ID for unknown reasons.
        """

        try:
            username = self.config['username']
            password = self.config['password']
            useragent = self.config['useragent']
        except KeyError as e:
            raise errors.BadCredentialsError('Missing config: ' + str(e))

        res = self._request('authenticate', {
            'user': username,
            'password': password,
            'client': useragent
        }, use_login_repeat=False)

        if 'sessionId' in res:
            sid = self.config['jsessionid'] = res['sessionId']
            log('debug', 'Did get a jsessionid from the server: ' + sid)
        else:
            raise errors.AuthError('Something went wrong while authenticating',
                                   res)
        self.login_result = dict()
        if 'personType' in res:
            self.login_result['personType'] = res['personType']
            self.login_result['personId'] = res['personId']
        if "klasseId" in res:
            self.login_result['klasseId'] = res['klasseId']

        return self

    def _request(self, method, params=None, use_login_repeat=None):
        if not isinstance(method, unicode_string):
            method = method.decode('ascii')

        if use_login_repeat is None:
            use_login_repeat = (method not in ('logout', 'authenticate'))
        attempts_left = self.config['login_repeat'] if use_login_repeat else 0

        data = None

        while data is None:
            try:
                data = rpc_request(self.config, method, params or {})
            except errors.NotLoggedInError:
                if attempts_left > 0:
                    self.logout(suppress_errors=True)
                    self.login()
                else:
                    raise errors.NotLoggedInError(
                        'Tried to login several times, failed. Original method'
                        ' was ' + method)
            else:
                return data

            attempts_left -= 1  # new round!


class ResultWrapperMixin(object):
    @result_wrapper
    def departments(self):
        """Get all departments.

        :rtype: :py:class:`webuntis.objects.DepartmentList`
        """
        return objects.DepartmentList, 'getDepartments', {}

    @result_wrapper
    def holidays(self):
        """Get all holidays.

        :rtype: :py:class:`webuntis.objects.HolidayList`
        """
        return objects.HolidayList, 'getHolidays', {}

    @result_wrapper
    def klassen(self, schoolyear=None):
        """Get all school classes.

        :param schoolyear: The schoolyear where the classes should be fetched
            from.
        :type schoolyear: :py:class:`webuntis.objects.SchoolyearObject` or an
            integer ID of it

        :rtype: :py:class:`webuntis.objects.KlassenList`
        """
        params = {}
        if schoolyear:
            params['schoolyearId'] = int(schoolyear)

        return objects.KlassenList, 'getKlassen', params

    @result_wrapper
    def timetable(self, start, end, **type_and_id):
        """Get the timetable for a specific school class and time period.

        :type start: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param start: The beginning of the time period.

        :type end: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param end: The end of the time period.

        :rtype: :py:class:`webuntis.objects.PeriodList`

        Furthermore you have to explicitly define a klasse, teacher, subject,
        room or student parameter containing the id or the object of the thing
        you want to get a timetable about::

            import datetime
            today = datetime.date.today()
            monday = today - datetime.timedelta(days=today.weekday())
            friday = monday + datetime.timedelta(days=4)

            klasse = s.klassen().filter(id=1)[0]  # schoolclass #1
            tt = s.timetable(klasse=klasse, start=monday, end=friday)

        :raises: :exc:`ValueError`, :exc:`TypeError`
        """
        element_type_table = {
            'klasse': 1,
            'teacher': 2,
            'subject': 3,
            'room': 4,
            'student': 5
        }

        invalid_type_error = TypeError(
            'You have to specify exactly one of the following parameters by '
            'keyword: ' +
            (', '.join(element_type_table.keys()))
        )

        if len(type_and_id) != 1:
            raise invalid_type_error

        element_type, element_id = list(type_and_id.items())[0]

        element_type = utils.userinput.string(element_type)

        if element_type not in element_type_table:
            raise invalid_type_error

        # if we have to deal with an object in element_id,
        # its id gets placed here anyway

        parameters = self._create_date_param(end, start,
                                             id=int(element_id), type=element_type_table[element_type])
        return objects.PeriodList, 'getTimetable', parameters

    @result_wrapper
    def timetable_extended(self, start, end, key_type="id", teacher_fields=["id"], **type_and_id):
        """Get the timetable for a specific school class and time period.

        Like timetable, but includes more info.
        """
        element_type_table = {
            'klasse': 1,
            'teacher': 2,
            'subject': 3,
            'room': 4,
            'student': 5
        }

        invalid_type_error = TypeError(
            'You have to specify exactly one of the following parameters by '
            'keyword: ' +
            (', '.join(element_type_table.keys()))
        )

        if len(type_and_id) != 1:
            raise invalid_type_error

        element_type, element_id = list(type_and_id.items())[0]

        element_type = utils.userinput.string(element_type)

        if element_type not in element_type_table:
            raise invalid_type_error

        return self._timetable_extended_raw(end, start, element_id, element_type_table[element_type], key_type, teacher_fields)

    @result_wrapper
    def my_timetable(self, end, start):
        """Get the timetable for the logged-in user.

        see timetable_extended.
        """
        return self._timetable_extended_raw(end, start,
                                            self.login_result['personId'], self.login_result['personType'])


    def _timetable_extended_raw(self, end, start, element_id, element_type_num, key_type="id", teacher_fields=["id"]):
        element = {
            "id" : int(element_id) if key_type == "id" else element_id,
            "type": element_type_num,
            "keyType": key_type
        }
        options = self._create_date_param(end,
                                          start,
                                          element=element,
                                          teacherFields=teacher_fields,
                                          onlyBaseTimetable=False,
                                          showBooking=True,
                                          showInfo=True,
                                          showSubstText=True,
                                          showLsText=True,
                                          showLsNumber=True,
                                          showStudentgroup=True,
                                          )
        parameters = {
            "options": options,
        }
        return objects.PeriodList, 'getTimetable', parameters

    @result_wrapper
    def rooms(self):
        """Get all rooms of a school.

        :rtype: :py:class:`webuntis.objects.RoomList`
        """
        return objects.RoomList, 'getRooms', {}

    @result_wrapper
    def schoolyears(self):
        """Get all schoolyears.

        :rtype: :py:class:`webuntis.objects.SchoolyearList`
        """
        return objects.SchoolyearList, 'getSchoolyears', {}

    @result_wrapper
    def subjects(self):
        """Get all subjects.

        :rtype: :py:class:`webuntis.objects.SubjectList`
        """
        return objects.SubjectList, 'getSubjects', {}

    @result_wrapper
    def teachers(self):
        """Get all teachers.

        :rtype: :py:class:`webuntis.objects.TeacherList`
        """
        return objects.TeacherList, 'getTeachers', {}

    @result_wrapper
    def statusdata(self):
        """Information about lesson types and period codes, specifically about
        the colors used to highlight them in the web-interface of WebUntis.

        :rtype: :py:class:`webuntis.objects.StatusData`
        """
        return objects.StatusData, 'getStatusData', {}

    @result_wrapper
    def last_import_time(self):
        """Information about the last change made.

        :rtype: py:class:`webuntis.objects.TimeStampObject`
        """
        return objects.TimeStampObject, 'getLatestImportTime', {}

    @result_wrapper
    def substitutions(self, start, end, department_id=0):
        """Get all substitutions.


        :type start: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param start: The beginning of the time period.

        :type end: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param end: The end of the time period.

        :param department_id:  int, set to 0 for all departments or  if not applicable

        :rtype: :py:class:`webuntis.objects.SubstitutionList`
        """

        parameters = self._create_date_param(end, start, departmentId=department_id)
        return objects.SubstitutionList, 'getSubstitutions', parameters

    @result_wrapper
    def timegrid_units(self):
        """Information about the Timegrid.

        :return:
        :rtype: :py:class:`webuntis.objects.TimegridObject`
        """
        return objects.TimegridObject, 'getTimegridUnits', {}

    @result_wrapper
    def students(self):
        """Get all students

        :rtype:  :py:class:`webuntis.objects.StudentsList`
        """
        return objects.StudentsList, 'getStudents', {}

    @result_wrapper
    def exam_types(self):
        """Information about the Exam types.
        needs additional rights Master/Exam Types -- Stammdaten /Pruefungsart

        :rtype:  :py:class:`webuntis.objects.ExamTypeList`
        """
        return objects.ExamTypeList, 'getExamTypes', {}

    @result_wrapper
    def exams(self, start, end, exam_type_id=0):
        """Information about the Exams.

        :type start: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param start: The beginning of the time period.

        :type end: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param end: The end of the time period.

        :param exam_type_id:  int - id of Exam, @TODO: allow examtype id/name

        :rtype: :py:class:`webuntis.objects.ExamsList`
        """

        parameters = self._create_date_param(end, start, examTypeId=exam_type_id)
        return objects.ExamsList, 'getExams', parameters

    @result_wrapper
    def timetable_with_absences(self, start, end):
        """Information about the Exams.

        :type start: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param start: The beginning of the time period.

        :type end: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param end: The end of the time period.

        :rtype: :py:class:`webuntis.objects.AbsencesList`
        """

        parameters = {u'options': self._create_date_param(end, start)}

        return objects.AbsencesList, 'getTimetableWithAbsences', parameters

    @result_wrapper
    def class_reg_events(self, start, end):
        """Information about the ClassRegEvents
        :type start: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param start: The beginning of the time period.

        :type end: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param end: The end of the time period.

        :rtype: :py:class:`webuntis.objects.ClassRegEventList`
        """
        parameters = self._create_date_param(end, start)
        return objects.ClassRegEventList, 'getClassregEvents', parameters

    # @TODO this is a copy of timetable()

    @result_wrapper
    def class_reg_event_for_id(self, start, end, **type_and_id):
        """Get the Information about the ClassRegEvents for a specific school class and time period.

        :type start: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param start: The beginning of the time period.

        :type end: :py:class:`datetime.datetime` or  :py:class:`datetime.date` or int
        :param end: The end of the time period.

        :rtype: :py:class:`webuntis.objects.ClassRegEventList`

        see timetable for the type_and_id parameter

        :raises: :exc:`ValueError`, :exc:`TypeError`
        """
        element_type_table = {
            'klasse': 1,
            'teacher': 2,
            'subject': 3,
            'room': 4,
            'student': 5
        }

        invalid_type_error = TypeError(
            'You have to specify exactly one of the following parameters by '
            'keyword: ' +
            (', '.join(element_type_table.keys()))
        )

        if len(type_and_id) != 1:
            raise invalid_type_error

        element_type, element_id = list(type_and_id.items())[0]

        element_type = utils.userinput.string(element_type)

        if element_type not in element_type_table:
            raise invalid_type_error

        # if we have to deal with an object in element_id,
        # its id gets placed here anyway

        parameters = self._create_date_param(end, start,
                                             id=int(element_id), type=element_type_table[element_type])
        return objects.ClassRegEventList, 'getClassregEvents', parameters

    @result_wrapper
    def class_reg_categories(self):
        """Information about the Request remark categories

        :rtype: :py:class:`webuntis.objects.ClassRegClassRegCategoryList`
        """
        return objects.ClassRegCategoryList, 'getClassregCategories', {}

    @result_wrapper
    def class_reg_category_groups(self):
        """Information about the Request remark categories groups

        :rtype: :py:class:`webuntis.objects.ClassRegClassRegCategoryGroupList`
        """
        return objects.ClassRegCategoryGroupList, 'getClassregCategoryGroups', {}

    @staticmethod
    def _create_date_param(end, start, **kwargs):
        json_start = utils.datetime_utils.format_date(start)
        json_end = utils.datetime_utils.format_date(end)
        if json_start > json_end:
            raise ValueError('Start can\'t be later than the end.')
        parameters = dict({
            'startDate': json_start,
            'endDate': json_end,
        }, **kwargs)
        return parameters

    def get_student(self, surname, fore_name, dob=0):
        """
        Search for a student by name

        :param surname:  family name
        :type surname: str
        :param fore_name: fore name
        :type fore_name: str
        :param dob: date of birth, use 0 if unknown -- unknown Unit!
        :type dob: int
        :return: a dummy StudentObject with just the id filled
        :raises: :exc:`KeyError`
        """
        s = self._search(surname=surname, fore_name=fore_name, dob=dob, what=5)
        id = s._data
        if not id:
            raise KeyError("Student not found")

        data = {"id": id, "name": surname, "longName": surname, "foreName": fore_name}
        return objects.StudentObject(data=data, parent=s._parent, session=s._session)

    def get_teacher(self, surname, fore_name, dob=0):
        """
        Search for a teacher by name

        :param surname:  family name
        :type surname: str
        :param fore_name: fore name
        :type fore_name: str
        :param dob: date of birth, use 0 if unknown -- unknown Unit!
        :type dob: int
        :return: a dummy TeacherObject with just the id and name filled
        :raises: :exc:`KeyError`
        """
        t = self._search(surname=surname, fore_name=fore_name, dob=dob, what=2)
        id = t._data
        if not id:
            raise KeyError("Teacher not found")

        data = {"id": id, "name": surname, "longName": surname, "foreName": fore_name, "title": ""}
        return objects.TeacherObject(data=data, parent=t._parent, session=t._session)

    @result_wrapper
    def _search(self, surname, fore_name, dob=0, what=-1):
        """
        search for student or teacher
        :rtype: :py:class:`webuntis.objects._OnlyID`
        """
        return objects.Result, 'getPersonId', {
            "sn": surname, "fn": fore_name, "dob": dob, "type": what
        }


class Session(JSONRPCSession, ResultWrapperMixin):
    """The origin of everything you want to do with the WebUntis API. Can be
    used as a context-manager to provide automatic log-out.

    Configuration can be set with keyword arguments when initializing
    :py:class:`Session`. Unless noted otherwise, they get saved in a dictionary
    located in the instance's :py:attr:`config` attribute and can be modified
    afterwards.

    :type username: str
    :param username: The username used for the API.

    :type password: str
    :param password: The password used for the API.

    :type server: str
    :param server: A host name, a URL, or a URL without path.

        ::

            s = webuntis.Session(..., server='thalia.webuntis.com')
            # 'https://thalia.webuntis.com/WebUntis/jsonrpc.do'

            # Want to disable SSL?
            # make sure there's NO SLASH at the end!
            s.config['server'] = 'http://thalia.webuntis.com'
            # 'http://thalia.webuntis.com/WebUntis/jsonrpc.do'

            # or maybe use a completely different API endpoint?
            s.config['server'] = 'http://thalia.webuntis.com/WebUntis/jsonrpc2.do'
            # 'http://thalia.webuntis.com/WebUntis/jsonrpc2.do'

            # or just change the path?
            s.config['server'] = 'thalia.webuntis.com/WebUntis/jsonrpc2.do'
            # 'https://thalia.webuntis.com/WebUntis/jsonrpc2.do'

            s.config['server'] = '!"$%/WebUntis/jsonrpc.do'
            # ValueError: Not a valid hostname

    :type school: str
    :param school: A valid school name.

    :type useragent: str
    :param useragent: A string containing a useragent. Please include useful
        information, such as an email address, for the server maintainer. Just
        like you would do with the HTTP useragents of bots.

    :type cachelen: int
    :param cachelen: The maximum size of the internal cache. All results are
        saved in it, but they only get used if you set the ``from_cache``
        parameter on a session method to ``True``. This parameter is not saved
        in the configuration dictionary.

        ::

            s.timetable(klasse=123)  # saves in cache
            s.timetable(klasse=123)  # fetch data again, override old value
            s.timetable(klasse=123, from_cache=True)  # get directly from cache

        The reason this cache was added is that the API only allows you to
        fetch a whole list of objects (teachers/schoolclasses/...), not single
        ones. It would seriously harm performance to fetch the whole list each
        time we want information about a single object. Without the cache, i
        sometimes experienced a performance decrease about twenty seconds, so i
        wouldn't set the ``cachelen`` to anything smaller than ``5``.

        Default value is ``20``.

        You can clear the cache using::

            s.cache.clear('timetable')  # clears all cached timetables
            s.cache.clear()  # clears everything from the cache

    :type jsessionid: str
    :param jsessionid: The session key to use. You usually shouldn't touch
        this.

    :type login_repeat: int
    :param login_repeat: The amount of times `python-webuntis` should try to
        login when finding no or an expired session. Default to ``0``, meaning
        it won't do that.

    :type use_cache: bool
    :param use_cache: always use the cache
    """

    cache = None
    '''Contains the caching dictionary for requests.'''

    # Repeated here because sphinx doesn't recognize it when defined in
    # JSONRPCSession:
    config = None
    '''The config dictionary, filled with most keyword arguments from
    initialization.'''

    def __init__(self, **config):
        if 'use_cache' in config:
            result_wrapper.session_use_cache = bool(config['use_cache'])
            del config['use_cache']
        cachelen = config.pop('cachelen', 20)
        self.cache = utils.SessionCache(maxlen=cachelen)
        JSONRPCSession.__init__(self, **config)
