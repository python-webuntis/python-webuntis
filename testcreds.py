import webuntis
import logging
logging.basicConfig(level=logging.DEBUG)
s = webuntis.Session(
    username='api',
    password='api',
    server='webuntis.grupet.at:8080',
    school='demo_inf',
    useragent='test'
)
