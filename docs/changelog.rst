=========
Changelog
=========

* work in progress:

    * Dropped Python 2.6 support, added Python up to 3.7

    * Code completion support for all objects

    * Added str() and reps() for all objects for easier debugging

    * Added new/missing API calls:

        * last_import_time
        * substitutions
        * timegrid_units
        * students
        * exam_types
        * exams
        * timetable_with_absences
        * class_reg_events

    * Code cleanup

* 0.1.9:

    * Add requests as a dependency and use it instead of urllib. Big security
      improvement due to certificate validation.

* 0.1.8:

    * Rewrote testsuite. Should work with both py.test and nosetest.

    * Removed support for Python 3.2 and 3.1. In earlier days i also was a bit
      sloppy with unicode strings vs bytestrings. That sloppiness has been
      partially fixed.

    * Instead of showing a default error message when the error code is not
      recognized, webuntis will now try to use the error message sent in the
      response. See 67d6fa2_.

.. _67d6fa2: https://github.com/python-webuntis/python-webuntis/commit/67d6fa21f7c199d89704d07dbba5219b0875b75e

* 0.1.7:

    * Bugfixes, as always.

    * :py:exc:`webuntis.errors.BadCredentialsError` now subclasses
      :py:exc:`ValueError`.

    * **Backwards incompatible:** Completely changed the API of
      :py:func:`webuntis.objects.PeriodList.to_table`, along with a rewrite of
      that function. Basically it doesn't accept a width parameter anymore, but
      sets of dates and times that should occur in the table. It now also pairs
      a :py:class:`datetime.date` object with a set of hours instead of the
      weekday number.

* 0.1.6:

    * Just documentation improvements (simplifying) and internal restructuring.

* 0.1.5:

    * Bugfixes

    * Major internal restructuring.

      * Now caching result objects instead of JSON

      * Added true hierarchial inheritance for Result objects.

    * New ``login_repeat`` option that automatically refreshes your session if
      neccessary. See :py:mod:`webuntis.Session`.

    * ``in`` operator is now supported by :py:class:`webuntis.objects.ListResult`

    * :py:meth:`webuntis.objects.ListResult.filter` now returns a
      :py:class:`webuntis.objects.ListResult` instead of a normal list.

    * **Backwards incompatible:** :py:class:`webuntis.objects.PeriodObject`
      used to have a ``type`` attribute that returned things like
      ``"cancelled"`` or ``"irregular"``. Due to me having read the API
      documentation too quickly, this is not like the ``type`` returned from
      the WebUntis API. So ``type`` is now renamed to ``code`` and the new
      ``type`` is something completely different.


* 0.1.4:

    * Updates to match changes in API.

    * Better docs.

    * Less bugs.

* 0.1.3:

    * Bugfix: Would crash at midnight times.

* 0.1.2:

    * Another bugfix wave.  
     
    * Switched to nosetests, make management of tests
      easier.  
      
    * Somehow i spelled "lesson" as "lession" throughout the whole
      module, in method names and elsewhere. This is fixed now, but it might
      break programs that are currently relying on that spelling error.

* 0.1.1:

    * Bugfixes
      
    * Added support for tox
      
    * Actual Python 2.6 support

* 0.1.0: First version of python-webuntis
