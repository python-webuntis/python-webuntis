'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals

from webuntis.utils import datetime_utils, lazyproperty


class Result(object):
    _jsonrpc_method = False
    _data = False

    def __init__(self, session, kwargs={}):
        if not self._jsonrpc_method:
            raise NotImplementedError

        self.session = session
        self._data = self._get_data(**kwargs)

    def _jsonrpc_parameters(self, **kwargs):
        '''This method returns all methods that should be passed to the
        JSON-RPC request'''
        # we return an empty dictionary here so subclasses don't
        # really need to overwrite this if they actually have no parameters
        return {}

    def _get_data(self, **kwargs):
        '''A simple wrapper for the jsonrpc_parameters builder.
        Can be overwritten by subclasses, which may require more complex
        options'''
        return self.session._request(
            self._jsonrpc_method,
            self._jsonrpc_parameters(**kwargs)
        )


class ListItem(object):
    '''ListItems represent an item in a
    :py:class:`webuntis.objects.ListResult`. They don\'t contain methods to
    retrieve data.'''

    noid = False

    def __init__(self, session, parent, rawdata):
        '''
        Keyword arguments:
        session -- a webuntis.session.Session object
        rawdata -- the relevant part of a json result for this object
        '''
        self.session = session
        self.parent = parent
        self.rawdata = rawdata

        self.id = self.rawdata['id'] if 'id' in self.rawdata else None

    def __int__(self):
        '''This is useful if the users pass a ListItem when a numerical ID
        is expected, so we just can put the thing through int(), regardless of
        what type it is.'''
        return self.id


class ListResult(Result):
    '''ListResult is an iterable version of
    :py:class:`webuntis.objects.Result`.
    '''

    # When the Result returns an array, this is very useful. Every item of that
    # array will be fed to an instance of self._itemclass, with the session and
    # the array item as initialization arguments.

    _itemclass = ListItem

    def filter(self, **criterions):
        '''
        Returns a list of all objects, filtered by attributes::

            foo = s.klassen().filter(id=1)  # returns basically the same as...
            foo = [kl for kl in s.klassen() if kl.id == 1]

        ::
        '''
        def meets_criterions(item):
            for key, value in criterions.items():
                # if the attribute value isn't one we're looking for
                if type(value) == list and getattr(item, key) in value:
                    continue
                elif getattr(item, key) == value:
                    continue
                else:
                    return False

            return True

        return [item for item in self if meets_criterions(item)]

    def __getitem__(self, i):
        '''Makes the object iterable and behave like a list'''
        if not isinstance(self._data[i], ListItem):
            # if we don't have an object yet
            self._data[i] = self._itemclass(self.session, self, self._data[i])

        return self._data[i]

    def __len__(self):
        '''Return the length of the items'''
        return len(self._data)


class DepartmentObject(ListItem):
    '''Represents a department
    '''

    @lazyproperty
    def name(self):
        '''short name such as *R1A*'''
        return self.rawdata['name']

    @lazyproperty
    def long_name(self):
        '''Long name, such as *Raum Erste A*. Not predictable.'''
        return self.rawdata['longName']


class DepartmentList(ListResult):
    '''A list of all departments::

        departments = s.departments()

    ::
    '''
    _itemclass = DepartmentObject
    _jsonrpc_method = 'getDepartments'


class HolidayObject(ListItem):
    '''Represents a single holiday.
    '''

    @lazyproperty
    def start(self):
        '''The start date of the holiday, as a datetime object.'''
        return datetime_utils.parse_date(self.rawdata['startDate'])

    @lazyproperty
    def end(self):
        '''The end of the holiday'''
        return datetime_utils.parse_date(self.rawdata['endDate'])

    @lazyproperty
    def name(self):
        '''Name, such as *Nationalfeiertag*.'''
        return self.rawdata['longName']

    @lazyproperty
    def short_name(self):
        '''Abbreviated form of the name'''
        return self.rawdata['name']


class HolidayList(ListResult):
    '''A list of all holidays::

        s.holidays()

    ::
    '''
    _itemclass = HolidayObject
    _jsonrpc_method = 'getHolidays'


class KlassenObject(ListItem):
    '''Represents a school class.'''

    @lazyproperty
    def name(self):
        '''Name of class'''
        return self.rawdata['name']

    @lazyproperty
    def long_name(self):
        '''Long name of class'''
        return self.rawdata['longName']


class KlassenList(ListResult):
    '''A list of all school classes.

    :param schoolyear:
        The schoolyear where we should get all our school \
        classes from. Either a \
        :py:class:`webuntis.objects.SchoolyearObject` or an \
        id of it.

    ::
        >>> s.klassen()
        >>>
        >>> year = s.schoolyears().filter(id=2)
        >>> s.klassen(schoolyear=year)

    '''
    _itemclass = KlassenObject
    _jsonrpc_method = 'getKlassen'

    def _jsonrpc_parameters(self, schoolyear=None):
        jsonrpc_parameters = {}
        if schoolyear:
            jsonrpc_parameters.update({
                'schoolyearId': int(schoolyear)
            })

        return jsonrpc_parameters


class PeriodObject(ListItem):
    '''Represents a time range, where lessons/subjects may be held.
    '''

    @lazyproperty
    def start(self):
        '''The start date/time of the period, as datetime object.'''

        return datetime_utils.parse_datetime(
            self.rawdata['date'],
            self.rawdata['startTime']
        )

    @lazyproperty
    def end(self):
        '''The end date/time of the period.'''

        return datetime_utils.parse_datetime(
            self.rawdata['date'],
            self.rawdata['endTime']
        )

    @lazyproperty
    def klassen(self):
        '''A list of :py:class:`webuntis.objects.KlassenObject` instances,
        which are attending this period.'''

        return self.session.klassen().filter(
            id=[kl['id'] for kl in self.rawdata['kl']]
        )

    @lazyproperty
    def teachers(self):
        '''A list of :py:class:`webuntis.objects.TeacherObject` instances,
        which are attending this period.'''

        return self.session.teachers().filter(
            id=[te['id'] for te in self.rawdata['te']]
        )

    @lazyproperty
    def subjects(self):
        '''A list of :py:class:`webuntis.objects.SubjectObject` instances,
        which are topic of this period. This is not used for things like
        multiple language lessons (*e.g.* Latin, Spanish, French) -- each of
        those will get placed in their own period.'''

        return self.session.subjects().filter(
            id=[su['id'] for su in self.rawdata['su']]
        )

    @lazyproperty
    def rooms(self):
        '''The rooms where this period is taking place at. This also is not
        used for multiple lessons, but rather for a single lesson that is
        actually occuring at multiple locations.'''

        return self.session.rooms().filter(
            id=[ro['id'] for ro in self.rawdata['ro']]
        )

    @lazyproperty
    def type(self):
        '''May be "cancelled" or "irregular" -- the latter implies a
        substitution.'''

        return self.rawdata['lstype'] if 'lstype' in self.rawdata else None


class PeriodList(ListResult):
    '''
    Aka timetable

    :param start: a starting date either in the form YYMMDD or as date/time
        object.
    :param end: a ending date in the same form as the starting date.

    Furthermore you have to explicitly define a klasse, teacher, subject, room
    or student parameter containing the id or the object of the thing you want
    to get a timetable about::

        schoolclass = s.klassen().filter(id=1)  # schoolclass #1

        s.timetable(klasse=schoolclass)  # which is the same as...
        s.periods(klasse=schoolclass)

    .. note:: See :py:mod:`webuntis.utils.timetable_utils` for various tools
        around the timetable.
    '''
    _itemclass = PeriodObject
    _jsonrpc_method = 'getTimetable'

    def _jsonrpc_parameters(self, start=None, end=None, **type_and_id):
        element_type_table = {
            'klasse':  1,
            'teacher': 2,
            'subject': 3,
            'room':    4,
            'student': 5
        }

        if len(type_and_id) != 1:
            raise ValueError(
                'You have to specify exactly one of the following parameters \
                    by keyword: ' +
                ', '.join(element_type_table.keys())
            )

        # apply end to start and vice-versa if one of them is missing
        if not start and end:
            start = end
        elif not end and start:
            end = start

        element_type, element_id = list(type_and_id.items())[0]

        # if we have to deal with an object in element_id,
        # its id gets placed here anyway
        parameters = {
            'id': int(element_id),
            'type': element_type_table[element_type],
        }

        if start:
            parameters['startDate'] = datetime_utils.format_date(start)
        if end:
            parameters['endDate'] = datetime_utils.format_date(end)

        return parameters


class RoomObject(ListItem):
    '''Represents a physical room. Such as a classroom, but also the physics
    laboratory or whatever.
    '''
    @lazyproperty
    def name(self):
        '''The short name of the room. Such as PHY.'''
        return self.rawdata['name']

    @lazyproperty
    def long_name(self):
        '''The long name of the room. Such as "Physics lab".'''
        return self.rawdata['longName']


class RoomList(ListResult):
    '''
    Represents a list of rooms::

        s.rooms()

    '''
    _itemclass = RoomObject
    _jsonrpc_method = 'getRooms'


class SchoolyearObject(ListItem):
    '''Represents a schoolyear.
    '''

    @lazyproperty
    def name(self):
        '''"2010/2011"'''

        return self.rawdata['name']

    @lazyproperty
    def start(self):
        '''The start date of the schoolyear, as datetime object'''
        return datetime_utils.parse_date(self.rawdata['startDate'])

    @lazyproperty
    def end(self):
        '''The end date'''
        return datetime_utils.parse_date(self.rawdata['endDate'])

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
        return (self == self.parent.current)


class SchoolyearList(ListResult):
    '''
    Represents a list of school years::

        s.schoolyears()

    '''
    _itemclass = SchoolyearObject
    _jsonrpc_method = 'getSchoolyears'

    @lazyproperty
    def current(self):
        '''Returns the current schoolyear in form of a
        :py:class:`webuntis.objects.SchoolyearObject`'''
        current_rawdata = self.session._request('getCurrentSchoolyear')
        current = self.filter(id=current_rawdata['id'])[0]
        return current


class SubjectObject(ListItem):
    '''Represents a subject.
    '''

    @lazyproperty
    def name(self):
        '''Short name of subject, such as *PHY*'''
        return self.rawdata['name']

    @lazyproperty
    def long_name(self):
        '''Long name of subject, such as *Physics*'''
        return self.rawdata['longName']


class SubjectList(ListResult):
    '''Represents a list of subjects::

        s.subjects()

    ::
    '''
    _itemclass = SubjectObject
    _jsonrpc_method = 'getSubjects'


class TeacherObject(ListItem):
    '''Represents a teacher.
    '''
    @lazyproperty
    def fore_name(self):
        '''fore name of the teacher'''
        return self.rawdata['foreName']

    @lazyproperty
    def long_name(self):
        '''surname of teacher'''
        return self.rawdata['longName']

    surname = long_name

    @lazyproperty
    def name(self):
        '''full name of the teacher'''
        return self.rawdata['name']


class TeacherList(ListResult):
    '''
    Represents a list of teachers::

        s.teachers()  # get all teachers of school

    ::
    '''
    _itemclass = TeacherObject
    _jsonrpc_method = 'getTeachers'


class TimeunitObject(ListItem):
    '''A bunch of timeunits for a specific day.
    '''

    @lazyproperty
    def times(self):
        '''A list of tuples containing the start and the end of each timeunit
        as datetime '''

        return [
            (
                datetime_utils.parse_time(unit['startTime']),
                datetime_utils.parse_time(unit['endTime'])
            ) for unit in self.rawdata['timeUnits']
        ]

    @lazyproperty
    def day(self):
        '''The day the timeunit list is for'''
        return self.rawdata['day']


class TimeunitList(ListResult):
    '''A list of times and dates for the current week. Doesn't contain actual
    data, but is useful when you want to generate a timetable::

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
        The date properties of the datetime objects are invalid! Since these
        are not provided by the official API, there's not much you can do about
        it.
    '''

    _itemclass = TimeunitObject
    _jsonrpc_method = 'getTimegridUnits'

class ColorInfo(object):
    '''An object containing information about a lession type or a period code::

        >>> lstype = s.statusdata().lession_types['ls']
        >>> lstype.name
        'ls'
        >>> lstype.forecolor
        '000000'
        >>> lstype.backcolor
        'ee7f00'
        >>>
    '''

    def __init__(self, rawdata):
        self.name = list(rawdata.items())[0][0]
        self.forecolor = rawdata[self.name]['foreColor']
        self.backcolor = rawdata[self.name]['backColor']

    @lazyproperty
    def name(self):
        '''The name of the LessionType or PeriodCode'''
        return list(self._data.items())[0][0]

    @lazyproperty
    def forecolor(self):
        '''The foreground color used in the web interfacei and elsewhere'''
        return self._data[self.name]['foreColor']

    @lazyproperty
    def backcolor(self):
        '''The background color used in the web interface and elsewhere'''
        return self._data[self.name]['backColor']

class StatusData(Result):
    '''
    Information about lession types and period codes and their colors::
    
        s.statusdata()

    '''
    _jsonrpc_method = 'getStatusData'

    @lazyproperty
    def lession_types(self):
        '''A list of :py:class:`webuntis.objects.ColorInfo` objects, containing
        information about all lession types defined'''
        return [
            ColorInfo(rawdata) for rawdata in self._data['lstypes']
        ]

    @lazyproperty
    def period_codes(self):
        '''A list of :py:class:`webuntis.objects.ColorInfo` objects, containing
        information about all period codes defined'''
        return [
            ColorInfo(rawdata) for rawdata in self._data['codes']
        ]

# Defines result classes that are accessible from outside
object_lists = {
    'departments': DepartmentList,
    'holidays': HolidayList,
    'klassen': KlassenList,
    'rooms': RoomList,
    'schoolyears': SchoolyearList,
    'subjects': SubjectList,
    'teachers': TeacherList,

    'timegrid': TimeunitList,
    'timeunits': TimeunitList,
    'statusdata': StatusData,

    'timetable': PeriodList,
    'periods': PeriodList
}
