=====================================
This project is now maintained again. It was originally written by `untitaker <https://github.com/untitaker>`_
=====================================
|
|
|

===============
python-webuntis
===============

.. image:: https://travis-ci.org/maphy-psd/python-webuntis.png?branch=master
    :target: https://travis-ci.org/maphy-psd/python-webuntis

.. image:: https://coveralls.io/repos/github/maphy-psd/python-webuntis/badge.svg?branch=master
    :target: https://coveralls.io/r/maphy-psd/python-webuntis

Bindings for WebUntis API
=========================

::

    import webuntis

    s = webuntis.Session(
        username='api',
        password='api',
        server='webuntis.grupet.at:8080',
        school='demo_inf',
        useragent='WebUntis Test'
    ).login()

    for klasse in s.klassen():
        print(klasse.name)

`read more... <http://python-webuntis.readthedocs.org/en/latest/>`_

Installation
============

::

    pip install webuntis

License
=======

``python-webuntis`` is released under the 3-clause BSD license, see ``LICENSE``
for details.
