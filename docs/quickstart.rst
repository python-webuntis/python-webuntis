===============
Getting Started
===============

Before we are getting started, there are a few things to know about WebUntis and its API:

.. note::

    - **You need an account for the API.** You can't access the API
      anonymously. It's designated that schools give each student a user
      account for the WebUntis server they're using. Many schools just make the
      timetable world-accessible though, preventing any use of the API. If you
      happen to be at such a school, you're a pitiful bastard.

    - **The API is read-only.** And there's nothing you can do about it.

    - **Different schools, different rules.** It is not neccessary that schools
      enter information about, for example, a teacher, in the correct format.
      It might happen that a school abuses the name field of a teacher to just
      write the teacher's initials in it. Testing is the only sane way out of
      this.

Are you still reading? Okay, let's install the webuntis package::

    pip install webuntis

Here's the example from the :doc:`Intro <index>` again::

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


So what does this do?

::

    s = webuntis.Session(
        server='webuntis.grupet.at:8080',
        username='api',
        password='api',
        school='demo_inf',
        useragent='WebUntis Test'
    )

*webuntis.Session* is a shortcut for :py:class:`webuntis.session.Session`. This class represents a new session on a WebUntis server, which is bound to a school. This means that you will have to create a new session if you want to read data from a different school, even if it's on the same server.

:py:class:`webuntis.session.Session` takes arguments such as the hostname, username and password. These options could also be imported later through the *options* object of your session, see :doc:`etc`.

But passing the credentials doesn't mean a session is started immediately. You have to do it manually::

    s.login()

This will raise an exception if you haven't provided the neccessary options (*i.e.* username, password, server).

So now that we're logged in, we can fetch some data. How about a list of all the classes of the school *demo_inf*? As the WebUntis software comes from Austria, these are called "klassen", which is German and means "classes". This name was probably choosen so there's no confusion between the classes of object-oriented programming languages and the classes that are actually important now.

Anyway, *python-webuntis* won't break that tradition::

    for klasse in s.klassen():
        print(klasse.name)

This code should be pretty self-explanatory. We get a list-like, iterable object when calling the :py:meth:`webuntis.session.Session.klassen`, a :py:class:`webuntis.objects.KlassenList` to be precise. This *KlassenList* contains multiple instances of :py:class:`webuntis.objects.KlassenObject`. An instance of this object has multiple attributes, one of them being *name*.

At last, you get logged out with this::

    s.logout()

You should always log out after doing your job, just like you should close a file after being done with it.
For such reasons, Python has the with-statement, which you also can use to log yourself out automatically::

    with webuntis.Session(...).login() as s:
        # work goes here
        s.klassen()

    # now you're logged out, even if your code halted with exceptions before.

Where to go from here?
======================

*  :doc:`session`

   This document provides a good starting point. It describes the only class you directly instantiate.

*  :doc:`objects`

   A complete overview of things you can do with the API

*  :doc:`etc`

   Some implementation details and neat tricks.
