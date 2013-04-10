import webuntis
from webuntis.tests import WebUntisTestCase


class BasicUsage(WebUntisTestCase):
    def test_server(self):
        x = webuntis.utils.userinput.server
        assert x('webuntis.grupet.at') == 'http://webuntis.grupet.at/WebUntis/jsonrpc.do'
        assert x('https://webuntis.grupet.at') == 'https://webuntis.grupet.at/WebUntis/jsonrpc.do'
        assert x('webuntis.grupet.at:8080') == 'http://webuntis.grupet.at:8080/WebUntis/jsonrpc.do'
        assert x('webuntis.grupet.at/a/b/c') == 'http://webuntis.grupet.at/a/b/c'
        assert x('webuntis.grupet.at/') == 'http://webuntis.grupet.at/'

        self.assertRaises(ValueError, x, '!"$%')
        self.assertRaises(ValueError, x, '')

    def test_string(self):
        x = webuntis.utils.userinput.string
        try:
            uc = unicode
        except NameError:
            uc = str

        assert type(x('foo')) is uc
