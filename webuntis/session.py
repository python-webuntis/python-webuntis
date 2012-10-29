'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals
from webuntis import utils, objects, errors

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
    '''Contains a options dict upon initialization. See
    :py:class:`webuntis.utils.option_utils` for more information.
    '''

    def __init__(self, **kwargs):
        # The OptionStore is an extended dictionary, associating validators
        # and other helper methods with each key
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
            except errors.NotLoggedInError as e:
                if attempts_left > 0:
                    self.logout(suppress_errors=True)
                    self.login()
                else:
                    raise errors.NotLoggedInError('Tried to login several times, failed. Original method was ' + method)
            else:
                return data

            attempts_left -= 1  # new round!



class Session(JSONRPCSession):
    '''The origin of everything you want to do with the WebUntis API. Can be
    used as a context-handler.'''

    _cache = None
    '''Contains the caching dictionary for requests.'''

    def __init__(self, **options):
        try:
            cachelen = options['cachelen']
            del options['cachelen']
        except KeyError:
            cachelen = 20

        if cachelen > 0:
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

    def __getattr__(self, name):
        '''Returns a callable which creates an instance (or reuses an old one)
        of the appropriate object-list class
        '''
        def result_object_wrapper(**kwargs):
            key = self._make_cache_key(name, kwargs)
            def get_result_object():
                obj = objects.result_objects[name](session=self, kwargs=kwargs)
                obj.store_data()
                return obj

            if self._cache is None:
                return get_result_object()

            if key not in self._cache:
                self._cache[key] = get_result_object()
            return self._cache[key]

        if name in objects.result_objects:
            return result_object_wrapper
        else:
            raise AttributeError(name)
