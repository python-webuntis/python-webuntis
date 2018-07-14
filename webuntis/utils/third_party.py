"""
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
"""

from collections import OrderedDict  # Python >= 2.7
import json  # Python >= 2.6

try:
    # Python 3
    import urllib.parse as urlparse  # pragma: no cover
except ImportError:
    # Python 2
    import urlparse
