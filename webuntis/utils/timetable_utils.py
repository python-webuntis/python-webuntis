'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals
import itertools


def table(periods, include_cancelled=False):
    '''
    Creates a table-like nested list out of a list of periods.

    :param timetable: A :py:class:`webuntis.objects.PeriodList` instance.
    :param include_cancelled: Defaults to false, defines whether cancelled
    periods should be included in the timetable.

    Returns a list containing "rows", which in turn contain "hours", which
    contain :py:class:`webuntis.objects.PeriodObject` instances which are
    happening at the same time.

    Example::

        # monday and friday belong to the same week

        hours = s.timetable(start=monday, end=friday)
        table = webuntis.utils.timetable_utils.table(hours)

        print('<table><thead>')
        for weekday in range(5):
            print('<th>' + weekday + '</th>')

        print('</thead><tbody>')
        for time, row in table:
            for weekday_number, cell in row:
                for period in cell:
                    for subject in period.subjects:
                        print(subject.name + ', ')

        print('</tbody></table>')

    Gives you HTML like this:

    +--------+--------+--------+--------+--------+
    | 0      | 1      | 2      | 3      | 4      |
    +========+========+========+========+========+
    | ME     | M      | PH     | M      | GSK    |
    +--------+--------+--------+--------+--------+
    | M      | BU     | D      | FRA    | D      |
    +--------+--------+--------+--------+--------+
    | E      | BU     | FRA    | BU     | E      |
    +--------+--------+--------+--------+--------+
    | RK,    | GSK    | E      | ME     | GWK    |
    | RISL   |        |        |        |        |
    +--------+--------+--------+--------+--------+
    | D      | BE     | M      | PH     | PH     |
    +--------+--------+--------+--------+--------+
    | FRA    |        |        |        |        |
    +--------+--------+--------+--------+--------+
    | INF+   |        |        |        |        |
    +--------+--------+--------+--------+--------+
    | INF+   |        |        |        |        |
    +--------+--------+--------+--------+--------+
    | BSP    | RKO    |        |        |        |
    +--------+--------+--------+--------+--------+

    '''

    if not len(periods):
        return []

    if not include_cancelled:
        periods = (period for period in periods if period.type != 'cancelled')

    time = lambda x: int(x.start.strftime('%H%M%S'))
    date = lambda x: int(x.start.strftime('%Y%m%d'))

    grouped = []
    times = []
    for i, row in itertools.groupby(sorted(periods, key=time), time):
        new_row = []

        starttime = None

        # group lessons by date -- now all lessons occuring at the same time
        # are grouped
        for i2, hour in itertools.groupby(sorted(row, key=date), date):
            if hour:
                # itertools._grouper objects can't be accessed like lists
                hour = list(hour)
                weekday = hour[0].start.weekday()

                while (len(new_row) - 1) < weekday:
                    new_row.append(list())  # expand row as much as needed
                new_row[weekday] = hour

                if not starttime:
                    starttime = hour[0].start

        grouped.append(new_row)
        times.append(starttime)

    # expand each row to the maximal length
    longest_row = len(max(grouped, key=len))
    for row in grouped:
        while len(row) < longest_row:
            row.append(list())

    # at last add a weekday indicator
    return zip(times, [enumerate(row) for row in grouped])
