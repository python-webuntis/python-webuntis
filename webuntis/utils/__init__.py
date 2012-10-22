'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals

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
        if name in self and dict.__getitem__(self, name):
            # every Option subclass has this
            return dict.__getitem__(self, name)
        elif name in self.filters:
            raise KeyError('No value for key: ' + name)
        else:
            raise KeyError('No value or filter for key: ' + name)

    def __setitem__(self, key, value):
        new_value = self.filters[key](value)
        if new_value:
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
