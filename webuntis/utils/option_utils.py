'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals
import logging
import re
try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse


class Option(object):
    def __init__(self, value=None):
        self._validate(value)
        self.value = value

    def _get_value(self):
        return self.value

    def _validate(self, value):
        raise NotImplementedError


class WhateverOption(Option):
    def _validate(self, value):
        return True  # no idea how to validate this


class UserAgentOption(WhateverOption):
    '''User Agent that should be sent to the server. Available in the
    OptionStore as "useragent".'''
    pass


class SchoolOption(WhateverOption):
    '''School option, just a string without any validation. Available in the
    OptionStore as "school".'''
    pass


class CredentialsOption(Option):
    '''The credentials option has a dictionary which has username and
    password, or just the JSESSIONID. Available in the OptionStore as
    "credentials".
    '''
    def __init__(self, creds):
        if 'username' in creds and 'password' in creds \
           and creds['username'] and creds['password']:
            self.value = {
                'username': creds['username'],
                'password': creds['password']
            }
        elif 'jsessionid' in creds and creds['jsessionid']:
            self.value = {
                creds['jsessionid']
            }
        else:
            self.value = {}

    def _get_value(self):
        return self.value


class ServerOption(Option):
    '''The server option retrieves a hostname or an URL where the API calls
    should be sent to. Available in the OptionStore as "server".

    You can nearly pass everything a server. Things that can't be read out of
    the string you pass get stuffed with default values::
        >>> s.options['server'] = 'thalia.webuntis.com'
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

    '''
    def __init__(self, value=None):
        if type(value) == dict or not value:
            self.value = value  # either it's None or we have a dictionary
        else:
            if re.match(r'^http(s?)\:\/\/', value):
                url = value
            else:  # if we just have the domain
                logging.debug('The URL given doesn\'t seem to be a valid URL, \
                    just gonna prepend "http://"')

                # append the http prefix and hope for the best
                url = 'http://' + value

            urlobj = urlparse.urlparse(url)

            if urlobj.scheme and urlobj.netloc:
                if urlobj.path == '/':
                    # A bit weird, but it formats kinda nicely in the log.
                    # I am not logging line each, because other threads might
                    # interfere this and fuck everything up.
                    logging.warning('''You specified that the API endpoint
should be /. That is uncommon. If you didn't mean to do so, remove the slash at
the end of your "server" parameter.''')

                self.value = {
                    'protocol': urlobj.scheme,
                    'host':     urlobj.netloc,
                    'path':     urlobj.path or '/WebUntis/jsonrpc.do'
                }
            else:
                self.value = {}

    def _get_value(self):
        if self.value:
            return self.value['protocol'] + \
                '://' + \
                self.value['host'] + \
                self.value['path']
        else:
            return self.value


class OptionStore(object):
    '''Basically a dictionary with a validation system.

    It associates each key with a class. When a new key is added, an instance
    of the proper Option class will be created, with the value as an attribute
    and saved in the self.values dictionary'''
    options = {
        'server':      ServerOption,
        'school':      SchoolOption,
        'useragent':   UserAgentOption,
        'credentials': CredentialsOption
    }
    values = None

    '''This variable indicates if we have enough options set to make an API
    request. Will be updated through self.update_ready_for_request'''
    ready_for_request = False

    def __init__(self):
        self.values = {}
        self._update_ready_for_request()

    def _get_object(self, name):
        '''Retrieves an object from the dictionary, returning None if there's
        no entry yet and raises an AttributeError if there's not even a
        corresponding class to the key.

        Keyword arguments:
          - name: the key name
        '''
        if name in self.values:
            return self.values[name]
        elif name in self.options:
            return None  # new empty option
        else:
            raise AttributeError

    def update(self, *args):
        '''Populates the value dictionary with new Option instances

        Keyword arguments:
          - either a dictionary with key-value pairs that should
        be flashed onto the value dictionary, or
          - the first attribute being a key, the second one a value
        '''
        if len(args) == 2:
            values = {args[0]: args[1]}
        elif len(args) == 1:
            values = args[0]
        else:
            raise ValueError('You gave me the wrong amount of arguments')

        for name, value in values.items():
            if value is not None:
                self.values[name] = self.options[name](value)
            else:
                # Don't change this to del without thinking!
                # I specifically made it this way so there's no error when the
                # value doesn't exist yet.
                self.values[name] = None

        self._update_ready_for_request()

    def _update_ready_for_request(self):
        '''Updates self.ready_for_request
        '''
        required = ['school', 'server', 'credentials', 'useragent']
        available = [option for option in required if self[option]]
        logging.debug(available)
        self.ready_for_request = (available == required)

    def __getitem__(self, name):
        '''Basically a wrapper for get_object to retrieve values of a Option
        instance in an easy way
        '''
        obj = self._get_object(name)
        if obj is not None:  # check if we got a real Option subclass
            return obj._get_value()  # every Option subclass has this
        else:
            return None

    def __setitem__(self, name, value):
        self.update(name, value)
