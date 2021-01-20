import locale
import datetime
import time
import sys

# additional modules
import TimeMonitor
import Contact
import Schedule
import EmailSender
from MsgGenerator import *
import ConfigManager


def main():
    # set locale
    locale.setlocale(locale.LC_ALL, '')
    
    # declaration
    print("initializing program...")
    try:
        timemonitor = TimeMonitor.TimeMonitor()
        contact = Contact.Contact()
        sch = Schedule.Schedule("1FUdVpQe8WYOcYyFWFrbVJSvhVwqskRGL_8kYZCfgci4", "Sheet1!A1:H", 
                                timemonitor.getDateTimeObj())
        email = EmailSender.EmailSender("gyh2060411551gyh@gmail.com", "gyh1999037gyh.gmail2")
        config = ConfigManager.ConfigManager()
    except Exception as err:
        print(err)
        sys.exit(1)
    whether_sent_curr_wk_email = config.getWeeklyEmailCondition_bool()
    
    
    # main loop
    while True:
        # check current time
        print("checking current time & internet connection...")
        timemonitor.updateObj()
        config.write2config("settings", "internet_connection", 
                            "true" if timemonitor.hasInternetConnection() else "false")
        
        wkDay = config.getNotificationTime_wkDay()
        hr = config.getNotificationTime_hr()
        
        time_to_send_notification = (                                                       # conditions 
                                        timemonitor.hasInternetConnection() and             # currently has internet connection
                                        timemonitor.hasTime() and                           # currently timemonitor has datetime value
                                        whether_sent_curr_wk_email == False and             # haven't send this week's email
                                        timemonitor.getDateTimeObj().weekday() == wkDay and # today is Wednesday
                                        #! timemonitor.getDateTimeObj().hour >= hr             # current time is >= noon
                                        timemonitor.getDateTimeObj().hour >= 0              # current time is >= noon
                                    )
        if time_to_send_notification:
            print("prepare to send email...")
            # update schedule from google spreadsheets
            sch.setCurrDate(timemonitor.getDateTimeObj())
            sch.updateSpreadsheet()
            
            # find contact people
            curr_column = sch.getCurrColumn()
            sermon_person = contact.findContact(curr_column[3])
            worship_person = contact.findContact(curr_column[4])
            
            # generate messages for people
            sermon_person_msg = getFullEmailMsg(getSermonMsg(sermon_person["refer_name"]), "(132) 456-789")
            worship_person_msg = getFullEmailMsg(getWorshipMsg(worship_person["refer_name"]), "(132) 456-789")
            
            # send email
            try:
                email.sendEmail(sermon_person["email"], "GCDC auto sent sermon notification", sermon_person_msg)
                email.sendEmail(worship_person["email"], "GCDC auto sent worship notification", worship_person_msg)
                whether_sent_curr_wk_email = True
                print("email sent!")
            except Exception as err:
                print(err)
            
        else:
            # print(timemonitor.getDateTimeStr_ctime())
            # print(getSermonMsg(sch.getCurrColumn()[3]))
            print("sleeping %s" % timemonitor.getDateTimeObj().time())
            time.sleep(5)
            # time.sleep(21600) # sleep for 6 hr
            print("5 sec later")


if __name__ == "__main__":
    main()