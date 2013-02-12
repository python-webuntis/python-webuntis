from credentials import s
import datetime
import logging

# ***DO NOT USE THIS EXAMPLE AS-IS***
# Properties that are printed here may contain arbitrary
# *unescaped* HTML. That is not expected, but you should not trust
# input from remote sources in general.

logging.basicConfig(level=logging.DEBUG)

today = datetime.date.today()

monday = today - datetime.timedelta(days=today.weekday())
friday = monday + datetime.timedelta(days=4)

klasse = s.klassen().filter(name='1A')[0]
table = s.timetable(klasse=klasse, start=monday, end=friday).to_table()


print('<table border="1"><thead><th>Time</th>')
for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
    print('<th>' + str(weekday) + '</th>')

print('</thead><tbody>')
for time, row in table:
    print('<tr>')
    print('<td>{}</td>'.format(time.strftime('%H:%M')))
    for date, cell in row:
        print('<td>')
        for period in cell:
            print(', '.join(su.name for su in period.subjects))
        print('</td>')

    print('</tr>')

print('</tbody></table>')
