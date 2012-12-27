'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals
from webuntis import utils, objects, errors
from webuntis.utils import result_wrapper, log
from webuntis.utils.third_party import json, urlrequest

import datetime


class JSONRPCRequest(object):
    _errorcodes = {
        -32601: errors.MethodNotFoundError,
        -8504: errors.BadCredentialsError,
        -8520: errors.NotLoggedInError
    }
    '''This lists the API-errorcodes python-webuntis is able to interpret,
    together with the exception that will be thrown.'''

    def __init__(self, session, method, params=None):
        self._session = session
        self._method = method
        self._params = params or {}

    def request(self):
        '''
        A method for sending a JSON-RPC request.

        :param method: The JSON-RPC method to be executed
        :type method: str

        :param params: JSON-RPC parameters to the method (should be JSON
        serializable)
        :type params: dict
        '''

        url = self._session.config['server'] + \
            '?school=' + \
            self._session.config['school']

        headers = {
            'User-Agent': self._session.config['useragent'],
            'Content-Type': 'application/json'
        }

        request_body = {
            'id': str(datetime.datetime.today()),
            'method': self._method,
            'params': self._params,
            'jsonrpc': '2.0'
        }

        if self._method != 'authenticate':
            if 'jsessionid' not in self._session.config:
                raise errors.NotLoggedInError(
                    'Don\'t have JSESSIONID. Did you already log out?')
            else:
                headers['Cookie'] = 'JSESSIONID=' + \
                    self._session.config['jsessionid']

        log('debug', 'Making new request:')
        log('debug', 'URL: ' + url)
        log('debug', 'DATA: ' + str(request_body))

        result_body = self._send_request(
            url,
            json.dumps(request_body).encode(),
            headers
        )
        return self._parse_result(request_body, result_body)

    @classmethod
    def _parse_result(cls, request_body, result_body):
        '''A subfunction of request, that, given the decoded JSON result,
        handles the error codes or, if everything went well, returns the result
        attribute of it. The request data has to be given too for logging and
        ID validation.

        :param request_body: The not-yet-encoded body of the request sent.
        :param result_body: The decoded body of the result recieved.
        '''

        if request_body['id'] != result_body['id']:
            raise errors.RemoteError(
                'Request ID was not the same one as returned.')

        try:
            return result_body['result']
        except KeyError:
            cls._parse_error_code(request_body, result_body)

    @classmethod
    def _parse_error_code(cls, request_body, result_body):
        '''A helper function for handling JSON error codes.'''
        log('error', result_body)
        try:
            error = result_body['error']
            exc = cls._errorcodes[error['code']](error['message'])
        except KeyError:
            exc = errors.RemoteError(
                ('Some JSON-RPC-ish error happened. Please report this to the '
                    'developer so he can implement a proper handling.'),
                str(result_body),
                str(request_body)
            )

        raise exc

    @staticmethod
    def _send_request(url, data, headers):
        '''A subfunction of request, mostly because of mocking. Sends the
        given headers and data to the url and tries to return the result
        JSON-decoded.
        '''

        request = urlrequest.Request(
            url,
            data,
            headers
        )
        # this will eventually raise errors, e.g. if there's an unexpected http
        # status code
        result_obj = urlrequest.urlopen(request)
        result = result_obj.read().decode('utf-8')

        try:
            result_data = json.loads(result)
            log('debug', 'Valid JSON found')
        except ValueError:
            raise errors.RemoteError('Invalid JSON', str(result))
        else:
            return result_data


class JSONRPCSession(object):
    '''Lower-level version of :py:class:`Session`. Do not use this.'''

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
            'login_repeat': 0
        }
        config.update(kwargs)
        self.config.update(config)

    def __enter__(self):
        '''Context-manager'''
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        '''Context-manager -- the only thing we need to clean up is to log out
        '''
        self.logout(suppress_errors=True)

    def logout(self, suppress_errors=False):
        '''
        Log out of session

        :type suppress_errors: bool
        :param suppress_errors: Whether to suppress errors.

        :raises: :py:class:`webuntis.errors.NotLoggedInError` -- Can't log out
            because not logged in. Raised unless ``suppress_errors`` is
            ``True``.
        '''
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
        '''Initializes an authentication, provided we have the credentials for
        it.

        :returns: The session. This is useful for jQuery-like command
            chaining::

                s = webuntis.Session(...).login()

        :raises: :py:class:`webuntis.errors.BadCredentialsError` --
            Username/Password missing or invalid.
        :raises: :py:class:`webuntis.errors.AuthError` -- Didn't recieve a
            session ID for unknown reasons.
        '''

        if 'username' not in self.config \
                or 'password' not in self.config:
            raise errors.BadCredentialsError('No login data specified.')

        log('debug', 'Trying to authenticate with username/password...')
        log('debug', 'Username: %s Password: %s' %
           (self.config['username'], self.config['password']))
        res = self._request('authenticate', {
            'user': self.config['username'],
            'password': self.config['password'],
            'client': self.config['useragent']
        }, use_login_repeat=False)
        log('debug', res)
        if 'sessionId' in res:
            log('debug', 'Did get a jsessionid from the server:')
            self.config['jsessionid'] = res['sessionId']
            log('debug', self.config['jsessionid'])
        else:
            raise errors.AuthError(
                'Something went wrong while authenticating',
                res
            )

        return self

    def _request(self, method, params=None, use_login_repeat=None):
        if use_login_repeat is None:
            use_login_repeat = (method not in ('logout', 'authenticate'))
        attempts_left = self.config['login_repeat'] if use_login_repeat else 0

        data = None

        while data is None:
            try:
                data = JSONRPCRequest(self, method, params).request()
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
        '''Get all departments.

        :rtype: :py:class:`webuntis.objects.DepartmentList`
        '''
        return objects.DepartmentList, 'getDepartments', {}

    @result_wrapper
    def holidays(self):
        '''Get all holidays.

        :rtype: :py:class:`webuntis.objects.HolidayList`
        '''
        return objects.HolidayList, 'getHolidays', {}

    @result_wrapper
    def klassen(self, schoolyear=None):
        '''Get all school classes.

        :param schoolyear: The schoolyear where the classes should be fetched
            from.
        :type schoolyear: :py:class:`webuntis.objects.SchoolyearObject` or an
            integer ID of it.

        :rtype: :py:class:`webuntis.objects.KlassenList`
        '''
        params = {}
        if schoolyear:
            params['schoolyearId'] = int(schoolyear)

        return objects.KlassenList, 'getKlassen', params

    @result_wrapper
    def timetable(self, start=None, end=None, **type_and_id):
        '''Get the timetable for a specific school class and time period.

        :param start: The beginning of the time period. Can be a
            :py:class:`datetime.datetime` object or a string of the format
            ``YYMMDD``.

        :param end: The end of the time period, same type as ``start``.

        :rtype: :py:class:`webuntis.objects.PeriodList`

        Furthermore you have to explicitly define a klasse, teacher, subject,
        room or student parameter containing the id or the object of the thing
        you want to get a timetable about::

            schoolclass = s.klassen().filter(id=1)[0]  # schoolclass #1

        :raises: :py:class:`ValueError` -- if something was wrong with the
            arguments supplied.

        '''
        element_type_table = {
            'klasse':  1,
            'teacher': 2,
            'subject': 3,
            'room':    4,
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

        if element_type not in element_type_table:
            raise invalid_type_error

        # apply end to start and vice-versa if one of them is missing
        if not start and end:
            start = end
        elif not end and start:
            end = start

        # if we have to deal with an object in element_id,
        # its id gets placed here anyway
        parameters = {
            'id': int(element_id),
            'type': element_type_table[element_type],
        }

        if start:
            parameters['startDate'] = utils.datetime_utils.format_date(start)
        if end:
            parameters['endDate'] = utils.datetime_utils.format_date(end)

        return objects.PeriodList, 'getTimetable', parameters

    @result_wrapper
    def rooms(self):
        '''Get all rooms of a school.

        :rtype: :py:class:`webuntis.objects.RoomList`
        '''
        return objects.RoomList, 'getRooms', {}

    @result_wrapper
    def schoolyears(self):
        '''Get all schoolyears.

        :rtype: :py:class:`webuntis.objects.SchoolyearList`
        '''
        return objects.SchoolyearList, 'getSchoolyears', {}

    @result_wrapper
    def subjects(self):
        '''Get all subjects.

        :rtype: :py:class:`webuntis.objects.SubjectList`
        '''
        return objects.SubjectList, 'getSubjects', {}

    @result_wrapper
    def teachers(self):
        '''Get all teachers.

        :rtype: :py:class:`webuntis.objects.TeacherList`
        '''
        return objects.TeacherList, 'getTeachers', {}

    @result_wrapper
    def timegrid(self):
        '''Get a "timegrid", whatever the hell that is. According to the
        official API docs, it is supposed to be useful when generating your own
        timetable. Maybe :py:meth:`webuntis.objects.PeriodList.to_table` could
        make use of this one day.

        :rtype: :py:class:`webuntis.objects.TimeunitList`
        '''
        return objects.TimeunitList, 'getTimegridUnits', {}

    @result_wrapper
    def statusdata(self):
        '''Information about lesson types and period codes, specifically about
        the colors used to highlight them in the web-interface of WebUntis.

        :rtype: :py:class:`webuntis.objects.StatusData`
        '''
        return objects.StatusData, 'getStatusData', {}


class Session(JSONRPCSession, ResultWrapperMixin):
    '''The origin of everything you want to do with the WebUntis API. Can be
    used as a context-handler.

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

            >>> s = webuntis.Session(..., server='thalia.webuntis.com')
            >>> s.config['server']
            'http://thalia.webuntis.com/WebUntis/jsonrpc.do'
            >>> # notice that there's NO SLASH at the end!
            >>> s.config['server'] = 'https://thalia.webuntis.com'
            >>> s.config['server']
            'https://thalia.webuntis.com/WebUntis/jsonrpc.do'
            >>> s.config['server'] = 'https://thalia.webuntis.com/'
            >>> # because a slash gets interpreted as the full path to the API
            >>> # endpoint, which would crash during login
            >>> s.config['server']
            'http://thalia.webuntis.com/'
            >>> s.config['server'] = '!"$%/WebUntis/jsonrpc.do'
            Traceback blah blah something ValueError

    :type school: str
    :param school: A valid school name.

    :type useragent: str
    :param useragent: A string containing a useragent. Please include useful
        information, such as an email address, for the server maintainer. Just
        like you would do with the HTTP useragents of bots.

    :type cachelen: int
    :param cachelen: The maximum size of the internal cache. All results are
        saved in it, but only used if you set the ``from_cache`` parameter on a
        session method to ``True``.

        ::
            s.timetable(klasse=123)  # saves in cache
            s.timetable(klasse=123)  # fetch data again, override old value
            s.timetable(klasse=123, from_cache=True)  # get directly from cache

        The reason this cache was added is because the API doesn't allow you to
        fetch information for e.g. a single teacher. It would seriously harm
        performance to fetch the whole list each time we want information about
        a teacher. And i am not just talking about some milliseconds, but up to
        thirty seconds of difference.

    :type jsessionid: str
    :param jsessionid: The session key to use. You usually shouldn't
        touch this.

    :param login_repeat: The amount of times `python-webuntis`
        should try to login when finding no or an expired session. Default to
        ``0``, meaning it won't do that.

    '''

    cache = None
    '''Contains the caching dictionary for requests.'''

    # Repeated here because sphinx doesn't recognize it when defined in
    # JSONRPCSession:
    config = None
    '''The config dictionary, filled with most keyword arguments from
    initialization.'''

    def __init__(self, **config):
        try:
            cachelen = config['cachelen']
            del config['cachelen']
        except KeyError:
            cachelen = 20

        self.cache = utils.SessionCache(maxlen=cachelen)

        JSONRPCSession.__init__(self, **config)
