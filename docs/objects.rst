==================
Objects and Models
==================

.. note::
    
    The classes listed here never should be instantiated directly. Instead, use
    the wrapper methods on :py:class:`webuntis.session.Session` they provide,
    as shown in the class' documentation.

.. module:: webuntis.objects

Departments
===========
.. autoclass:: DepartmentList
  :members:
  :show-inheritance:

.. autoclass:: DepartmentObject
  :members:

Holidays
========
.. autoclass:: HolidayList
  :members:

.. autoclass:: HolidayObject
  :members:

Klassen
=======
.. autoclass:: KlassenList

.. autoclass:: KlassenObject
  :members:

Timetables and Periods
======================
.. autoclass:: PeriodList
  :members:

.. autoclass:: PeriodObject
  :members:

Rooms
=====
.. autoclass:: RoomList
  :members:

.. autoclass:: RoomObject
  :members:

Schoolyears
===========
.. autoclass:: SchoolyearList
  :members:

.. autoclass:: SchoolyearObject
  :members:

Subjects
========
.. autoclass:: SubjectList
  :members:

.. autoclass:: SubjectObject
  :members:

Teachers
========
.. autoclass:: TeacherList
  :members:

.. autoclass:: TeacherObject
  :members:

Timegrid and Timeunits
======================
.. autoclass:: TimeunitList
  :members:

.. autoclass:: TimeunitObject
  :members:

Lesson Types and Period Codes
==============================
.. autoclass:: StatusData
  :members:

.. autoclass:: ColorInfo
  :members:

============
Base Classes
============

The following classes are subclassed by the classes above:

.. autoclass:: Result
  :members:

.. autoclass:: ListResult
  :members:

.. autoclass:: ListItem
  :members:
