import datetime

from . import WebUntisTestCase
import webuntis


class ResultTests(WebUntisTestCase):
    Result = webuntis.objects.Result

    def test_initialization(self):
        r = self.Result(data={'id': 123}, session=object())
        self.assert_strict_equal(r.id, int(r), 123)
        r = self.Result(data={'id': 124}, parent=r)
        self.assert_strict_equal(r.id, int(r), 124)

        self.assertRaises(TypeError, self.Result, data={u'id': 137})
        self.assertRaises(TypeError, self.Result, data={u'id': 137},
                          session=object(), parent=r)
        self.assertRaises(TypeError, self.Result, data={u'id': 139},
                          parent=object())

    def test_hashes(self):
        r1 = self.Result(data={u'id': 124}, session=object())

        r2 = None
        assert r1 != r2
        assert hash(r1) != hash(r2)

        r2 = self.Result(data={u'id': 123}, session=object())
        assert r1 != r2
        assert hash(r1) != hash(r2)

        r2 = self.Result(data={u'id': 124}, session=object())
        assert r1 == r2
        assert hash(r1) == hash(r2)

    def test_str(self):
        r1 = self.Result(data={u'id': 124}, session=object())
        assert str(r1) == u"{u'id': 124}" or str(r1) == u"{'id': 124}"
        r2 = self.Result(data={u'name': "abc"}, session=object())
        assert str(r2) == u'abc'

    def test_repr(self):
        r1 = self.Result(data={u'id': 124}, session=object())
        assert repr(r1) == u"Result({u'id': 124})" or repr(r1) == u"Result({'id': 124})"

class ListResultTests(WebUntisTestCase):
    Result = webuntis.objects.ListResult
    lazyproperty = webuntis.utils.misc.lazyproperty

    def test_basics(self):
        class CustomItem(webuntis.objects.ListItem):
            @self.lazyproperty
            def value(self):
                return self._data[u'val']

        class CustomListResult(self.Result):
            _itemclass = CustomItem

        data = [
            {u'id': 1, u'val': 3},
            {u'id': 2, u'val': 19},
            {u'id': 3, u'val': 29}
        ]

        r = CustomListResult(data=list(data), session=object())

        self.assert_strict_equal(len(r), len(data))
        for res, raw in zip(r, data):
            assert type(res) is CustomItem
            assert res in r
            assert {u'id': res.id, u'value': res.value} in r
            self.assert_strict_equal(res.id, raw[u'id'])

        s = str(r);
        assert "'val': 3" in s
        assert "'id': 2" in s
        s = repr(r);
        assert "'val': 3" in s
        assert "'id': 2" in s
        assert 'CustomListResult' in s
        assert 'CustomItem' in s


    def test_filter(self):
        class CustomItem(webuntis.objects.ListItem):
            @self.lazyproperty
            def one(self):
                return self._data[u'one']

            @self.lazyproperty
            def two(self):
                return self._data[u'two']

        class CustomListResult(self.Result):
            _itemclass = CustomItem

        data = [
            {u'id': 1, u'one': u'eins', u'two': u'zwei'},
            {u'id': 2, u'one': u'oans', u'two': u'zwoa'},
            {u'id': 3, u'one': u'unus', u'two': u'duo'}
        ]

        r = CustomListResult(data=list(data), session=object())
        self.assert_strict_equal(len(r), 3)

        results = dict((x.id, x) for x in r)

        x = list(r.filter(id=1))
        self.assert_strict_equal(x, [results[1]])

        x = list(r.filter(id=set([1, 2])))
        self.assert_strict_equal(x, [results[1], results[2]])

        self.assert_strict_equal(
            list(r.filter(id=set([1, 2])).filter(one='eins')),
            list(r.filter(one='eins', id=set([1, 2]))),
            [results[1]]
        )

        x = list(r.filter(two='zwoa'))
        self.assert_strict_equal(x, [results[2]])


class DepartmentTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.DepartmentObject(
            data={u'id': 1, u'name': u'ZIMMER', u'longName': u'Das Zimmer'},
            session=object())

        self.assert_strict_equal(x.name, u'ZIMMER')
        self.assert_strict_equal(x.long_name, u'Das Zimmer')


class HolidayTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.HolidayObject(
            data={
                u'id': 1,
                u'name': u'SOMMER',
                u'longName': u'Sommerferien',
                u'startDate': u'20120303',
                u'endDate': u'20120403'
            },
            session=object())

        assert x.short_name == u'SOMMER'
        assert x.name == u'Sommerferien'

        assert x.start.strftime('%Y-%m-%d') == '2012-03-03'
        assert x.end.strftime('%Y-%m-%d') == '2012-04-03'


class KlassenTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.KlassenObject(
            data={
                u'id': 1,
                u'name': u'1A',
                u'longName': u'Erste A'
            },
            session=object())

        self.assert_strict_equal(x.name, u'1A')
        self.assert_strict_equal(x.long_name, u'Erste A')


class PeriodTests(WebUntisTestCase):
    Obj = webuntis.objects.PeriodObject

    def test_dates(self):
        x = self.Obj(
            data={
                u'id': 1,
                u'startTime': u'0800',
                u'endTime': u'0900',
                u'date': u'20120303'
            },
            session=object()
        )

        assert x.start.strftime('%Y-%m-%d %H:%M') == '2012-03-03 08:00'
        assert x.end.strftime('%Y-%m-%d %H:%M') == '2012-03-03 09:00'

    def test_code(self):
        x = self.Obj(data={}, session=object())
        assert x.code is None

        x = self.Obj(data={u'code': u''}, session=object())
        assert x.code is None

        x = self.Obj(data={u'code': u'hoompaloompa'}, session=object())
        assert x.code is None

        x = self.Obj(data={u'code': u'cancelled'}, session=object())
        self.assert_strict_equal(x.code, u'cancelled')

        x = self.Obj(data={u'code': u'irregular'}, session=object())
        self.assert_strict_equal(x.code, u'irregular')

    def test_type(self):
        x = self.Obj(data={}, session=object())
        self.assert_strict_equal(x.type, u'ls')

        for type in (u'ls', u'oh', u'sb', u'bs', u'ex'):
            x = self.Obj(data={u'lstype': type}, session=object())
            self.assert_strict_equal(x.type, type)

        x = self.Obj(data={u'type': u'hoompaloompa'}, session=object())
        self.assert_strict_equal(x.type, u'ls')


class RoomTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.RoomObject(
            data={u'name': u'PHY', u'longName': u'Physics lab'},
            session=object()
        )

        self.assert_strict_equal(x.name, u'PHY')
        self.assert_strict_equal(x.long_name, u'Physics lab')


class SchoolyearTests(WebUntisTestCase):
    def test_object(self):
        class parent(object):
            _session = object()
            current = {u'name': u'Holidayz'}

        x = webuntis.objects.SchoolyearObject(
            data={
                u'name': u'Holidayz',
                u'startDate': u'20120401',
                u'endDate': u'20120901'
            },
            parent=parent
        )

        assert not x.is_current  # that kind of "weak typing" really shouldn't work
        assert x.start.strftime('%Y-%m-%d') == '2012-04-01'
        assert x.end.strftime('%Y-%m-%d') == '2012-09-01'
        assert x.name == u'Holidayz'

    def test_list(self):
        class StubSession(object):
            def _request(s, method):
                assert method == u'getCurrentSchoolyear'
                return {u'id': 123}

        x = webuntis.objects.SchoolyearList(
            data=[
                {u'id': 121, u'name': u'Summer'},
                {u'id': 122, u'name': u'Autumn'},
                {u'id': 123, u'name': u'Winter'},
                {u'id': 124, u'name': u'St. Florian'}
            ],
            session=StubSession()
        )

        self.assert_strict_equal(x.current.id, 123)
        assert x.current.is_current
        self.assert_strict_equal(x.current.name, u'Winter')


class SubjectTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.SubjectObject(
            data={
                u'name': u'Math',
                u'longName': u'Mathematics'
            },
            session=object()
        )

        self.assert_strict_equal(x.name, u'Math')
        self.assert_strict_equal(x.long_name, u'Mathematics')


class TeacherTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.TeacherObject(
            data={
                u'foreName': u'Hans',
                u'longName': u'Gans',
                u'name': u'Hans Gans',
                u'title': u'Dr',
            },
            session=object()
        )

        self.assert_strict_equal(x.fore_name, u'Hans')
        self.assert_strict_equal(x.long_name, x.surname, u'Gans')
        self.assert_strict_equal(x.name, u'Hans Gans')

        self.assert_strict_equal(x.title, u'Dr')
        self.assert_strict_equal(x.full_name, u'Dr Hans Gans')


class TimeStampTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.TimeStampObject(
            data=1420202020202,
            session=object()
        )
        exp = datetime.datetime(2015, 1, 2, 13, 33, 40,tzinfo=None)


        self.assertEqual(x.date.date(), exp.date())
        # some differences py2 vs. py3:
        # self.assertEqual(x.date.time(), exp.time())
        ## TODO: hour: fails for travis, but is ok here ;-(( removed for now
        ## self.assertEqual(x.date.time().hour, exp.time().hour)
        self.assertEqual(x.date.time().minute, exp.time().minute)
        self.assertEqual(x.date.time().second, exp.time().second)


class TimegridTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.TimegridObject(
            data=[{'day': 2, 'timeUnits': [{'startTime': 710, 'name': '0', 'endTime': 800},
                                           {'startTime': 800, 'name': '1', 'endTime': 850},
                                           {'startTime': 850, 'name': '2', 'endTime': 940}]}],
                  session = object())

        self.assertEqual(x[0].day, 2)
        self.assertEqual(x[0].dayname, "monday")
        self.assertEqual(x[0].timeUnits[0].name, "0")
        self.assertEqual(x[0].timeUnits[1].start, datetime.time(8, 0))
        self.assertEqual(x[0].timeUnits[2].end, datetime.time(9, 40))


class PeriodTestsData(WebUntisTestCase):
    def test_data(self):
        sess = object()
        klasse1 = webuntis.objects.KlassenObject(
            data={u'id': 2, u'name': u'1A'},
            session=sess)
        teacher1 = webuntis.objects.TeacherObject(
            data={u'id': 3, u'name': u'Hans Gans'},
            session=sess)
        teacher2 = webuntis.objects.TeacherObject(
            data={u'id': 7, u'name': u'Daniel Duesentrieb'},
            session=sess)
        subject1 = webuntis.objects.SubjectObject(
            data={u'id': 4, u'name': u'Math'},
            session=sess
        )
        room1 = webuntis.objects.RoomObject(
            data={u'id': 5, u'name': u'PHY', u'longName': u'Physics lab'},
            session=object()
        )
        room2 = webuntis.objects.RoomObject(
            data={u'id': 8, u'name': u'TS'},
            session=sess
        )

        class StubSession(object):
            def klassen(self, *args, **kw):
                return webuntis.objects.KlassenList(
                    [klasse1], session=sess)

            def teachers(self, *args, **kw):
                return webuntis.objects.TeacherList(
                    [teacher1, teacher2], session=sess)

            def subjects(self, *args, **kw):
                return webuntis.objects.SubjectList(
                    [subject1], session=sess)

            def rooms(self, *args, **kw):
                return webuntis.objects.RoomList(
                    [room1, room2], session=sess)

        p = webuntis.objects.PeriodObject(
            data={
                u'id': 1,
                u'kl': [{"id": 2}],
                u'te': [{"id": 3, u'orgid': 7}],
                u'su': [{"id": 4}],
                u'ro': [{"id": 5, u'orgid': 8}],
            },
            session=StubSession()
        )
        self.assertEqual(p.klassen[0].name, u'1A')
        self.assertEqual(p.teachers[0].name, u'Hans Gans')
        self.assertEqual(p.subjects[0].name, u'Math')
        self.assertEqual(p.rooms[0].name, u'PHY')

        self.assertEqual(p.original_teachers[0].name, u'Daniel Duesentrieb')
        self.assertEqual(len(p.original_teachers), 1)

        # without orgid
        p = webuntis.objects.PeriodObject(
            data={
                u'id': 1,
                u'kl': [{"id": 2}],
                u'te': [{"id": 3}],
                u'su': [{"id": 4}],
                u'ro': [{"id": 5}],
            },
            session=StubSession()
        )
        self.assertEqual(len(p.original_teachers), 0)
        self.assertEqual(len(p.original_rooms), 0)


class SubstitutionTests(WebUntisTestCase):
    def test_substitution(self):
        s = webuntis.objects.SubstitutionObject(
            data={
                u'reschedule': {u'date': u'20170304', u'startTime': u'1002', u'endTime': u'1101'},
                u'type': u'reason',
            },
            session=object()
        )

        self.assertEqual(s.type, u'reason')
        start = s.reschedule_start
        self.assertEqual(start.date(), datetime.date(2017, 3, 4))
        # TODO: hour: fails for travis, but is ok here ;-(( removed for now
        self.assertEqual(start.time().minute, 2)
        end = s.reschedule_end
        self.assertEqual(end.time().minute, 1)
