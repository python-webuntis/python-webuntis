import webuntis
import logging

logging.basicConfig(level=logging.DEBUG)

# Testserver from Grupet
# Used by all examples

s = webuntis.Session(
        username='api',
        password='api',
        server='webuntis.grupet.at:8080',
        useragent='foo',
        school='demo_inf'
)

s.login()
