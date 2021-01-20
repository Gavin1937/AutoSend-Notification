import locale

import TimeMonitor
import Contact



tm = TimeMonitor.TimeMonitor()

dt = tm.getDateTimeObj()

print(dt)

print(tm.hasInternatConnection())

print(tm.getDateTimeStr())
print(tm.getDateTimeStr_ctime())


locale.setlocale(locale.LC_ALL, '')


try:
    c = Contact.Contact()
except Exception as err:
    print(err)

# for i in c.getData()['contact_list']:
print(c.findEmail("日本語"))