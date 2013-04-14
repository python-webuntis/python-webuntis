from webuntis.tests import WebUntisTestCase
import webuntis


class ResultTests(WebUntisTestCase):
    Result = webuntis.objects.Result
    def test_initialization(self):
        r = self.Result(data={'id': 123}, session=object())
        assert r.id == int(r) == 123
        r = self.Result(data={'id': 124}, parent=r)
        assert r.id == int(r) == 124

        self.assertRaises(TypeError, self.Result, data={'id': 137})
        self.assertRaises(TypeError, self.Result, data={'id': 137},
                          session=object(), parent=r)
        self.assertRaises(TypeError, self.Result, data={'id': 139},
                          parent=object())

    def test_hashes(self):
        r1 = self.Result(data={'id': 124}, session=object())

        r2 = None
        assert r1 != r2
        assert hash(r1) != hash(r2)

        r2 = self.Result(data={'id': 123}, session=object())
        assert r1 != r2
        assert hash(r1) != hash(r2)

        r2 = self.Result(data={'id': 124}, session=object())
        assert r1 == r2
        assert hash(r1) == hash(r2)


class ListResultTests(WebUntisTestCase):
    Result = webuntis.objects.ListResult
    lazyproperty = webuntis.utils.misc.lazyproperty

    def test_basics(self):
        class CustomItem(webuntis.objects.ListItem):
            @self.lazyproperty
            def value(self):
                return self._data['val']

        class CustomListResult(self.Result):
            _itemclass = CustomItem

        data = [
            {'id': 1, 'val': 3},
            {'id': 2, 'val': 19},
            {'id': 3, 'val': 29}
        ]

        r = CustomListResult(data=list(data), session=object())

        assert len(r) == len(data)
        for res, raw in zip(r, data):
            assert type(res) is CustomItem
            assert res in r
            assert {'id': res.id, 'value': res.value} in r
            assert res.id == raw['id']

    def test_filter(self):
        class CustomItem(webuntis.objects.ListItem):
            @self.lazyproperty
            def one(self):
                return self._data['one']

            @self.lazyproperty
            def two(self):
                return self._data['two']

        class CustomListResult(self.Result):
            _itemclass = CustomItem

        data = [
            {'id': 1, 'one': 'eins', 'two': 'zwei'},
            {'id': 2, 'one': 'oans', 'two': 'zwoa'},
            {'id': 3, 'one': 'unus', 'two': 'duo'}
        ]

        r = CustomListResult(data=list(data), session=object())
        assert len(r) == 3

        results = dict((x.id, x) for x in r)

        assert list(r.filter(id=1)) == [results[1]]
        assert list(r.filter(id=set([1,2]))) == [results[1], results[2]]
        assert list(r.filter(id=set([1,2])).filter(one='eins')) == \
               list(r.filter(one='eins', id=set([1,2]))) == [results[1]]


class DepartmentTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.DepartmentObject(
            data={'id': 1, 'name': 'ZIMMER', 'longName': 'Das Zimmer'},
            session=object())

        assert x.name == 'ZIMMER'
        assert x.long_name == 'Das Zimmer'

class HolidayTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.HolidayObject(
            data={
                'id': 1,
                'name': 'SOMMER',
                'longName': 'Sommerferien',
                'startDate': '20120303',
                'endDate': '20120403'
            },
            session=object())

        assert x.short_name == 'SOMMER'
        assert x.name == 'Sommerferien'

        assert x.start.year == 2012
        assert x.start.month == 03
        assert x.start.day == 03

        assert x.end.year == 2012
        assert x.end.month == 04
        assert x.end.day == 03


class KlassenTests(WebUntisTestCase):
    def test_basics(self):
        x = webuntis.objects.KlassenObject(
            data={
                'id': 1,
                'name': '1A',
                'longName': 'Erste A'
            },
            session=object())

        assert x.name == '1A'
        assert x.long_name == 'Erste A'
