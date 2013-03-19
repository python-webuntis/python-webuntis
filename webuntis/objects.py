'''
    This file is part of python-webuntis

    :copyright: (c) 2013 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals
from webuntis.utils import datetime_utils, lazyproperty, \
    timetable_utils


class Result(object):
    '''Base class used to represent most API objects.

    :param data: Usually JSON data that should be represented.

                 In the case of :py:class:`ListResult`, however, it might also
                 be a list of JSON mixed with :py:class:`ListItem` objects.

    :param parent: (optional) A result object this result should be the child
                    of. If given, the session will be inherited.

    :param session: Mandatory if ``parent`` is not supplied. Overrides the
                    parent's inherited session.

    '''

    _parent = None
    _session = None
    _data = None

    def __init__(self, data, parent=None, session=None):
        if not isinstance(parent, Result) and parent is not None:
            raise TypeError('If provided, parent must be an instance of '
                            'webuntis.objects.Result.')

        if bool(parent is None) == bool(session is None):
            raise TypeError('Either parent or session has to be provided.')

        self._session = session or parent._session
        self._parent = parent
        self._data = data

    @lazyproperty
    def id(self):
        '''The ID of this element.

        An ID is needed for the object to be hashable. Therefore a result
        may bring its own implementation of this method even though the
        original API response didn't contain any ID.'''
        return self._data['id'] if 'id' in self._data else None

    def __int__(self):
        '''This is useful if the users pass a ListItem when a numerical ID
        is expected, so we just can put the thing through int(), regardless of
        what type it is.'''
        return self.id

    def __hash__(self):
        return hash('%s#%i' % (self.__class__.__name__, self.id))

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return hash(self) == hash(other)


class ListItem(Result):
    '''ListItems represent an item in a
    :py:class:`Result`. They don\'t contain methods to
    retrieve data.'''


class ListResult(Result):
    '''A list-like version of :py:class:`Result` that takes a list and returns
    a list of objects, containing a list value each.

        '''

    # When the Result returns an array, this is very useful. Every item of that
    # array will be fed to an instance of self._itemclass, with the session and
    # the array item as initialization arguments.

    #: the class which should be used to instantiate an array item.
    _itemclass = ListItem

    def filter(self, **criterions):
        '''
        Return a list of all objects, filtered by attributes::

            foo = s.klassen().filter(id=1)  # is kind-of the same as
            foo = [kl for kl in s.klassen() if kl.id == 1]

            # We can also use sets to match multiple values.
            bar = s.klassen().filter(name={'1A', '2A', '3A', '4A'})
            # is kind-of the same as
            bar = [kl for kl in s.klassen()
                   if kl.id in {'1A', '2A', '3A', '4A'}]

            # Since ``filter`` returns a ListResult itself too, we can chain
            # multiple calls together:
            bar = s.klassen().filter(id=4, name='7A')  # is the same as
            bar = s.klassen().filter(id=4).filter(name='7A')

        :py:meth:`filter` is also used when using the ``in`` operator on a
        :py:class:`ListResult`::

            we_have_it = {'name': '6A'} in s.klassen()  # same as
            we_have_it = bool(s.klassen().filter(name='6A'))


        .. note::
            This is only available because it looks nicer than list
            comprehensions or generator expressions. Depending on your usecase
            alternatives to this method may be faster.

        '''
        criterions = list(criterions.items())

        def meets_criterions(item):
            '''Returns true if the item meets the criterions'''
            for key, value in criterions:
                # if the attribute value isn't one we're looking for
                attribute = getattr(item, key)
                if attribute == value:
                    continue
                elif isinstance(value, set) and attribute in value:
                    continue
                else:
                    return False

            return True

        return type(self)(
            parent=self,
            data=[item for item in self if meets_criterions(item)]
        )

    def __contains__(self, criterion):
        return bool(self.filter(**criterion))

    def __getitem__(self, i):
        '''Makes the object iterable and behave like a list'''
        data = self._data[i]  # fails if there is no such item

        if type(data) is not self._itemclass:
            data = self._data[i] = self._itemclass(
                parent=self,
                data=data
            )

        return data

    def __len__(self):
        '''Return the length of the items'''
        return len(self._data)


class DepartmentObject(ListItem):
    '''Represents a department'''

    @lazyproperty
    def name(self):
        '''short name such as *R1A*'''
        return self._data['name']

    @lazyproperty
    def long_name(self):
        '''Long name, such as *Raum Erste A*. Not predictable.'''
        return self._data['longName']


class DepartmentList(ListResult):
    '''A list of departments, in form of :py:class:`DepartmentObject`
    instances.'''
    _itemclass = DepartmentObject


class HolidayObject(ListItem):
    '''Represents a single holiday.'''

    @lazyproperty
    def start(self):
        '''The start date of the holiday, as a datetime object.'''
        return datetime_utils.parse_date(self._data['startDate'])

    @lazyproperty
    def end(self):
        '''The end of the holiday'''
        return datetime_utils.parse_date(self._data['endDate'])

    @lazyproperty
    def name(self):
        '''Name, such as *Nationalfeiertag*.'''
        return self._data['longName']

    @lazyproperty
    def short_name(self):
        '''Abbreviated form of the name'''
        return self._data['name']


class HolidayList(ListResult):
    '''A list of holidays, in form of :py:class:`HolidayObject`
    instances.'''
    _itemclass = HolidayObject


class KlassenObject(ListItem):
    '''Represents a school class.'''

    @lazyproperty
    def name(self):
        '''Name of class'''
        return self._data['name']

    @lazyproperty
    def long_name(self):
        '''Long name of class'''
        return self._data['longName']


class KlassenList(ListResult):
    '''A list of school classes, in form of :py:class:`KlassenObject`
    instances.'''
    _itemclass = KlassenObject


class PeriodObject(ListItem):
    '''Represents a time range, where lessons/subjects may be held.'''

    @lazyproperty
    def start(self):
        '''The start date/time of the period, as datetime object.'''

        return datetime_utils.parse_datetime(
            self._data['date'],
            self._data['startTime']
        )

    @lazyproperty
    def end(self):
        '''The end date/time of the period.'''

        return datetime_utils.parse_datetime(
            self._data['date'],
            self._data['endTime']
        )

    @lazyproperty
    def klassen(self):
        '''A :py:class:`KlassenList` containing the classes which are attending
        this period.'''

        return self._session.klassen(from_cache=True).filter(
            id=set([kl['id'] for kl in self._data['kl']])
        )

    @lazyproperty
    def teachers(self):
        '''A list of :py:class:`TeacherObject` instances,
        which are attending this period.'''

        return self._session.teachers(from_cache=True).filter(
            id=set([te['id'] for te in self._data['te']])
        )

    @lazyproperty
    def subjects(self):
        '''A :py:class:`SubjectList` containing the subjects which are topic of
        this period. This is not used for things like multiple language lessons
        (*e.g.* Latin, Spanish, French) -- each of those will get placed in
        their own period.'''

        return self._session.subjects(from_cache=True).filter(
            id=set([su['id'] for su in self._data['su']])
        )

    @lazyproperty
    def rooms(self):
        '''The rooms (:py:class:`RoomList`) where this period is taking place
        at. This also is not used for multiple lessons, but rather for a single
        lesson that is actually occuring at multiple locations (?).'''

        return self._session.rooms(from_cache=True).filter(
            id=set([ro['id'] for ro in self._data['ro']])
        )

    @lazyproperty
    def code(self):
        '''May be:

          - ``None`` -- There's nothing special about this period.
          - ``"cancelled"`` -- Cancelled
          - ``"irregular"`` -- Substitution/"Supplierung"/Not planned event
        '''

        if 'code' not in self._data:
            return None
        else:
            return self._data['code'] or None

    @lazyproperty
    def type(self):
        '''May be:

          - ``"ls"`` -- Normal lesson
          - ``"oh"`` -- Office hour
          - ``"sb"`` -- Standby
          - ``"bs"`` -- Break Supervision
          - ``"ex"`` -- Examination
        '''

        return (self._data['lstype'] if 'lstype' in self._data else 'ls')


class PeriodList(ListResult):
    '''Aka timetable, a list of periods, in form of :py:class:`PeriodObject`
    instances.'''
    _itemclass = PeriodObject

    def to_table(self, dates=None, times=None):
        '''
        Creates a table-like structure out of the periods. Useful for rendering
        timetables in HTML and other markup languages.

        Check out the example from the repository for clarification.

        :param dates: An iterable of :py:class:`datetime.date` objects that
            definetly should be included in the table. If this parameter is
            ``None``, the timetable is just as wide as it has to be, leaving
            out days without periods.

        :param times: An iterable of :py:class:`datetime.time` objects that
            definetly should be included in the table. If this parameter is
            ``None``, the timetable is just as tall as it has to be, leaving
            out hours without periods.

        :returns: A list containing "rows", which in turn contain "hours",
            which contain :py:class:`webuntis.objects.PeriodObject` instances
            which are happening at the same time.

        '''

        return timetable_utils.table(self, dates=dates, times=times)


class RoomObject(ListItem):
    '''Represents a physical room. Such as a classroom, but also the physics
    lab or whatever.
    '''
    @lazyproperty
    def name(self):
        '''The short name of the room. Such as PHY.'''
        return self._data['name']

    @lazyproperty
    def long_name(self):
        '''The long name of the room. Such as "Physics lab".'''
        return self._data['longName']


class RoomList(ListResult):
    '''A list of rooms, in form of :py:class:`RoomObject` instances.'''
    _itemclass = RoomObject


class SchoolyearObject(ListItem):
    '''Represents a schoolyear.'''

    @lazyproperty
    def name(self):
        '''"2010/2011"'''

        return self._data['name']

    @lazyproperty
    def start(self):
        '''The start date of the schoolyear, as datetime object'''
        return datetime_utils.parse_date(self._data['startDate'])

    @lazyproperty
    def end(self):
        '''The end date'''
        return datetime_utils.parse_date(self._data['endDate'])

    @lazyproperty
    def is_current(self):
        '''
        Boolean, check if this is the current schoolyear::

            >>> y = s.schoolyears()
            >>> y.current.id
            7
            >>> y.current.is_current
            True
            >>> y.filter(id=y.current.id).is_current
            True

        '''
        return (self == self._parent.current)


class SchoolyearList(ListResult):
    '''A list of schoolyears, in form of :py:class:`SchoolyearObject`
    instances.'''
    _itemclass = SchoolyearObject

    @lazyproperty
    def current(self):
        '''Returns the current schoolyear in form of a
        :py:class:`SchoolyearObject`'''
        current_data = self._session._request('getCurrentSchoolyear')
        current = self.filter(id=current_data['id'])[0]
        return current


class SubjectObject(ListItem):
    '''Represents a subject.'''

    @lazyproperty
    def name(self):
        '''Short name of subject, such as *PHY*'''
        return self._data['name']

    @lazyproperty
    def long_name(self):
        '''Long name of subject, such as *Physics*'''
        return self._data['longName']


class SubjectList(ListResult):
    '''A list of subjects, in form of :py:class:`SubjectObject` instances.'''
    _itemclass = SubjectObject


class TeacherObject(ListItem):
    '''Represents a teacher.'''
    @lazyproperty
    def fore_name(self):
        '''fore name of the teacher'''
        return self._data['foreName']

    @lazyproperty
    def long_name(self):
        '''surname of teacher'''
        return self._data['longName']

    surname = long_name

    @lazyproperty
    def name(self):
        '''full name of the teacher'''
        return self._data['name']


class TeacherList(ListResult):
    '''A list of teachers, in form of :py:class:`TeacherObject` instances.'''
    _itemclass = TeacherObject


class TimeunitObject(ListItem):
    '''A bunch of timeunits for a specific day.'''

    @lazyproperty
    def times(self):
        '''A list of tuples containing the start and the end of each timeunit
        as datetime '''

        return [
            (
                datetime_utils.parse_time(unit['startTime']),
                datetime_utils.parse_time(unit['endTime'])
            ) for unit in self._data['timeUnits']
        ]

    @lazyproperty
    def day(self):
        '''The day the timeunit list is for'''
        return self._data['day']

    @lazyproperty
    def id(self):
        return int(self.day)


class TimeunitList(ListResult):
    '''A list of times and dates for the current week, in form of
    :py:class:`TimeunitObject` instances. Doesn't contain actual data, but is
    useful when you want to generate a timetable::

        >>> grid = s.timegrid()
        >>>
        >>> # 1 = Sunday
        >>> # 2 = Monday
        >>> # ...
        >>> # 7 = Saturday
        >>> grid[0].day
        2
        >>> grid[0].times
        [
            (datetime.datetime(...), datetime.datetime(...)),
            ...
        ]

    .. note::
        The date-specific properties of the datetime objects are invalid, since
        these are not provided by the official API.
    '''

    _itemclass = TimeunitObject


class ColorInfo(Result):
    '''
    An object containing information about a lesson type or a period code::

        >>> lstype = s.statusdata().lesson_types[0]
        >>> lstype.name
        'ls'
        >>> lstype.forecolor
        '000000'
        >>> lstype.backcolor
        'ee7f00'

    ::

        >>> pcode = s.statusdata().period_codes[0]
        >>> pcode.name
        'cancelled'
        >>> pcode.forecolor
        'FFFFFF'
        >>> pcode.backcolor
        'FF0000'

    '''

    @lazyproperty
    def id(self):
        return hash(self.__class__.__name__ + self.name)

    @lazyproperty
    def name(self):
        '''The name of the LessonType or PeriodCode'''
        return list(self._data.items())[0][0]

    @lazyproperty
    def forecolor(self):
        '''The foreground color used in the web interface and elsewhere'''
        return self._data[self.name]['foreColor']

    @lazyproperty
    def backcolor(self):
        '''The background color used in the web interface and elsewhere'''
        return self._data[self.name]['backColor']


class StatusData(Result):
    '''Information about lesson types and period codes and their colors.'''

    @lazyproperty
    def lesson_types(self):
        '''A list of :py:class:`ColorInfo` objects, containing
        information about all lesson types defined'''
        return [
            ColorInfo(parent=self, data=data)
            for data in self._data['lstypes']
        ]

    @lazyproperty
    def period_codes(self):
        '''A list of :py:class:`ColorInfo` objects, containing
        information about all period codes defined'''
        return [
            ColorInfo(parent=self, data=data)
            for data in self._data['codes']
        ]
