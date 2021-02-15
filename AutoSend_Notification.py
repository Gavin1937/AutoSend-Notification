
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
from ConfigManager import datetime2sec, sec2datetime
import ArgumentHandler
from My_Logger import logger



# get current system time string fmt=%Y-%m-%d %H:%M:%S.%f
def getSysTimeStr():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

# Send Email to all people in contact_list.json
def sendEmail2All(config, email, contact_list, message_block, subject):
    try:
        logger.info("Trying to send email to all people in contact_list.json")
        print("[%s] - Trying to send email to all people in contact_list.json" % getSysTimeStr())
        buff = ""
        for person in contact_list:
            msg = message_block.replace("#", person["refer_name"])
            email.sendEmail(person["email"], subject, msg)
            buff += person["refer_name"] + ", "
        if config.isEnableNotiAdmin():
            msg2admin = "Sent Email to All:\n" + buff + "\n\nMessage:\n" + message_block
            email.sendEmail(config.getAdminEmailAddr(), 
                        "AutoSend-Notification: Email Sending Notification",
                        msg2admin)
            logger.info("Sent Email to notify admin")
    except Exception as err:
        logger.warning("Cannot send email to all people in contact_list.json. Exception: %s" % str(err))
        raise err


def main():
    # set locale
    locale.setlocale(locale.LC_ALL, '')
    logger.info("Set locale")
    
    # construct ArgumentHandler to handle arguments first
    logger.info("Constructing argHdl")
    argHdl = ArgumentHandler.ArgumentHandler(sys.argv)
    logger.info("Finish argHdl")
    # handle help argument
    if argHdl.hasArg():
        if argHdl.hasHelp():
            argHdl.printHelp()
            print("[%s] - Exit Program" % getSysTimeStr())
            logger.info("Exit Program")
            sys.exit()
    
    # declaration
    print("[%s] - Initializing program..." % getSysTimeStr())
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
        email = EmailSender.EmailSender(config.getUserEmailAddr(), config.getUserEmailPsw(), config.getSMTPserver())
        logger.info("Finish email")
        
    except Exception as err:
        print("[%s] - %s" % (getSysTimeStr(), str(err)))
        logger.warning("Something is wrong during declaration. Exception: %s" % str(err))
        logger.info("Exit program")
        sys.exit()
    whether_sent_curr_wk_email = config.getWeeklyEmailCondition_bool()
    
    
    # handle argv
    if argHdl.hasArg():
        if argHdl.hasSend2AllMsg():
            try:
                logger.info("Trying to send email to all")
                sendEmail2All(config, email, contact.getContactList(), argHdl.getSend2AllMsg(), config.getMsgSbj())
            except Exception as err:
                logger.warning("Fail to send email to all. Exception: %s" % str(err))
                raise err
        if argHdl.hasSheetColumn():
            loc_col_buf = sch.getCurrColumn()
            if loc_col_buf != None:
                argHdl.printSheetColumn(loc_col_buf)
            else:
                logger.warning("Cannot find next column in Google Spreadsheet, Spreadsheet data is out of date.")
                raise Exception("Cannot find next column in Google Spreadsheet, Spreadsheet data is out of date.")
        print("[%s] - Exit Program" % getSysTimeStr())
        logger.info("Exit Program")
        sys.exit()
    
    
    # main loop
    while True:
        # check current time
        print("[%s] - Checking current time & internet connection..." % getSysTimeStr())
        try:
            logger.info("Trying to check current time & internet connection...")
            timemonitor.updateTime()
        except Exception as err:
            logger.warning("Cannot check current time & internet connection. Exception: %s" % str(err))
            print("[%s] - %s" % (getSysTimeStr(), str(err)))
        config.write2config("settings", "internet_connection", 
                            "true" if timemonitor.hasInternetConnection() else "false")
        logger.info("Update config.ini \"internet_connection\" setting")
        
        
        condition_list = ""
        # collecting & logging conditions
        condition_list += str(int(config.getLastNotifyTime() == None))                                          # don't have last notify time
        logger.info("\"time_to_refresh_wkly_notification\" [%r] Whether last notify time is empty" % bool(int(condition_list[len(condition_list)-1])))
        condition_list += str(int(config.getWeeklyEmailCondition_bool() == False))                              # haven't send email this week
        logger.info("\"time_to_refresh_wkly_notification\" [%r] Didn't send email this week" % bool(int(condition_list[len(condition_list)-1])))
        time_to_refresh_wkly_notification_flag = int(condition_list,2) == int("1"*len(condition_list),2)
        # or
        if not time_to_refresh_wkly_notification_flag:
            condition_list = ""
            condition_list += str(int(timemonitor.getDateTimeObj().date() > config.getLastNotifyTime()))            # current time > last notify time
            logger.info("\"time_to_refresh_wkly_notification\" [%r] Whether current time > last notify time" % bool(int(condition_list[len(condition_list)-1])))
            condition_list += str(int(timemonitor.getDateTimeObj().weekday() >= config.getNotificationUpdateDay())) # current weekday >= notification update weekday
            logger.info("\"time_to_refresh_wkly_notification\" [%r] Whether current weekday >= notification update weekday" % bool(int(condition_list[len(condition_list)-1])))
            time_to_refresh_wkly_notification_flag = int(condition_list,2) == int("1"*len(condition_list),2)
        logger.info("Time to refresh wkly notification status: [%r]" % time_to_refresh_wkly_notification_flag)
        
        # reset weekly notification flag if is new week
        if time_to_refresh_wkly_notification_flag:
            whether_sent_curr_wk_email = False
            config.setSentWklyEmail(whether_sent_curr_wk_email)
            logger.info("Fresh weekly notification status, haven't send notification in this week")
        
        wkDay = config.getNotificationTime_wkDay()
        wklyNotiAft = config.getNotificationTime_WklyNotiAfter()
        noNotiBef = config.getNotificationTime_NoNotiBef()
        noNotiAft = config.getNotificationTime_NoNotiAft()
        curr_time = timemonitor.getDateTimeObj()
        
        
        condition_list = ""
        # collecting & logging conditions
        condition_list += str(int(timemonitor.hasInternetConnection()))        # currently has internet connection
        logger.info("\"time_to_send_notification\" [%r] Whether have internet" % bool(int(condition_list[len(condition_list)-1])))
        condition_list += str(int(timemonitor.hasTime()))                      # currently timemonitor has datetime value
        logger.info("\"time_to_send_notification\" [%r] Whether have time in TimeMonitor" % bool(int(condition_list[len(condition_list)-1])))
        condition_list += str(int(whether_sent_curr_wk_email == False))        # haven't send this week's email
        logger.info("\"time_to_send_notification\" [%r] Didn't sent current week's email" % bool(int(condition_list[len(condition_list)-1])))
        condition_list += str(int(curr_time.weekday() >= wkDay))               # current weekday >= weekday for notification
        logger.info("\"time_to_send_notification\" [%r] Whether Current weekday is equal/later than set weekday" % bool(int(condition_list[len(condition_list)-1])))
        condition_list += str(int(datetime2sec(curr_time) >= wklyNotiAft))     # current time is >= weekly notification time (sec)
        logger.info("\"time_to_send_notification\" [%r] Whether is time to send email" % bool(int(condition_list[len(condition_list)-1])))
        condition_list += str(int(datetime2sec(curr_time) < noNotiAft))        # current time is within no notification time limit 1 (sec)
        logger.info("\"time_to_send_notification\" [%r] Wether current time is less than no_noti_after" % bool(int(condition_list[len(condition_list)-1])))
        condition_list += str(int(datetime2sec(curr_time) >= noNotiBef))       # current time is out of no notification time limit 2 (sec)
        logger.info("\"time_to_send_notification\" [%r] Wether current time is greater/equal to no_noti_before" % bool(int(condition_list[len(condition_list)-1])))
        
        time_to_send_notification = int(condition_list, 2) == int("1"*len(condition_list), 2)
        logger.info("Time to send notification status: [%r]" % time_to_send_notification)
        if time_to_send_notification:
            print("[%s] - Prepare to send email..." % getSysTimeStr())
            logger.info("Prepare to send email...")
            # update schedule from google spreadsheets
            sch.setCurrDate(timemonitor.getDateTimeObj())
            sch.updateSpreadsheet()
            logger.info("Update google spreadsheets from internet")
            if sch.getCurrColumn() == None:
                logger.warning("Cannot find next column in Google Spreadsheet, Spreadsheet data is out of date.")
                raise Exception("Cannot find next column in Google Spreadsheet, Spreadsheet data is out of date.")
            
            # find contact people
            curr_column = sch.getCurrColumn()
            sermon_person = contact.findContact(curr_column[3])
            worship_person = contact.findContact(curr_column[4])
            logger.info("Find people to contact for emails")
            
            # update connection with SMTP server
            email.reconnect()
            logger.info("Reconnect to SMTP server")
            
            # load messages from file
            logger.info("Loading messages from file %s" % config.getMsgFilePath())
            msg_str_arr = config.getMsgsFromFile()
            
            # generate messages for people
            if config.isEnableNotiAdmin():
                msg2admin = "Sent Email to:\n\n"
            if sermon_person != None:
                sermon_person_msg = getFullEmailMsg(msg_str_arr[0],
                                            getSermonMsg(msg_str_arr[1], sermon_person["refer_name"]),
                                            config.getUserNum())
                if config.isEnableNotiAdmin():
                    msg2admin += "Sermon Person: " + sermon_person["name"] + ",\n\nMessage:\n" + sermon_person_msg + "\n\n"
            if worship_person != None:
                worship_person_msg = getFullEmailMsg(msg_str_arr[0],
                                            getWorshipMsg(msg_str_arr[2], worship_person["refer_name"]),
                                            config.getUserNum())
                if config.isEnableNotiAdmin():
                    msg2admin += "Worship Person: " + worship_person["name"] + ",\n\nMessage:\n" + worship_person_msg + "\n\n"
            logger.info("Generate messages for people")
            
            # send email
            try:
                logger.info("Trying to send email")
                if sermon_person != None:
                    email.sendEmail(sermon_person["email"], config.getMsgSbj(), sermon_person_msg)
                    logger.info("Sent email to preacher")
                if worship_person != None:
                    email.sendEmail(worship_person["email"], config.getMsgSbj(), worship_person_msg)
                    logger.info("Sent email to worship leader")
                if config.isEnableNotiAdmin():
                    email.sendEmail(config.getAdminEmailAddr(),
                                "AutoSend-Notification: Email Sending Notification",
                                msg2admin)
                    logger.info("Sent email to notify admin")
                print("[%s] - All emails sent" % getSysTimeStr())
                whether_sent_curr_wk_email = True
                config.setSentWklyEmail(whether_sent_curr_wk_email)
                logger.info("Update weekly notification status, already sent notification in this week")
                config.setLastNotifyTime(datetime.now(tz=timezone("US/Pacific")))
                logger.info("Successfully sent email")
            except Exception as err:
                print("[%s] - %s" % (getSysTimeStr(), str(err)))
                logger.warning("Fail to send email. Exception: %s" % str(err))
            # disconnect server
            email.disconnect()
            
        else:
            # disconnect server
            email.disconnect()
            print("[%s] - No more task now, sleep for %s seconds" % (getSysTimeStr(), config.getSleepTimeSec_int(timemonitor.getDateTimeObj())))
            logger.info("No more task now, sleep for %s seconds" % config.getSleepTimeSec_int(timemonitor.getDateTimeObj()))
            time.sleep(config.getSleepTimeSec_int(timemonitor.getDateTimeObj()))


if __name__ == "__main__":
    try:    
        print("[%s] - Start Program" % getSysTimeStr())
        logger.info("Start Program")
        main()
        print("[%s] - Exit Program" % getSysTimeStr())
        logger.info("Exit Program")
    except Exception as err:
        print("[%s] - %s" % (getSysTimeStr(), str(err)))
        logger.warning("Something wrong with program. Exception: %s" %str(err))
        logger.warning(str(err))


