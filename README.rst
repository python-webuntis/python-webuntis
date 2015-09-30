=====================================
This project is no longer maintained.
=====================================

I moved on and do no longer use it. See `the relevant ticket
<https://github.com/untitaker/python-webuntis/issues/3>`_.

|
|
|
|
|
|

===============
python-webuntis
===============

.. image:: https://travis-ci.org/untitaker/python-webuntis.png?branch=master
    :target: https://travis-ci.org/untitaker/python-webuntis

.. image:: https://coveralls.io/repos/untitaker/python-webuntis/badge.png
    :target: https://coveralls.io/r/untitaker/python-webuntis 


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

`read more... <http://python-webuntis.readthedocs.org/en/latest/>`_

Installation
============

Latest version (this is the normal way)
+++++++++++++++++++++++++++++++++++++++

::

    pip install webuntis
