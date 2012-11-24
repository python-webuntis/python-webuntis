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

from . import datetime_utils, option_utils, timetable_utils


class lazyproperty(object):
    '''A read-only @property that is only evaluated once.

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

    >>> options = FilterDict({
    ...    'foo': lambda x: 'whoopdeedoo'
    ... })
    >>>
    >>> options['foo'] = 'somethingelse'
    >>> options['foo']
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
        new_value = self.filters[key](value)
        if new_value is not None:
            dict.__setitem__(
                self,
                key,
                new_value
            )
        elif key in self:
            dict.__delitem__(self, key)

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

#class result_wrapper(object):
    #def __init__(self, func):
        #self._func = func
        #self.__doc__ = func.__doc__
        #self.__name__ = func.__name__

    #def __call__(self, session, **kwargs):
        #result_class, jsonrpc_method, jsonrpc_args = self._func(session, **kwargs)
        #key = session._make_cache_key(self.__name__, kwargs)

        #if key not in session._cache:
            #data = session._request(
                #jsonrpc_method,
                #jsonrpc_args
            #)
            #obj = result_class(session=session, data=data)

            #session._cache[key] = result = obj
        #else:
            #result = session._cache[key]
#        return result

def result_wrapper(func):
    @wraps(func)
    def inner(self, **kwargs):
        result_class, jsonrpc_method, jsonrpc_args = func(self, **kwargs)
        key = self._make_cache_key(func.__name__, kwargs)

        if key not in self._cache:
            data = self._request(
                jsonrpc_method,
                jsonrpc_args
            )
            obj = result_class(session=self, data=data)
            self._cache[key] = result = obj
        else:
            result = self._cache[key]

        return result

    return inner
