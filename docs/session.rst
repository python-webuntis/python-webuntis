=======
Session
=======

.. currentmodule:: webuntis.session

.. autoclass:: JSONRPCSession
  :members:

.. autoclass:: Session

  .. method:: departments
    
     Returns a new instance of :py:class:`webuntis.objects.departments.DepartmentList`.

  .. method:: holidays

     Returns a new instance of :py:class:`webuntis.objects.holidays.HolidayList`.

  .. method:: klassen

     Returns a new instance of :py:class:`webuntis.objects.klassen.KlassenList`.

  .. method:: schoolyears

     Returns a new instance of :py:class:`webuntis.objects.schoolyears.SchoolyearList`.

  .. method:: subjects

     Returns a new instance of :py:class:`webuntis.objects.subjects.SubjectList`.

  .. method:: teachers

     Returns a new instance of :py:class:`webuntis.objects.teachers.TeacherList`.

  .. method:: timeunits

     Returns a new instance of :py:class:`webuntis.objects.teachers.TeacherList`.

  .. method:: timegrid

     Does exactly the same as :py:meth:`timeunits`.

  .. method:: periods

     Returns a new instance of :py:class:`webuntis.objects.periods.PeriodList`.

  .. method:: timetable

     Does exactly the same as :py:meth:`periods`.
