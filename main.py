import locale
from datetime import datetime, timedelta
from pytz import timezone
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
    
    # prompt user for basic infos use in declaration part
    # TODO: add prompt
    
    # declaration
    print("Initializing program...")
    logger.info("Initializing program...")
    try:
        logger.info("Constructing config")
        config = ConfigManager.ConfigManager()
        logger.info("Finish config")
        
        logger.info("Constructing timemonitor")
        timemonitor = TimeMonitor.TimeMonitor()
        logger.info("Finish timemonitor")
        
        logger.info("Constructing contact")
        contact = Contact.Contact()
        logger.info("Finish contact")
        
        logger.info("Constructing sch")
        sch = Schedule.Schedule(config.getSpreadsheetID(), config.getSpreadsheetRange(), 
                                timemonitor.getDateTimeObj())
        logger.info("Finish sch")
        
        logger.info("Constructing email")
        email = EmailSender.EmailSender(config.getUserEmailAddr(), config.getUserEmailPsw())
        logger.info("Finish email")
        
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
        
        # reset weekly notification flag if is new week
        time_to_refresh_wkly_notification_flag = (
            timemonitor.getDateTimeObj().date() > config.getLastNotifyTime() and
            timemonitor.getDateTimeObj().weekday() <= config.getNotificationUpdateDay()
        )
        if time_to_refresh_wkly_notification_flag:
            whether_sent_curr_wk_email = False
            config.setSentWklyEmail(whether_sent_curr_wk_email)
            logger.info("Fresh weekly notification status, haven't send notification in this week")
        
        wkDay = config.getNotificationTime_wkDay()
        hr = config.getNotificationTime_hr()
        min = config.getNotificationTime_min()
        sec = config.getNotificationTime_sec()
        
        time_to_send_notification = (                                                        # conditions 
                                        timemonitor.hasInternetConnection() and              # currently has internet connection
                                        timemonitor.hasTime() and                            # currently timemonitor has datetime value
                                        whether_sent_curr_wk_email == False and              # haven't send this week's email
                                        timemonitor.getDateTimeObj().weekday() == wkDay and  # today is Wednesday
                                        timemonitor.getDateTimeObj().hour >= hr and          # current time is >= noon
                                        timemonitor.getDateTimeObj().minute >= min and       # current time min >= 0
                                        timemonitor.getDateTimeObj().second >= sec           # current time sec >= 0
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
            if sermon_person != None:
                sermon_person_msg = getFullEmailMsg(getSermonMsg(sermon_person["refer_name"]), config.getUserNum())
            if worship_person != None:
                worship_person_msg = getFullEmailMsg(getWorshipMsg(worship_person["refer_name"]), config.getUserNum())
            logger.info("Generate messages for people")
            
            # send email
            try:
                logger.info("Trying to send email")
                if sermon_person != None:
                    email.sendEmail(sermon_person["email"], "GCDC auto sent sermon notification", sermon_person_msg)
                    logger.info("Sent email to preacher")
                if worship_person != None:
                    email.sendEmail(worship_person["email"], "GCDC auto sent worship notification", worship_person_msg)
                    logger.info("Sent email to worship leader")
                print("All emails sent")
                whether_sent_curr_wk_email = True
                config.setSentWklyEmail(whether_sent_curr_wk_email)
                logger.info("Update weekly notification status, already sent notification in this week")
                config.setLastNotifyTime(datetime.now(tz=timezone("US/Pacific")))
                logger.info("Successfully sent email")
            except Exception as err:
                print(err)
                logger.warning("Fail to send email. Exception: %s" % str(err))
            
        else:
            print("sleeping for %s seconds" % config.getSleepTimeSec_int())
            logger.info("No more task now, sleep for %s sec" % config.getSleepTimeSec_int())
            time.sleep(config.getSleepTimeSec_int())


if __name__ == "__main__":
    main()
    logger.info("Exist Program")