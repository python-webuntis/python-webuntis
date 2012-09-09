'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals
from webuntis import utils, objects, errors
import re

try:
    import urllib.request as urlrequest
    import urllib.error as urlerrors
except ImportError:
    import urllib2 as urlrequest
    import urllib2 as urlerrors
import logging
import datetime


try:
    import json
except ImportError:
    import simplejson as json


class JSONRPCSession(object):
    '''Contains the functions for not much more than a simple JSON-RPC Session.
    Can be used as a context-handler.
    '''
    options = None

    def __init__(self, **kwargs):
        # The OptionStore is an extended dictionary, associating validators
        # and other helper methods with each key
        self.options = utils.OptionStore()
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
        self.logout()

    def logout(self, suppress_errors=False):
        '''
        Log out of session

        :param suppress_errors: boolean, whether to not raise an error if we
            already were logged out.
        '''
        #Send a JSON-RPC 'logout' method without parameters to log out
        if 'jsessionid' in self.options['credentials']:
            self._make_request('logout')
            del self.options['credentials']['jsessionid']
        elif not suppress_errors:
            raise errors.RemoteError('Already logged out!')

    def login(self):
        '''Initializes an authentication, provided we have the credentials for
        it.

        .. note::

            When authenticating, the username and password will be deleted from
            memory and only the jsessionid will be kept in the
            :py:class:`webuntis.utils.option_utils.OptionStore` instance.
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
            raise errors.AuthError('Something went wrong while \
                    authenticating', res)

        return self


    def _request(self, method, params=None):
        '''A wrapper for _make_request implementing a LRU Cache'''
        key = (method, hash(tuple(params or {})))
        
        if key not in self._cache:
            self._cache[key] = self._make_request(method, params)
        return self._cache[key]

    def _make_request(self, method, params=None):
        '''
        A method for sending a JSON-RPC request.

        :param method: The JSON-RPC method to be executed
        :type method: str

        :param params: JSON-RPC parameters to the method \
                (should be JSON serializable)
        :type params: dict
        '''

        if not self.options.ready_for_request:
            raise errors.AuthError('Not enough settings set: \
                school, server, useragent and username/password \
                or jsessionid')

        url = self.options['server']
        url += '?school=' + self.options['school']
        cookie_header = True
        if method == 'authenticate':
            cookie_header = False
        elif 'jsessionid' not in self.options['credentials']:
            raise errors.AuthError(
                'Don\'t have JSESSIONID. Did you already log out?'
            )

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
        except ValueError as e:
            logging.error('Error: Invalid JSON')
            logging.debug(res_str)
            raise errors.RemoteError('Invalid JSON')

        if res_data['id'] != req_data['id']:
            raise errors.RemoteError('Request id was not the same as \
                the one returned')
        elif 'result' in res_data:
            return res_data['result']
        else:
            logging.error(res_data)
            raise errors.RemoteError(
                'Some JSON-RPC-ish error happened',
                str(res_data),
                str(req_data)
            )


class Session(JSONRPCSession):
    '''Provides an abstraction layer above the JSON-RPC Instance.
    '''

    def __getattr__(self, name):
        '''Returns a callable which creates an instance (or reuses an old one)
        of the appropriate object-list class
        '''
        def get_objectlist(**kwargs):
            '''Returns the corrent objectclass after checking in the cache
            '''
            return objects.object_lists[name](session=self, kwargs=kwargs)

        if name in objects.object_lists:
            return get_objectlist
        else:
            raise AttributeError('There is no such datatype')
