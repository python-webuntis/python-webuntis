============
Introduction
============

Bindings for WebUntis
=====================

`python-webuntis <https://github.com/untitaker/python-webuntis>`_ is a handy library which provides a thin abstraction layer on top of the API of `WebUntis <http://grupet.at>`_, a timetable system used for schools all around Europe. It is compatible with Python 3 and Python 2::

    import webuntis

    s = webuntis.Session(
        server='webuntis.grupet.at:8080',
        username='api',
        password='api',
        school='demo_inf',
        useragent='WebUntis Test'
    )

    s.login()

    for klasse in klassen:
        print(klasse.name)

    s.logout()


Output::

    1A
    2A
    3A
    [...]



:doc:`Read More <quickstart>`

.. toctree::
 :hidden:

 quickstart

Index
=====
.. toctree::
  :maxdepth: 2

  quickstart
  session
  objects
  etc
  changelog
  license
