'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals
import itertools


def table(periods, width=None):
    '''
    Creates a table-like nested list out of a list of periods.

    :param timetable: A :py:class:`webuntis.objects.PeriodList` instance or any
        other iterable containing :py:class:`webuntis.objects.PeriodObject`
        instances.

    :param width: Optionally, a fixed width for the table. The function will
        fill every row with empty cells until that width is met. If the timetable
        is too big, it will raise a ``ValueError``.

    :returns: A list containing "rows", which in turn contain "hours", which
        contain :py:class:`webuntis.objects.PeriodObject` instances which are
        happening at the same time.

    Example::

        monday = datetime.datetime.strptime('20121008', '%Y%m%d')
        friday = datetime.datetime.strptime('20121012', '%Y%m%d')

        table = s.timetable(klasse=878, start=monday, end=friday).to_table()


        print('<table><thead>')
        for weekday in range(5):
            print('<th>' + str(weekday) + '</th>')

        print('</thead><tbody>')
        for time, row in table:
            print('<tr>')
            for weekday_number, cell in row:
                print('<td>')
                for hour in cell:
                    print('<small>' + str(hour.type) + ', ' + str(hour.id) + '</small>')
                    print('<div>')
                    print(', '.join(su.name for su in hour.subjects))
                    print('</div>')

                print('</td>')

            print('</tr>')

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
    if not width:
        longest_row = len(max(grouped, key=len))
    else:
        longest_row = width
    for row in grouped:
        while len(row) < longest_row:
            row.append(list())

    # at last add a weekday indicator
    return zip(times, [enumerate(row) for row in grouped])
