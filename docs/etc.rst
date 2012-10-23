===
Etc
===

Here is random stuff that doesn't fit anywhere else.

.. module:: webuntis.utils

Timetable Utils
===============

.. module:: webuntis.utils.timetable_utils

.. autofunction:: table

Options
============

.. module:: webuntis.utils.option_utils

Configuration options can be set with keyword arguments when initializing
_:py:class:`webuntis.session.Session`. Unless noted otherwise, they get saved
in a dictionary located in the instance's ``options`` attribute and can be
modified afterwards.

  - ``credentials``: A dictionary containing ``username`` and  ``password``. Before
    the session is used, :py:meth:`webuntis.session.JSONRPCSession.login` must
    be called, in order to add a ``jsessionid`` key, which will be deleted when
    calling :py:meth:`webuntis.session.JSONRPCSession.logout`.
    
    In theory, you can obtain the jsessionid yourself and add it to the
    ``credentials`` dictionary. In this case, the other two keys are obviously
    not needed.

  - ``school``: A string containing a valid school name.

  - ``server``: A string containing a host name, a URL, or a URL without path::

        >>> s.options['server'] = 'thalia.webuntis.com'
        >>> s.options['server']
        'http://thalia.webuntis.com/WebUntis/jsonrpc.do'
        >>> # notice that there's NO SLASH at the end!
        >>> s.options['server'] = 'https://thalia.webuntis.com'
        >>> s.options['server']
        'https://thalia.webuntis.com/WebUntis/jsonrpc.do'
        >>> s.options['server'] = 'https://thalia.webuntis.com/'
        >>> # because a slash gets interpreted as the full path to the API
        >>> # endpoint, which would crash during login
        >>> s.options['server']
        'http://thalia.webuntis.com/'
        >>> s.options['server'] = '!"$%/WebUntis/jsonrpc.do'
        Traceback blah blah something ValueError

  - ``useragent``: A string containing a useragent.
    
    Please include useful information, such as an email address, for the server
    maintainer. Just like you would do with the HTTP useragents of bots.

  - ``cachelen``: Amount of API requests kept in cache. Default to 20. Isn't
    saved in the ``options`` object and cannot be modified afterwards.

  - ``keep_session_alive``: Boolean, whether or not to re-login when the
    session has expired. Enabled by default.

Errors and Exceptions
=====================

`python-webuntis` tries to cover as many error codes recieved by the API as possible.

.. automodule:: webuntis.errors
    :members:
    :show-inheritance:
    :member-order: bysource
