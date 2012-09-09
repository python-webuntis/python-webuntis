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

For the full documentation, check out `the documentation <http://dev.unterwaditzer.net/python-webuntis/>`_.
