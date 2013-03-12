===============
Getting Started
===============

Before we are getting started, there are a few things to know about WebUntis
and its API:

.. note::

    - **You need an account for the API.** You can't access the API
      anonymously. It's designated that schools give each student a user
      account for the WebUntis server they're using. Many schools just make the
      timetable world-accessible though, preventing any use of the API. If you
      happen to be at such a school, you're a pitiful bastard.

    - **The API is read-only.** And there's nothing you can do about it.

    - **The API documentation does not explain the purpose of some methods.**
      So i can't do a much better job at it.

    - **Different schools, different rules.** It is not neccessary that schools
      enter information about, for example, a teacher, in the correct format.
      It might happen that a school abuses the name field of a teacher to just
      write the teacher's initials in it. The timezone of the dates and times
      is also dependent on how your school inserted those. Testing is the only
      sane way out of this.

    - **Don't like something about the usage of my package?** Please, `let me
      know! <https://github.com/untitaker/python-webuntis/issues/new>`_ I don't
      want python-webuntis to become as inconsistent and *weird* as the API it
      is wrapping.

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

    # a minimal example, these parameters are absolutely neccessary
    s = webuntis.Session(
        server='webuntis.grupet.at:8080',
        username='api',
        password='api',
        school='demo_inf',
        useragent='WebUntis Test'
    )

:py:class:`webuntis.Session` represents a new session on a WebUntis server,
which is bound to a school. This means that you will have to create a new
session if you want to read data from a different school, even if it's on the
same server.

But passing the credentials in doesn't mean a session is started immediately.
You have to do it manually::

    s.login()

This will raise an exception if you haven't provided the neccessary
configuration (*i.e.* username, password, server, useragent, school).

So now that we're logged in, we can fetch some data. How about a list of all
the classes of the school *demo_inf*? As the WebUntis software comes from
Austria, these are called "klassen", which is German and means "classes". This
name was probably choosen so there's no confusion between the classes of
object-oriented programming languages and the classes that are actually
important now.

Anyway, *python-webuntis* won't break that tradition::

    for klasse in s.klassen():
        print(klasse.name)

We get a list-like, iterable object when calling
:py:meth:`webuntis.Session.klassen`, a :py:class:`webuntis.objects.KlassenList`
to be precise. This *KlassenList* contains multiple instances of
:py:class:`webuntis.objects.KlassenObject`. An instance of this object has
multiple attributes, one of them being *name*.

At last, you get logged out with this::

    s.logout()

You should always log out after doing your job, just like you should close a
file after being done with it. For such reasons, Python has the with-statement,
which you also can use to log yourself out automatically::

    with webuntis.Session(...).login() as s:
        # work goes here

    # now you're logged out, even if your code halted with exceptions before.

Where to go from here?
======================

:doc:`session` describes the ``Session`` class, which is the only class you
will ever directly get in touch with.
