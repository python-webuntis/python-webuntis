'''
    This file is part of python-webuntis

    :copyright: (c) 2013 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
# Uncategorized utils go here

from __future__ import unicode_literals
from functools import wraps
from copy import deepcopy
from .third_party import OrderedDict


class lazyproperty(object):
    '''A read-only @property that is only evaluated once. Only usable on class
    instances' methods.

    Stolen from http://www.reddit.com/r/Python/comments/ejp25/cached_property_decorator_that_is_memory_friendly/
    '''
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:  # pragma: no cover
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result


class LruDict(OrderedDict):
    def __init__(self, maxlen=50):
        super(LruDict, self).__init__()
        self._maxlen = maxlen

    def __setitem__(self, key, value):
        self.pop(key, None)
        super(LruDict, self).__setitem__(key, value)
        while len(self.items()) > self._maxlen:
            self.popitem(last=False)


class SessionCache(LruDict):
    def clear(self, method=None):
        if method is None:
            LruDict.clear(self)
        else:
            for k in list(self):
                if k[0] == method:
                    del self[k]


class FilterDict(object):
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
    _contents = None

    def __init__(self, filters):
        self.filters = filters
        self._contents = {}

    def __getitem__(self, key):
        # check if we got a real Option subclass
        if key in self:
            # every Option subclass has this
            return self._contents[key]
        elif key in self.filters:
            raise KeyError('No value for key: ' + key)
        else:
            raise KeyError('No value or filter for key: ' + key)

    def __setitem__(self, key, value):
        if value is None:
            self._contents.pop(key, None)
            return

        new_value = self.filters[key](value)

        if new_value is None:
            self._contents.pop(key, None)
            return

        self._contents[key] = new_value

    def __delitem__(self, key):
        del self._contents[key]

    def update(self, new_pairs):
        for key, value in new_pairs.items():
            self[key] = value

    def __contains__(self, key):
        return (key in self._contents and
                self._contents[key] is not None)

    def __iter__(self):
        return iter(self._contents)


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
        from_cache = False
        if 'from_cache' in kwargs and kwargs['from_cache']:
            from_cache = True
            del kwargs['from_cache']

        result_class, jsonrpc_method, jsonrpc_args = func(self, **kwargs)
        key = cache_key(func.__name__, jsonrpc_args)

        if from_cache and key in self.cache:
            return self.cache[key]

        data = self._request(jsonrpc_method, jsonrpc_args)
        self.cache[key] = result = result_class(session=self, data=data)
        return result

    return inner


def cache_key(method, args=None):
    '''Get a hashable object given a string and a dictionary.'''
    if args is None:
        args = {}
    hash_args = frozenset(deepcopy(args).items())

    return (method, hash_args)
