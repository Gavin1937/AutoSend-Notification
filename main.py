import locale

import TimeMonitor
import Contact
import Schedule

import datetime


def main():
    
    locale.setlocale(locale.LC_ALL, '')
    
    tm = TimeMonitor.TimeMonitor()
    
    try:
        c = Contact.Contact()
    except Exception as err:
        print(err)
    
    if c.isFileExist() == True:
        print(c.findEmail("日本語"))
    
    try:
        sch = Schedule.Schedule("1FUdVpQe8WYOcYyFWFrbVJSvhVwqskRGL_8kYZCfgci4", "Sheet1!A1:H", datetime.datetime(year=2020, month=8, day=1))
        
        
    except Exception as err:
        print(err)
    
    
    print(sch.getCurrColumn())
    
    sch.setCurrDate(datetime.datetime(year=2020, month=11, day=19))
    
    print(sch.getCurrColumn())
    



if __name__ == "__main__":
    main()