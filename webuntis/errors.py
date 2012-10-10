'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals


class Error(Exception):
    '''Superclass for all `python-webuntis`-specific errors, never gets raised
    directly. Positional arguments get joined with ``", "`` and get dumped into
    ``self.msg``'''

    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.msg = ', '.join(args)


class RemoteError(Error, IOError):
    '''There was some kind of error while interacting with the server.'''
    pass


class MethodNotFoundError(RemoteError):
    '''The JSON-RPC method was not found. This really should not occur.'''
    pass


class AuthError(RemoteError):
    '''Usually missing credentials, but also other problems while logging in
    are covered with this.'''
    pass


class BadCredentialsError(AuthError):
    '''Invalid username or password'''
    pass


class NotLoggedInError(AuthError):
    '''The session expired or we never logged in.'''
