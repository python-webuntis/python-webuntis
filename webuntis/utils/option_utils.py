'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals
import re
import logging
try:
    from urllib import parse as urlparse  # Python 3
except ImportError:
    import urlparse  # Python 2


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
            'jsessionid': creds['jsessionid']
        }
    else:
        return {}

def server_parser(url):
    if not url:
        return url  # either it's None or we have a dictionary

    if not re.match(r'^http(s?)\:\/\/', url):  # if we just have the hostname
        logging.debug('The URL given doesn\'t seem to be a valid URL, \
            just gonna prepend "http://"')

        # append the http prefix and hope for the best
        url = 'http://' + url

    urlobj = urlparse.urlparse(url)

    if not urlobj.scheme or not urlobj.netloc:
        # urlparse failed
        raise ValueError('Not a valid URL or hostname')

    if not re.match(r'^[a-zA-Z0-9\.\:-]+$', urlobj.netloc):
        # That's not even a valid hostname
        raise ValueError('Not a valid hostname')

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
        (urlobj.path or '/WebUntis/jsonrpc.do')

option_parsers = {
    'credentials': credentials_parser,
    'school': careless_parser,
    'server': server_parser,
    'useragent': careless_parser
}
