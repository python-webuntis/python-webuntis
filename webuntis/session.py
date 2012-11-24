'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals
from webuntis import utils, objects, errors
result_wrapper = utils.result_wrapper

try:
    # Python 3
    import urllib.request as urlrequest
    import urllib.error as urlerrors
except ImportError:
    # Python 2
    import urllib2
    urlrequest = urlerrors = urllib2
import logging
import datetime


try:
    import json  # Python >= 2.6
except ImportError:
    import simplejson as json  # from dependency "simplejson"


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

        url = self._session.options['server'] + \
            '?school=' + \
            self._session.options['school']

        headers = {
            'User-Agent': self._session.options['useragent'],
            'Content-Type': 'application/json'
        }

        request_body = {
            'id': str(datetime.datetime.today()),
            'method': self._method,
            'params': self._params,
            'jsonrpc': '2.0'
        }

        if self._method != 'authenticate':
            if 'jsessionid' not in self._session.options:
                raise errors.NotLoggedInError(
                    'Don\'t have JSESSIONID. Did you already log out?')
            else:
                headers['Cookie'] = 'JSESSIONID=' + \
                    self._session.options['jsessionid']

        logging.debug('Making new request:')
        logging.debug('URL: ' + url)
        logging.debug('DATA: ' + str(request_body))

        result_body = self._send_request(
            url,
            json.dumps(request_body).encode(),
            headers
        )
        return self._parse_result(request_body, result_body)

    def _parse_result(self, request_body, result_body):
        '''A subfunction of _make_request that, given the decoded JSON result,
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
            self._parse_error_code(request_body, result_body)

    def _parse_error_code(self, request_body, result_body):
        '''A helper function for handling JSON error codes.'''
        logging.error(result_body)
        try:
            error = result_body['error']
            exc = self._errorcodes[error['code']](error['message'])
        except KeyError:
            exc = errors.RemoteError(
                ('Some JSON-RPC-ish error happened. Please report this to the '
                    'developer so he can implement a proper handling.'),
                str(result_body),
                str(request_body)
            )

        raise exc

    def _send_request(self, url, data, headers):
        '''A subfunction of _make_request, mostly because of mocking. Sends the
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
            logging.debug('Valid JSON found')
            logging.debug(result_data)
        except ValueError:
            raise errors.RemoteError('Invalid JSON', str(result))
        else:
            return result_data


class JSONRPCSession(object):
    '''Lower-level version of :py:class:`Session`. Do not use this.'''

    options = None
    '''Dictionary with configuration.'''

    def __init__(self, **kwargs):
        self.options = utils.FilterDict(utils.option_utils.options)
        options = {
            'server': None,
            'school': None,
            'useragent': None,
            'username': None,
            'password': None,
            'jsessionid': None,
            'login_repeat': 0
        }
        options.update(kwargs)
        self.options.update(options)

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

        :param suppress_errors: boolean, whether to suppress errors if we
            already were logged out.

        :raises: :py:class:`webuntis.errors.NotLoggedInError`
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
            del self.options['jsessionid']
        except KeyError:
            throw_errors()

    def login(self):
        '''Initializes an authentication, provided we have the credentials for
        it.

        :returns: The session. This is useful for jQuery-like command
            chaining::

                s = webuntis.Session(...).login()

        :raises: :py:class:`webuntis.errors.BadCredentialsError`
        :raises: :py:class:`webuntis.errors.AuthError`
        '''

        if 'username' not in self.options \
                or 'password' not in self.options:
            raise errors.AuthError('No login data specified.')

        logging.debug('Trying to authenticate with username/password...')
        logging.debug('Username: ' +
                      self.options['username'] +
                      ' Password: ' +
                      self.options['password'])
        res = self._request('authenticate', {
            'user': self.options['username'],
            'password': self.options['password'],
            'client': self.options['useragent']
        }, use_login_repeat=False)
        logging.debug(res)
        if 'sessionId' in res:
            logging.debug('Did get a jsessionid from the server:')
            self.options['jsessionid'] = res['sessionId']
            logging.debug(self.options['jsessionid'])
        else:
            raise errors.AuthError(
                'Something went wrong while authenticating',
                res
            )

        return self

    def _request(self, method, params=None, use_login_repeat=None):
        if use_login_repeat is None:
            use_login_repeat = (method not in ('logout', 'authenticate'))
        attempts_left = self.options['login_repeat'] if use_login_repeat else 0

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
                        'Tried to login several times, failed. Original method '
                        'was ' + method)
            else:
                return data

            attempts_left -= 1  # new round!


class Session(JSONRPCSession):
    '''The origin of everything you want to do with the WebUntis API. Can be
    used as a context-handler.
    
    Configuration options can be set with keyword arguments when initializing
    _:py:class:`Session`. Unless noted otherwise, they get saved in a
    dictionary located in the instance's ``options`` attribute and can be
    modified afterwards.

    :type username: str
    :param username: The username used for the API.

    :type password: str
    :param password: The password used for the API.

    :type jsessionid: str
    :param jsessionid: The current session key. Shouldn't be changed unless you
        know what you're doing.

    :type school: str
    :param school: A valid school name.

    :type server: str
    :param server: A host name, a URL, or a URL without path.

            >>> s = webuntis.Session(..., server='thalia.webuntis.com')
            >>> s.options['server']
            'http://thalia.webuntis.com/WebUntis/jsonrpc.do'
            >>> # notice that there's NO SLASH at the end!
            >>> s.options['server'] = 'https://thalia.webuntis.com'
            >>> s.options['server']
            'https://thalia.webuntis.com/WebUntis/jsonrpc.do'
            >>> s.options['server'] = 'https://thalia.webuntis.com/'
            >>> # because a slash gets interpreted as the full path to the API
            >>> # endpoint, which would crash during login
            >>> s.options['server']
            'http://thalia.webuntis.com/'
            >>> s.options['server'] = '!"$%/WebUntis/jsonrpc.do'
            Traceback blah blah something ValueError

    :type useragent: str
    :param useragent: A string containing a useragent. Please include useful
        information, such as an email address, for the server maintainer. Just
        like you would do with the HTTP useragents of bots.

    :param cachelen: Amount of API requests kept in cache. Default to ``20``.
        Isn't saved in the :py:attr:`options` dictionary and cannot be modified
        afterwards.  

    :param login_repeat: The amount of times `python-webuntis` should try to
        login when finding no or an expired session. Default to ``0``, meaning it
        won't do that.

    '''

    #: Contains the caching dictionary for requests.
    _cache = None

    def __init__(self, **options):
        try:
            cachelen = options['cachelen']
            del options['cachelen']
        except KeyError:
            cachelen = 20

        self._cache = utils.LruDict(maxlen=cachelen)

        JSONRPCSession.__init__(self, **options)

    def _make_cache_key(self, method, kwargs):
        '''A helper method that generates a hashable object out of a string and
        a dictionary.

        It doesn't use ``hash()`` or similar methods because it's neat that the
        keys are human-readable and enable us to trace back the origin of the
        key. Python does that anyway under the hood when using it as a
        dictionary key.
        '''

        return (method, frozenset((kwargs or {}).items()))

    @result_wrapper
    def departments(self):
        return objects.DepartmentList, 'getDepartments', {}

    @result_wrapper
    def holidays(self):
        return objects.HolidayList, 'getHolidays', {}

    @result_wrapper
    def klassen(self, schoolyear=None):
        params = {}
        if schoolyear:
            params['schoolyearId'] = int(schoolyear)

        return objects.KlassenList, 'getKlassen', params

    @result_wrapper
    def periods(self, start=None, end=None, **type_and_id):
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
            parameters['startDate'] = datetime_utils.format_date(start)
        if end:
            parameters['endDate'] = datetime_utils.format_date(end)

        return objects.PeriodList, 'getTimetable', parameters

    timetable = periods

    @result_wrapper
    def rooms(self):
        return objects.RoomList, 'getRooms', {}

    @result_wrapper
    def schoolyears(self): 
        return objects.SchoolyearList, 'getSchoolyears', {}

    @result_wrapper
    def subjects(self): 
        return objects.SubjectList, 'getSubjects', {}

    @result_wrapper
    def teachers(self):
        return objects.TeacherList, 'getTeachers', {}

    @result_wrapper
    def timegrid(self):
        return objects.TimeunitList, 'getTimegridUnits', {}

    timeunits = timegrid

    @result_wrapper
    def statusdata(self):
        return objects.StatusData, 'getStatusData', {}
