"""
    This file is part of python-webuntis

    :copyright: (c) 2013 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import unicode_literals

from copy import deepcopy
from datetime import datetime


def table(periods, dates=None, times=None):
    """The backend of :py:meth:`webuntis.objects.PeriodList.to_table`."""

    if not len(periods):
        return []

    # generate some useful sets
    times = set(times or []).union(period.start.time() for period in periods)
    dates = set(dates or []).union(period.start.date() for period in periods)
    datetimes = set(datetime.combine(d, t) for d in dates for t in times)

    # create an empty table from all possible combinations of dates and times
    ttable = dict((t, dict((d, set()) for d in dates)) for t in times)

    # add the periods to the table
    # periods may be added twice if they are longer than one hour
    for period in periods:
        for dt in datetimes:
            if period.start <= dt < period.end:
                ttable[dt.time()][dt.date()].add(period)

    # Convert the hashtable to the output format by sorting each dictionary's
    # .items() by key.
    return sorted((time, sorted(row.items())) for time, row in ttable.items())


def combine(periods, combine_breaks=True):
    """
    shorten a list of periods (or substitutions) by combining consecutive Elements

    :type combine_breaks: bool
    :param combine_breaks: combine breaks
    :type periods: webuntis.objects.PeriodList or webuntis.objects.SubstitionList
    :param periods: Periodlist do combine/shorten

    :return:
    """

    if len(periods) < 2:
        return periods

    result_type = type(periods)

    olddata = [deepcopy(p._data) for p in periods]

    if u'lsid' in olddata[0]:
        olddata.sort(key=lambda p: (p[u'lsid'], p[u'date'], p[u'startTime']))
    else:
        olddata.sort(key=lambda p: (p[u'date'], p[u'startTime']))

    data = []
    last = olddata[0]

    # fields to compare
    fields = set(k for k in last.keys() if not isinstance(last[k], list)) - {u'id', u'key', u'startTime', u'endTime'}
    if u'su' in last.keys():
        fields |= {u'su', u'kl'}  # don't combine different subjects or klassen
    # fields to combine
    fields_list = set(k for k in last.keys() if isinstance(last[k], list)) - {u'id', u'key'}

    for current in olddata[1:]:
        try:
            same = (all(current[field] == last[field] for field in fields) and
                    (combine_breaks or (last[u'endTime'] in [current[u'startTime', current[u'endTime']]])))
        except KeyError:
            same = False
        if same:
            last[u'endTime'] = current[u'endTime']
            for f in fields_list:
                for c in current[f]:
                    if c not in last[f]:
                        last[f].append(c)
        else:
            data.append(last)
            last = current

    data.append(last)

    data.sort(key=lambda p: (p[u'date'], p[u'startTime']))
    res = result_type(parent=periods._parent, session=periods._session, data=data)
    return res
