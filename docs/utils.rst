=====
Utils
=====

Timetable Utils
===============

.. module:: webuntis.utils.timetable_utils

.. autofunction:: table

Option Utils
============

.. module:: webuntis.utils.option_utils

.. autoclass:: OptionStore

An instance of :py:class:`webuntis.utils.option_utils.OptionStore` is always created in a session instance at ``s.options``::

  >>> s = webuntis.Session()
  >>> s.options['credentials']  # a s.login() would fail.
  {}
  >>> s.options.credentials = {  # but we can define creds afterwards 
  ...     'username': 'rambo',
  ...     'password': 'lel'
  ... }
  >>> s.options['server'] = 'thalia.webuntis.com'  # change the server
  >>> s.options['server']
  'http://thalia.webuntis.com/WebUntis/jsonrpc.do'
  >>> s.options['useragent'] = 'FooBar'
  >>> s.options['school'] = 'Baumschule'
  >>> 
  >>> s.login()  # now that we have everything, we can login
  >>> s.options.credentials
  {
      'username': 'rambo',
      'password': 'lel',
      'jsessionid': '5N8934796V7568NB7U586N9B576'
  }
  >>> s.logout()  # and out
  >>> s.options.credentials
  {
      'username': 'rambo',
      'password': 'lel'
  }
  >>> s.login()  # and in ...
  >>> s.options.credentials
  {
      'username': 'rambo',
      'password': 'lel',
      'jsessionid': 'FDG748SB48S48R4SB84RS145VRB'
  }

  


The :py:meth:`webuntis.session.JSONRPCSession.authenticate` method saves the session id into the same dictionary where username and password are stored in.



All Options
+++++++++++

.. autoclass:: CredentialsOption

.. autoclass:: SchoolOption

.. autoclass:: ServerOption

.. autoclass:: UserAgentOption
