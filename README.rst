===============
python-webuntis
===============

Bindings for WebUntis API
=========================

::

    import webuntis

    s = webuntis.Session(
        username='api',
        password='api',
        server='webuntis.grupet.at:8080',
        school='demo_inf'
    ).login()

    for klasse in s.klassen():
        print(klasse.name)

`read more... <http://dev.unterwaditzer.net/python-webuntis/>`_

Installation
============

Latest version (this is the normal way)
+++++++++++++++++++++++++++++++++++++++

::

    pip install webuntis


Development
===========

Installing Development Dependencies
+++++++++++++++++++++++++++++++++++

A `virtualenv <http://www.virtualenv.org/>`_ is recommended::

    $ pip install -r dev_requirements.txt


Unittests
+++++++++

::

    $ python run-tests.py

For the single testsuites and their descriptions, look at the docstrings of the
modules in ``webuntis.tests``.
