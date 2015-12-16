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

        x = list(r.filter(id=set([1,2])))
        self.assert_strict_equal(x, [results[1], results[2]])

        self.assert_strict_equal(
            list(r.filter(id=set([1,2])).filter(one='eins')),
            list(r.filter(one='eins', id=set([1,2]))),
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
            x = self.Obj(data={u'lstype':type}, session=object())
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

        self.assert_strict_equal(x.name,  u'Math')
        self.assert_strict_equal(x.long_name, u'Mathematics')


class TeacherTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.TeacherObject(
            data={
                u'foreName': u'Hans',
                u'longName': u'Gans',
                u'name': u'Hans Gans'
            },
            session=object()
        )

        self.assert_strict_equal(x.fore_name, u'Hans')
        self.assert_strict_equal(x.long_name, x.surname, u'Gans')
        self.assert_strict_equal(x.name, u'Hans Gans')

class TimeStampTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.TimeStampObject(
            data=1420202020202,
            session=object()
        )
        self.assertEqual(x.date, datetime.datetime(2015, 1, 2, 13, 33, 40))