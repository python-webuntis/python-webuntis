'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals
import re
import logging
try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse


def careless_parser(value):
    return value

def credentials_parser(creds):
    if 'username' in creds and 'password' in creds \
       and creds['username'] and creds['password']:
        return {
            'username': creds['username'],
            'password': creds['password']
        }
    elif 'jsessionid' in creds and creds['jsessionid']:
        return {
            creds['jsessionid']
        }
    else:
        return {}

def server_parser(value):
    if not value:
        return value  # either it's None or we have a dictionary

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

        return urlobj.scheme + \
                '://' + \
                urlobj.netloc + \
                (urlobj.path or '/WebUntis/jsonrpc')
    else:
        return None  # Doesn't seem like we have a value.

option_parsers = {
    'credentials': credentials_parser,
    'school': careless_parser,
    'server': server_parser,
    'useragent': careless_parser
}
