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
from My_Logger import *


def main():
    # set locale
    locale.setlocale(locale.LC_ALL, '')
    logger.info("Set locale")
    
    # declaration
    print("Initializing program...")
    logger.info("Initializing program...")
    try:
        logger.info("Constructing timemonitor")
        timemonitor = TimeMonitor.TimeMonitor()
        logger.info("Finish timemonitor")
        logger.info("Constructing contact")
        contact = Contact.Contact()
        logger.info("Finish contact")
        logger.info("Constructing sch")
        sch = Schedule.Schedule("1FUdVpQe8WYOcYyFWFrbVJSvhVwqskRGL_8kYZCfgci4", "Sheet1!A1:H", 
                                timemonitor.getDateTimeObj())
        logger.info("Finish sch")
        logger.info("Constructing email")
        email = EmailSender.EmailSender("gyh2060411551gyh@gmail.com", "gyh1999037gyh.gmail2")
        logger.info("Finish email")
        logger.info("Constructing config")
        config = ConfigManager.ConfigManager()
        logger.info("Finish config")
    except Exception as err:
        print(err)
        logger.warning("Something is wrong during declaration. Exception: %s" % str(err))
        logger.info("Exit program")
        sys.exit()
    whether_sent_curr_wk_email = config.getWeeklyEmailCondition_bool()
    
    
    # main loop
    while True:
        # check current time
        print("Checking current time & internet connection...")
        logger.info("Checking current time & internet connection...")
        timemonitor.updateObj()
        config.write2config("settings", "internet_connection", 
                            "true" if timemonitor.hasInternetConnection() else "false")
        logger.info("Update config.ini \"internet_connection\" setting")
        
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
            print("Prepare to send email...")
            logger.info("Prepare to send email...")
            # update schedule from google spreadsheets
            sch.setCurrDate(timemonitor.getDateTimeObj())
            sch.updateSpreadsheet()
            logger.info("Update google spreadsheets from internet")
            
            # find contact people
            curr_column = sch.getCurrColumn()
            sermon_person = contact.findContact(curr_column[3])
            worship_person = contact.findContact(curr_column[4])
            logger.info("Find people to contact for emails")
            
            # generate messages for people
            sermon_person_msg = getFullEmailMsg(getSermonMsg(sermon_person["refer_name"]), "(132) 456-789")
            worship_person_msg = getFullEmailMsg(getWorshipMsg(worship_person["refer_name"]), "(132) 456-789")
            logger.info("Generate messages for people")
            
            # send email
            try:
                logger.info("Trying to send email")
                email.sendEmail(sermon_person["email"], "GCDC auto sent sermon notification", sermon_person_msg)
                logger.info("Sent email to preacher")
                email.sendEmail(worship_person["email"], "GCDC auto sent worship notification", worship_person_msg)
                logger.info("Sent email to worship leader")
                whether_sent_curr_wk_email = True
                print("All emails sent")
                logger.info("Successfully sent email")
            except Exception as err:
                print(err)
                logger.warning("Fail to send email. Exception: %s" % str(err))
            
        else:
            logger.info("No more task now, sleep for 5 sec")
            print("sleeping %s" % timemonitor.getDateTimeObj().time())
            time.sleep(5)
            # logger.info("No more task now, sleep for 6 hr")
            # time.sleep(21600) # sleep for 6 hr
            print("5 sec later")


if __name__ == "__main__":
    main()
    logger.info("Exist Program")