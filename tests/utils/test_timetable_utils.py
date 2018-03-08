import datetime
from webuntis.utils.timetable_utils import table
from .. import WebUntisTestCase


class StubPeriod(object):
    def __init__(self, start, end):
        self.start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M')
        self.end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M')


class BasicUsage(WebUntisTestCase):
    def test_empty(self):
        assert table([]) == []

    def test_simple(self):
        monday = [
            StubPeriod('2012-05-03 08:01', '2012-05-03 09:00'),
            StubPeriod('2012-05-03 09:01', '2012-05-03 10:00')
        ]

        tuesday = [
            StubPeriod('2012-06-03 08:01', '2012-06-03 09:00'),
            StubPeriod('2012-06-03 09:01', '2012-06-03 10:00')
        ]

        wednesday = [
            StubPeriod('2012-07-03 08:01', '2012-07-03 09:00'),
            StubPeriod('2012-07-03 09:01', '2012-07-03 10:00')
        ]

        given_input = set(monday + tuesday + wednesday)
        rows = table(given_input)

        assert len(rows) == 2
        assert all(len(row) == 3 for time, row in rows)
        assert all(all(len(cell) == 1 for date, cell in row) for time, row in rows)
        assert all(all(list(cell)[0] in given_input for date, cell in row) for time, row in rows)
