===
Etc
===

Timetable Utils
===============

.. module:: webuntis.utils.timetable_utils

.. autofunction:: table

Options
============

In an instance of :py:class:`webuntis.session.Session`, a dictionary-like object is created. It accepts the following keys:

  - *credentials*: A dictionary containing *username* and  *password*. Before the session is used, :py:meth:`webuntis.session.JSONRPCSession.login` must be called, in order to add a *jsessionid* key, which will be deleted when calling :py:meth:`webuntis.session.JSONRPCSession.logout`.
    
    In theory, you can obtain the jsessionid yourself and add it to the *credentials* dictionary. In this case, the other two keys are obviously not needed.

  - *school*: A string containing a valid school name.

  - *server*: A string containing a host name, a URL, or a URL without path::

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
        KeyError  

  - *useragent*: A string containing a useragent.
    
    Please include useful information, such as an email address, for the server maintainer. Just like you would do with the HTTP useragents of bots.

Caching
=======

python-webuntis implements a LRU Cache which caches the latest 20 requests per default. You can set the length with::

    s = webuntis.Session(..., cachelen=40)

Setting it to `0` obviously disables the cache.

