'''
    This file is part of python-webuntis

    :copyright: (c) 2013 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''


class Error(Exception):
    '''Superclass for all `python-webuntis`-specific errors, never gets raised
    directly.'''


class RemoteError(Error, IOError):
    '''There was some kind of error while interacting with the server.'''
    pass


class MethodNotFoundError(RemoteError):
    '''The JSON-RPC method was not found. This really should not occur.'''
    pass


class AuthError(RemoteError):
    '''Errors while logging in.'''
    pass


class BadCredentialsError(AuthError, ValueError):
    '''Invalid or missing username or password.'''
    pass


class NotLoggedInError(AuthError):
    '''The session expired or we never logged in.'''
