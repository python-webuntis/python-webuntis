'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

_logger = None


def log(level, message, *args, **kwargs):
    '''Log a message to the logger used. Written inside a function so it can be
    overridden if really neccessary.'''
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('webuntis')

    getattr(_logger, level)(message, *args, **kwargs)
