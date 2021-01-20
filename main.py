import TimeMonitor


tm = TimeMonitor.TimeMonitor()

dt = tm.getDateTimeObj()

print(dt)

print(tm.hasInternatConnection())

print(tm.getDateTimeStr())
print(tm.getDateTimeStr_ctime())