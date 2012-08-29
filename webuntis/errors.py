'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals


class Error(Exception):
    pass


class RemoteError(Error, IOError):
    pass


class AuthError(RemoteError):
    pass
