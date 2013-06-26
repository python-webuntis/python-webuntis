=====================
Bindings for WebUntis
=====================

:Author: `Markus Unterwaditzer <http://unterwaditzer.net>`_
:Version: |release|
:Project Page: `on GitHub <https://github.com/untitaker/python-webuntis>`_
:License: :doc:`new-style BSD <license>`

`python-webuntis` is a package for the API of `WebUntis
<http://www.grupet.at>`_, a timetable system used for schools all around
Europe. It is compatible with Python >= 2.6 and Python >= 3.3::

    import webuntis

    s = webuntis.Session(
        server='webuntis.grupet.at:8080',
        username='api',
        password='api',
        school='demo_inf',
        useragent='WebUntis Test'
    )

    s.login()

    for klasse in s.klassen():
        print(klasse.name)

    s.logout()


Output::

    1A
    2A
    3A
    [...]



:doc:`Read More <quickstart>`

Index
=====
.. toctree::
  :maxdepth: 2

  quickstart
  session
  objects
  exceptions
  changelog
  license
