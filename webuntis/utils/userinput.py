'''
    This file is part of python-webuntis

    :copyright: (c) 2013 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
import re
from .logger import log
from .third_party import urlparse


def server(url):
    if not re.match(r'^http(s?)\:\/\/', url):  # if we just have the hostname
        log('debug', 'The URL given doesn\'t seem to be a valid URL, just '
                     'gonna prepend "https://"')

        # append the http prefix and hope for the best
        url = 'https://' + url

    urlobj = urlparse.urlparse(url)

    if not urlobj.scheme or not urlobj.netloc:
        # urlparse failed
        raise ValueError('Not a valid URL or hostname')

    if not re.match(r'^[a-zA-Z0-9\.\:\-_]+$', urlobj.netloc):
        # That's not even a valid hostname
        raise ValueError('Not a valid hostname')

    if urlobj.path == '/':
        log('warning', 'You specified that the API endpoint should be "/".'
                       'That is uncommon. If you didn\'t mean to do so,'
                       'remove the slash at the end of your "server"'
                       'parameter.')

    return urlobj.scheme + \
        u'://' + \
        urlobj.netloc + \
        (urlobj.path or u'/WebUntis/jsonrpc.do')


def string(value):
    '''Make the string unicode'''
    if isinstance(value, unicode_string):
        return value
    return value.decode('ascii')

config_keys = {
    'username': string,
    'password': string,
    'jsessionid': string,
    'school': string,
    'server': server,
    'useragent': string,
    'login_repeat': int,
    '_http_session': None
}

try:
    unicode_string = unicode
    bytestring = str
except NameError:
    unicode_string = str
    bytestring = bytes
