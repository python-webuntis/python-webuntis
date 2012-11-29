'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals
from functools import wraps

try:
    unicode
except NameError:
    # Python 3
    basestring = unicode = str

try:
    from collections import OrderedDict  # Python >= 2.7
except ImportError:
    from ordereddict import OrderedDict  # from dependency "ordereddict"

from . import datetime_utils, timetable_utils
from .config_utils import config_keys


class lazyproperty(object):
    '''A read-only @property that is only evaluated once. Only usable on class instances' methods.

    Stolen from http://www.reddit.com/r/Python/comments/ejp25/cached_property_decorator_that_is_memory_friendly/
    '''
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result


class LruDict(OrderedDict):
    def __init__(self, maxlen=50):
        super(LruDict, self).__init__()
        self._maxlen = maxlen

    def __setitem__(self, key, value):
        super(LruDict, self).__setitem__(key, value)
        while len(self.items()) > self._maxlen:
            self.popitem(last=False)


class FilterDict(dict):
    '''A dictionary which passes new values to a function found at the
    corresponding key in self.filters

    :param filters: A dictionary containing functions. If a new key is set into
    an instance of FilterDict, the filter dictionary will be consulted to
    filter the value with a function.

    >>> config = FilterDict({
    ...    'foo': lambda x: 'whoopdeedoo'
    ... })
    >>>
    >>> config['foo'] = 'somethingelse'
    >>> config['foo']
    'whoopdeedoo'

    '''
    filters = None

    def __init__(self, filters):
        self.filters = filters

    def __getitem__(self, name):
        # check if we got a real Option subclass
        if name in self and dict.__getitem__(self, name) is not None:
            # every Option subclass has this
            return dict.__getitem__(self, name)
        elif name in self.filters:
            raise KeyError('No value for key: ' + name)
        else:
            raise KeyError('No value or filter for key: ' + name)

    def __setitem__(self, key, value):
        if value is None:
            if key in self:
                del self[key]
            return

        new_value = self.filters[key](value)

        if new_value is None:
            if key in self:
                del self[key]
            return

        dict.__setitem__(self, key, new_value)

    def update(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            self.__setitem__(key, value)


def is_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return not isinstance(obj, basestring)


def result_wrapper(func):
    '''A decorator for the session methods that return result objects. The
    decorated function has to return a tuple with the result class to
    instantiate, a JSON-RPC method and its parameters.  This decorator fetches
    the data with the JSON-RPC method and parameters and returns an instance of
    the result class the inner function returned (and saves it in the session
    cache).
    '''
    @wraps(func)
    def inner(self, **kwargs):
        result_class, jsonrpc_method, jsonrpc_args = func(self, **kwargs)
        key = SessionCacheKey(func.__name__, kwargs)

        if key not in self.cache:
            data = self._request(
                jsonrpc_method,
                jsonrpc_args
            )
            obj = result_class(session=self, data=data)
            self.cache[key] = result = obj
        else:
            result = self.cache[key]

        return result

    return inner


class SessionCacheKey(object):
    '''A hashable object whose primary purpose is to get used as a dictionary
    key.'''
    def __init__(self, method, kwargs):
        self.method = method
        self.kwargs = kwargs

    def _cache_key(self):
        return (self.method, frozenset((self.kwargs or {}).items()))

    def __hash__(self):
        return hash(self._cache_key())

    def __eq__(self, other):
        return type(other) == type(self) and hash(other) == hash(self)

    def __repr__(self):
        return 'webuntis.utils.%s(%s)' % (
            self.__class__.__name__,
            ', '.join((repr(self.method), repr(self.kwargs)))
        )
