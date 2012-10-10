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


class JSONRPCSession(object):
    '''Lower-level version of :py:class:`Session`. Do not use this.'''

    options = None
    '''Contains a options dict upon initialization. See
    :py:class:`webuntis.utils.option_utils` for more information.'''

    _errorcodes = {
        -32601: errors.MethodNotFoundError,
        -8504: errors.BadCredentialsError,
        -8520: errors.NotLoggedInError
    }
    '''This lists the API-errorcodes python-webuntis is able to interpret,
    together with the exception that will be thrown.'''

    def __init__(self, **kwargs):
        # The OptionStore is an extended dictionary, associating validators
        # and other helper methods with each key
        self.options = utils.FilterDict(utils.option_utils.option_parsers)
        options = {
            'server': None,
            'school': None,
            'useragent': None,
            'username': None,
            'password': None,
            'jsessionid': None,
            'cachelen': 20
        }
        options.update(kwargs)

        self.options.update({
            'server': options['server'],
            'school': options['school'],
            'useragent': options['useragent'],
            'credentials': {
                'username': options['username'],
                'password': options['password'],
                'jsessionid': options['jsessionid']
            }
        })
        if options['cachelen'] > 0:
            self._cache = utils.LruDict(maxlen=options['cachelen'])

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
            self.options['credentials']['jsessionid']

            self._make_request('logout')
            del self.options['credentials']['jsessionid']
        except KeyError as e:
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

        if 'username' not in self.options['credentials'] \
                or 'password' not in self.options['credentials']:
            raise errors.AuthError('No login data specified.')

        logging.debug('Trying to authenticate with username/password...')
        logging.debug('Username: ' +
                      self.options['credentials']['username'] +
                      ' Password: ' +
                      self.options['credentials']['password'])
        res = self._make_request('authenticate', {
            'user': self.options['credentials']['username'],
            'password': self.options['credentials']['password'],
            'client': self.options['useragent']
        })
        logging.debug(res)
        if 'sessionId' in res:
            logging.debug('Did get a jsessionid from the server:')
            self.options['credentials']['jsessionid'] = res['sessionId']
            logging.debug(self.options['credentials']['jsessionid'])
        else:
            raise errors.AuthError(
                'Something went wrong while authenticating',
                res
            )

        return self

    def _request(self, method, params=None):
        '''A wrapper for _make_request implementing a LRU Cache'''
        key = (method, hash(tuple(params or {})))

        if key not in self._cache:
            self._cache[key] = self._make_request(method, params)
        return self._cache[key]

    def _handle_json_error(self, req_data, res_data):
        '''Given the request and response objects, this raises the appropriate
        exceptions.'''
        logging.error(res_data)
        try:
            error = res_data['error']
            your_weapon = self._errorcodes[error['code']](error['message'])
        except KeyError:
            your_weapon = errors.RemoteError(
                'Some JSON-RPC-ish error happened. Please report this to the \
developer so he can implement a proper handling.',
                str(res_data),
                str(req_data)
            )

        raise your_weapon

    def _make_request(self, method, params=None):
        '''
        A method for sending a JSON-RPC request.

        :param method: The JSON-RPC method to be executed
        :type method: str

        :param params: JSON-RPC parameters to the method (should be JSON
        serializable)
        :type params: dict
        '''

        url = self.options['server']
        url += '?school=' + self.options['school']
        cookie_header = True
        if method == 'authenticate':
            cookie_header = False
        elif 'jsessionid' not in self.options['credentials']:
            raise errors.AuthError('Don\'t have JSESSIONID. Did you already log out?')

        if not params:
            params = {}

        req_data = {
            'id': str(datetime.datetime.today()),
            'method': method,
            'params': params,
            'jsonrpc': '2.0'
        }

        req_data_json = json.dumps(req_data).encode()

        logging.debug('Making new request:')
        logging.debug('URL: ' + url)
        logging.debug(req_data_json)

        req = urlrequest.Request(
            url,
            req_data_json,
            {
                'User-Agent': self.options['useragent'],
                'Content-Type': 'application/json'
            }
        )
        if cookie_header:
            req.add_header(
                'Cookie',
                'JSESSIONID=' + self.options['credentials']['jsessionid']
            )

        # this will eventually raise errors, e.g. if there's an unexpected http
        # status code
        res = urlrequest.urlopen(req)

        res_str = res.read().decode('utf-8')

        try:
            res_data = json.loads(res_str)
            logging.debug('Valid JSON found')
            logging.debug(res_data)
        except ValueError:
            raise errors.RemoteError('Invalid JSON', str(res_str))

        if res_data['id'] != req_data['id']:
            raise errors.RemoteError('Request id was not the same as the one returned')
        elif 'result' in res_data:
            return res_data['result']
        else:
            self._handle_json_error(req_data, res_data)


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
