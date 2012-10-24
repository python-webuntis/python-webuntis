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
    def __init__(self, session, method, params=None):
        self._session = session
        self._method = method
        self._params = params or {}

    def request(self):
        data = None
        i = 0
        while data is None:
            i += 1
            try:
                data = self._make_request()
            except errors.NotLoggedInError as e:
                if self._session.options['login_repeat'] >= i:
                    self._session.logout(suppress_errors=True)
                    self._session.login()
                else:
                    raise e

        return data

    def _make_request(self):
        '''
        A method for sending a JSON-RPC request.

        :param method: The JSON-RPC method to be executed
        :type method: str

        :param params: JSON-RPC parameters to the method (should be JSON
        serializable)
        :type params: dict
        '''



        url = self._session.options['server'] + '?school=' + self._session.options['school']

        headers = {
            'User-Agent': self._session.options['useragent'],
            'Content-Type': 'application/json'
        }

        req_data = {
            'id': str(datetime.datetime.today()),
            'method': self._method,
            'params': self._params,
            'jsonrpc': '2.0'
        }

        if self._method != 'authenticate':
            if 'jsessionid' not in self._session.options:
                raise errors.NotLoggedInError('Don\'t have JSESSIONID. Did you already log out?')
            else:
                headers['Cookie'] = 'JSESSIONID=' + self._session.options['jsessionid']

        logging.debug('Making new request:')
        logging.debug('URL: ' + url)
        logging.debug('DATA: ' + str(req_data))

        res_data = self._send_request(url, json.dumps(req_data).encode(), headers)
        return self._handle_json(req_data, res_data)


    def _handle_json(self, request_body, result_body):
        '''A subfunction of _make_request that, given the decoded JSON result,
        handles the error codes or, if everything went well, returns the result
        attribute of it. The request data has to be given too for logging and
        ID validation.

        :param request_body: The not-yet-encoded body of the request sent.
        :param result_body: The decoded body of the result recieved.
        '''

        def handle_error_code():
            '''A helper function for handling JSON error codes.'''
            logging.error(res_data)
            try:
                error = res_data['error']
                exc = self._errorcodes[error['code']](error['message'])
            except KeyError:
                exc = errors.RemoteError(
                    ('Some JSON-RPC-ish error happened. Please report this to the '
                    'developer so he can implement a proper handling.'),
                    str(res_data),
                    str(req_data)
                )

            raise exc

        if request_body['id'] != result_body['id']:
            raise errors.RemoteError('Request ID was not the same one as returned.')

        try:
            return result_body['result']
        except KeyError:
            handle_error_code()

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

    _cache = None
    '''Contains the caching dictionary for requests.'''

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
            'cachelen': 20,  # Not implemented in LruDict
            'login_repeat': 0
        }
        options.update(kwargs)

        if options['cachelen'] > 0:
            self._cache = utils.LruDict(maxlen=options['cachelen'])

        del options['cachelen']

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
        # Send a JSON-RPC 'logout' method without parameters to log out
        try:
            # aborts if we don't have creds
            self.options['jsessionid']

            self._make_request('logout')
            del self.options['jsessionid']
        except KeyError:
            if not suppress_errors:
                raise errors.NotLoggedInError('We already were logged out.')

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
        res = self._make_request('authenticate', {
            'user': self.options['username'],
            'password': self.options['password'],
            'client': self.options['useragent']
        })
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

    def _request(self, method, params=None):
        '''A wrapper for :py:class:`JSONRPCRequest` using the LRU Cache'''

        if self._cache is None:
            return self._make_request(method, params)
        else:
            key = (method, hash(tuple(params or {})))
            if key not in self._cache:
                self._cache[key] = self._make_request(method, params)
            return self._cache[key]

    def _make_request(self, method, params=None):
        return JSONRPCRequest(self, method, params).request()


    _errorcodes = {
        -32601: errors.MethodNotFoundError,
        -8504: errors.BadCredentialsError,
        -8520: errors.NotLoggedInError
    }
    '''This lists the API-errorcodes python-webuntis is able to interpret,
    together with the exception that will be thrown.'''






class Session(JSONRPCSession):
    '''The origin of everything you want to do with the WebUntis API. Can be
    used as a context-handler.'''

    def __getattr__(self, name):
        '''Returns a callable which creates an instance (or reuses an old one)
        of the appropriate object-list class
        '''
        def get_result_object(**kwargs):
            obj = objects.result_objects[name](session=self, kwargs=kwargs)
            obj.store_data()
            return obj

        if name in objects.result_objects:
            return get_result_object
        else:
            raise AttributeError(name)
