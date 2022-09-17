
===============
python-webuntis
===============

.. image:: https://img.shields.io/pypi/v/webuntis
    :target: https://pypi.org/project/webuntis/

.. image:: https://img.shields.io/pypi/pyversions/webuntis
    :target: https://pypi.org/project/webuntis/

.. image:: https://img.shields.io/pypi/l/webuntis
    :target: https://pypi.org/project/webuntis/

.. image:: https://travis-ci.org/AugustH/python-webuntis.png?branch=master
    :target: https://travis-ci.org/maphy-psd/python-webuntis

.. image:: https://coveralls.io/repos/github/maphy-psd/python-webuntis/badge.svg?branch=master
    :target: https://coveralls.io/r/maphy-psd/python-webuntis

.. image:: https://pepy.tech/badge/webuntis
    :target: https://pepy.tech/project/webuntis

.. image:: https://pepy.tech/badge/webuntis/month
    :target: https://pepy.tech/project/webuntis



Bindings for WebUntis API
=========================

::

    import webuntis

    with webuntis.Session(
        username='name',
        password='passwd',
        server='webuntis.grupet.at:8080',
        school='demo_inf',
        useragent='WebUntis Test'
    ).login() as s:
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


This project is now maintained again. It was originally written by `untitaker <https://github.com/untitaker>`_
==============================================================================================================
