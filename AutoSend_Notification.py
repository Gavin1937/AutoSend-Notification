import sys
import os
import gc
from My_Logger import logger
from datetime import datetime



# get current system time string fmt=%Y-%m-%d %H:%M:%S.%f
def getSysTimeStr():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

# Send Email to all people in contact_list.json
def sendEmail2All(config, email, contact_list, message_block, subject):
    try:
        logger.info("Trying to send email to all people in contact_list.json")
        print(f"[{getSysTimeStr()}] - Trying to send email to all people in contact_list.json")
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
        logger.warning(f"Cannot send email to all people in contact_list.json. Exception: {str(err)}")
        raise err


def main():
    # import libs
    import locale
    import ArgumentHandler
    
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
            print(f"[{getSysTimeStr()}] - Exit Program")
            logger.info("Exit Program")
            sys.exit()
    
    # declaration
    print(f"[{getSysTimeStr()}] - Initializing program...")
    logger.info("Initializing program...")
    try:
        # import libs
        import ConfigManager
        import TimeMonitor
        import Contact
        
        logger.info("Constructing config")
        config = ConfigManager.ConfigManager()
        logger.info("Finish config")
        
        logger.info("Constructing timemonitor")
        timemonitor = TimeMonitor.TimeMonitor()
        logger.info("Finish timemonitor")
        
        logger.info("Constructing contact")
        contact = Contact.Contact()
        logger.info("Finish contact")
        
    except Exception as err:
        print(f"[{getSysTimeStr()}] - {str(err)}")
        logger.warning(f"Something is wrong during declaration. Exception: {str(err)}")
        logger.info("Exit program")
        sys.exit()
    whether_sent_curr_wk_email = config.getWeeklyEmailCondition_bool()
    
    
    # handle argv
    if argHdl.hasArg():
        # import libs
        import Schedule
        import EmailSender
        # initialize sch
        logger.info("Constructing sch")
        sch = Schedule.Schedule(config.getSpreadsheetID(), config.getSpreadsheetRange(), 
                                timemonitor.getDateTimeObj())
        logger.info("Finish sch")
        # initialize email
        logger.info("Constructing email")
        email = EmailSender.EmailSender(config.getUserEmailAddr(), config.getUserEmailPsw(), config.getSMTPserver())
        logger.info("Finish email")
        
        if argHdl.hasSend2AllMsg():
            try:
                logger.info("Trying to send email to all")
                sendEmail2All(config, email, contact.getContactList(), argHdl.getSend2AllMsg(), config.getMsgSbj())
            except Exception as err:
                logger.warning(f"Fail to send email to all. Exception: {str(err)}")
                raise err
        if argHdl.hasSheetColumn():
            loc_col_buf = sch.getCurrColumn()
            if loc_col_buf != None:
                argHdl.printSheetColumn(loc_col_buf)
            else:
                logger.warning("Cannot find next column in Google Spreadsheet, Spreadsheet data is out of date.")
                raise Exception("Cannot find next column in Google Spreadsheet, Spreadsheet data is out of date.")
        print(f"[{getSysTimeStr()}] - Exit Program")
        logger.info("Exit Program")
        sys.exit()
    
    
    # main loop
    while True:
        # import libs
        from ConfigManager import datetime2sec
        import time
        
        # update config & contact file
        config.update_reload_config()
        contact.updateContact()
        
        # check current time
        print(f"[{getSysTimeStr()}] - Checking current time & internet connection...")
        try:
            logger.info("Trying to check current time & internet connection...")
            timemonitor.updateTime()
        except Exception as err:
            logger.warning(f"Cannot check current time & internet connection. Exception: {str(err)}")
            print(f"[{getSysTimeStr()}] - {str(err)}")
            config.write2config("settings", "internet_connection", "false")
            logger.info(f"Update config.ini: \"internet_connection\" = [{timemonitor.hasInternetConnection()}]")
            raise ValueError("No Internet Connection")
        config.write2config("settings", "internet_connection", "true")
        logger.info(f"Update config.ini: \"internet_connection\" = [{timemonitor.hasInternetConnection()}]")
        
        
        condition_list = ""
        # collecting & logging conditions
        condition_list += str(int(config.getLastNotifyTime() == None))                                          # don't have last notify time
        logger.info(f"\"time_to_refresh_wkly_notification\" [{(config.getLastNotifyTime() == None)}] Whether last notify time is empty")
        condition_list += str(int(config.getWeeklyEmailCondition_bool() == False))                              # haven't send email this week
        logger.info(f"\"time_to_refresh_wkly_notification\" [{(config.getWeeklyEmailCondition_bool() == False)}] Didn't send email this week")
        time_to_refresh_wkly_notification_flag = int(condition_list,2) == int("1"*len(condition_list),2)
        # or
        if not time_to_refresh_wkly_notification_flag:
            condition_list = ""
            condition_list += str(int(timemonitor.getDateTimeObj().date() > config.getLastNotifyTime()))            # current time > last notify time
            logger.info(f"\"time_to_refresh_wkly_notification\" [{(timemonitor.getDateTimeObj().date() > config.getLastNotifyTime())}] Whether current time > last notify time")
            condition_list += str(int(timemonitor.getDateTimeObj().weekday() >= config.getNotificationUpdateDay())) # current weekday >= notification update weekday
            logger.info(f"\"time_to_refresh_wkly_notification\" [{(timemonitor.getDateTimeObj().weekday() >= config.getNotificationUpdateDay())}] Whether current weekday >= notification update weekday")
            time_to_refresh_wkly_notification_flag = int(condition_list,2) == int("1"*len(condition_list),2)
        logger.info(f"Time to refresh wkly notification status: [{time_to_refresh_wkly_notification_flag}]")
        
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
        logger.info(f"\"time_to_send_notification\" [{timemonitor.hasInternetConnection()}] Whether have internet")
        condition_list += str(int(timemonitor.hasTime()))                      # currently timemonitor has datetime value
        logger.info(f"\"time_to_send_notification\" [{timemonitor.hasTime()}] Whether have time in TimeMonitor")
        condition_list += str(int(whether_sent_curr_wk_email == False))        # haven't send this week's email
        logger.info(f"\"time_to_send_notification\" [{(whether_sent_curr_wk_email == False)}] Didn't sent current week's email")
        condition_list += str(int(curr_time.weekday() >= wkDay))               # current weekday >= weekday for notification
        logger.info(f"\"time_to_send_notification\" [{(curr_time.weekday() >= wkDay)}] Whether Current weekday is equal/later than set weekday")
        condition_list += str(int(datetime2sec(curr_time) >= wklyNotiAft))     # current time is >= weekly notification time (sec)
        logger.info(f"\"time_to_send_notification\" [{(datetime2sec(curr_time) >= wklyNotiAft)}] Whether is time to send email")
        condition_list += str(int(datetime2sec(curr_time) < noNotiAft))        # current time is within no notification time limit 1 (sec)
        logger.info(f"\"time_to_send_notification\" [{(datetime2sec(curr_time) < noNotiAft)}] Wether current time is less than no_noti_after")
        condition_list += str(int(datetime2sec(curr_time) >= noNotiBef))       # current time is out of no notification time limit 2 (sec)
        logger.info(f"\"time_to_send_notification\" [{(datetime2sec(curr_time) >= noNotiBef)}] Wether current time is greater/equal to no_noti_before")
        
        time_to_send_notification = int(condition_list, 2) == int("1"*len(condition_list), 2)
        logger.info(f"Time to send notification status: [{time_to_send_notification}]")
        if time_to_send_notification:
            # import libs
            from MsgGenerator import getSermonMsg, getWorshipMsg, getFullEmailMsg
            from pytz import timezone
            import Schedule
            import EmailSender
            
            # initialize sch
            logger.info("Constructing sch")
            sch = Schedule.Schedule(config.getSpreadsheetID(), config.getSpreadsheetRange(), 
                                    timemonitor.getDateTimeObj())
            logger.info("Finish sch")
            # initialize email
            logger.info("Constructing email")
            email = EmailSender.EmailSender(config.getUserEmailAddr(), config.getUserEmailPsw(), config.getSMTPserver())
            logger.info("Finish email")
            
            
            print(f"[{getSysTimeStr()}] - Prepare to send email...")
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
            del curr_column
            logger.info("Find people to contact for emails")
            
            # load messages from file
            logger.info(f"Loading messages from file {config.getMsgFilePath()}")
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
                    email.sendEmail(config.getAdminEmailAddr(), config.getMsgSbj(), msg2admin)
                    logger.info("Sent email to notify admin")
                print(f"[{getSysTimeStr()}] - All emails sent")
                whether_sent_curr_wk_email = True
                config.setSentWklyEmail(whether_sent_curr_wk_email)
                logger.info("Update weekly notification status, already sent notification in this week")
                config.setLastNotifyTime(datetime.now(tz=timezone("US/Pacific")))
                logger.info("Successfully sent email")
                config.update_config()
            except Exception as err:
                print(f"[{getSysTimeStr()}] - {str(err)}")
                logger.warning(f"Fail to send email. Exception: {str(err)}")
            # disconnect server
            email.disconnect()
            
            # remove imported modules, functions, and objects
            # obj
            del email
            del sch
            del sermon_person
            del worship_person
            del msg_str_arr
            del msg2admin
            # function
            del getSermonMsg
            del getWorshipMsg
            del getFullEmailMsg
            # module
            del Schedule
            del EmailSender
            
        else:
            print(f"[{getSysTimeStr()}] - No more task now, sleep for {config.getSleepTimeSec_int(timemonitor.getDateTimeObj())} seconds")
            logger.info(f"No more task now, sleep for {config.getSleepTimeSec_int(timemonitor.getDateTimeObj())} seconds")
            time.sleep(config.getSleepTimeSec_int(timemonitor.getDateTimeObj()))
            
        
        # remove caches from main loop
        del datetime2sec
        del condition_list
        del wkDay
        del wklyNotiAft
        del noNotiBef
        del noNotiAft
        del curr_time
        # force Garbage Collector to release unreferenced memory
        gc.collect()


if __name__ == "__main__":
    while True:
        try:    
            print(f"[{getSysTimeStr()}] - Start Program")
            logger.info("Start Program")
            main()
            print(f"[{getSysTimeStr()}] - Exit Program")
            logger.info("Exit Program")
        except KeyboardInterrupt:
            gc.collect()
            print()
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except ValueError as verr:
            from time import sleep
            if "No Internet Connection" in str(verr):
                sleep(1800)
        except Exception as err:
            print(f"[{getSysTimeStr()}] - {str(err)}")
            logger.warning(f"Something wrong with program. Exception: {str(err)}")


