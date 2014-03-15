from webuntis.tests import WebUntisTestCase
import webuntis.utils.datetime_utils as dtutils
import datetime


class BasicUsage(WebUntisTestCase):
    def test_parse_date(self):
        x = dtutils.parse_date
        assert x('20120403').strftime('%Y-%m-%d') == '2012-04-03'
        assert x(20120403).strftime('%Y-%m-%d') == '2012-04-03'

    def test_parse_time(self):
        x = dtutils.parse_time
        assert x('0800').strftime('%H:%M') == '08:00'
        assert x(800).strftime('%H:%M') == '08:00'

    def test_parse_datetime(self):
        x = dtutils.parse_datetime
        assert x(20120403, 800).strftime('%Y-%m-%d %H:%M') == '2012-04-03 08:00'

    def test_format_date(self):
        x = dtutils.format_date
        assert x('20120403') == x(20120403) == 20120403
        d = datetime.datetime.strptime('20120403', '%Y%m%d')
        assert x(d) == 20120403

    def test_format_time(self):
        x = dtutils.format_time
        assert x(800) == x('0800') == 800
        d = datetime.datetime.strptime('0800', '%H%M')
        assert x(d) == 800
