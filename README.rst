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

From latest commit in master
++++++++++++++++++++++++++++

::

    git clone git://github.com/untitaker/python-webuntis.git
    cd python-webuntis
    python setup.py install

If you want to remove the -dev flag in the version for whatever reason, replace the last line with::

    python setup.py release install

 
Unittests
=========

The unittests need `mock <http://www.voidspace.org.uk/python/mock/>`_ and `nose <https://nose.readthedocs.org/en/latest/index.html>`_ installed.

You can run the default testsuites using::

    $ nosetests

For the single testsuites and their descriptions, look at the docstrings of the modules in ``webuntis.tests``.
