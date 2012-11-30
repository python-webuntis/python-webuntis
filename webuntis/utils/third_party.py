'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

try:
    from collections import OrderedDict  # Python >= 2.7
except ImportError:
    from ordereddict import OrderedDict  # from dependency "ordereddict"

try:
    import json  # Python >= 2.6
except ImportError:
    import simplejson as json  # from dependency "simplejson"

try:
    # Python 3
    import urllib.request as urlrequest
    import urllib.error as urlerrors
    import urllib.parse as urlparse
except ImportError:
    # Python 2
    import urllib2
    import urlparse
    urlrequest = urlerrors = urllib2
