import webuntis
from .. import WebUntisTestCase


class Functions(WebUntisTestCase):
    def test_lazyproperty(self):
        class FooBar(object):
            obj = 42
            _already_called = False
            @webuntis.utils.misc.lazyproperty
            def yesplease(self):
                assert not self._already_called
                self._already_called = True
                return self.obj
                
        foobar = FooBar()
        assert foobar.yesplease == 42
        foobar.obj = 43
        assert foobar.yesplease == 42

    def test_result_wrapper(self):
        wrapper = webuntis.utils.misc.result_wrapper
        class PseudoSession(object):
            def __init__(self):
                self.cache = {}

            def _request(self, method, args):
                return (method, args)  # "data"

            @wrapper
            def some_stuff(self):
                method = 'getFoo'
                args = {'chocolate': 'yesplease'}

                def resultclass(session, data):
                    assert session is self
                    assert data == (method, args)
                    return data

                return resultclass, method, args

        s = PseudoSession()

        a = s.some_stuff()
        b = s.some_stuff()
        assert a == b
        assert a is not b

        a = s.some_stuff()
        b = s.some_stuff(from_cache=True)
        assert a == b
        assert a is b

    def test_cache_key(self):
        x = webuntis.utils.misc.cache_key

        a = x('klassen', {})
        b = x('klassen', None)
        assert hash(a) == hash(b)
        assert a is not b

        c = x('klassen', {'g': 'G'})
        assert hash(c) != hash(a)
        assert hash(c) != hash(b)

        d = x('teachers', {})
        assert hash(d) != hash(a)
        assert hash(d) != hash(c)

class LruDictTests(WebUntisTestCase):
    def test_basic_interface(self):
        def test(Dict):
            d = Dict(maxlen=3)

            d['one'] = 1
            d['two'] = 2
            d['three'] = 3

            assert list(d.items()) == [
                ('one', 1),
                ('two', 2),
                ('three', 3)
            ]

            d['four'] = 4
            assert list(d.items()) == [
                ('two', 2),
                ('three', 3),
                ('four', 4)
            ]

            d['two'] = 5
            assert list(d.items()) == [
                ('three', 3),
                ('four', 4),
                ('two', 5)
            ]

            d['three']
            assert list(d.items()) == [
                ('three', 3),
                ('four', 4),
                ('two', 5)
            ]

            d.clear()
            assert not d

        test(webuntis.utils.misc.LruDict)
        test(webuntis.utils.misc.SessionCache)

    def test_sessioncache_clear(self):
        d = webuntis.utils.misc.SessionCache(maxlen=50)

        d[('getDuck', 123)] = 'Hans Gans'
        d[('getDuck', 234)] = 'Donald Duck'
        d[('getDuck', 345)] = 'Daisy Duck'
        d[('getDuck', 456)] = 'Dagobert Duck'
        d[('getDog', 567)] = 'Pluto'
        d[('getDog', 678)] = 'Goofy'
        d[('getMouse', 324)] = 'Mickey'
        d[('getMouse', 576)] = 'Minnie'

        d.clear('getMouse')
        assert not any(m == 'getMouse' for m, a in d.keys())
        assert len(d) == 6

        d.clear('getDog')
        assert len(d) == 4

        d.clear('getDuck')
        assert not d


class FilterDictTests(WebUntisTestCase):
    def test_basics(self):
        d = webuntis.utils.misc.FilterDict({
            'foo': lambda x: 'whoopdeedoo',
            'bar': lambda x: 1/0,
            'alwaysnone': lambda x: None
        })

        d['foo'] = 'somethingelse'
        assert d['foo'] == 'whoopdeedoo'

        self.assertRaises(KeyError, d.__getitem__, 'bar')
        self.assertRaises(KeyError, d.__getitem__, 'what')
        self.assertRaises(KeyError, d.__setitem__, 'somekey', 'someval')

        d['foo'] = None
        assert 'foo' not in d
        d['foo'] = 'somethingelse'
        assert 'foo' in d
        del d['foo']
        assert 'foo' not in d

        d['alwaysnone'] = 'YES'
        assert 'alwaysnone' not in d

        assert list(d) == []
        d.update({'foo': 'bar', 'alwaysnone': True})
        assert set(d) == set(['foo'])
