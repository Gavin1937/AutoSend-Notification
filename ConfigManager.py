from configparser import ConfigParser
import os
from datetime import datetime, timedelta
from My_Logger import logger


# global variables
user_info_arr = {
    "contact_person_name": "",          # Who to contact for questions
    "contact_person_number": "",        # Phone number of this person
    "sender_email_addr": "",            # Sender Email's address
    "sender_email_password": "",        # Sender Email's password
    "enable_notify_admin": "true",      # Whether send an email to notify contact_person (admin) after each email sending, default=true
    "admin_email_addr": "",             # If enable_notify_admin=true, require an email for contact_person (admin)
    "spreadsheet_id": "",               # Id of Google Spreadsheet to read
    "spreadsheet_range": "",            # Range of Google Spreadsheet to read
    "message_subject": "",              # Subject for all auto send emails
    "messages_file_path": ""            # Path to text file that contains all message blocks
}
settings_arr = {
    "internet_connection": "false",     # Whether have internet connection
                                        # **DO NOT MODIFY THIS VALUE**
    "sent_weekly_email": "false",       # Whether sent current week's email
                                        # **DO NOT MODIFY THIS VALUE**
    "weekly_checking_day": "2",         # When to check time & internet connection in a week, (2 = Wednesday)
    "weekly_checking_time": "43200",    # When to check time & internet connection in a "weekly_checking_day",
                                        # always start from 0sec of the day
    "smtp_server": "smtp.gmail.com:587" # SMTP server:port, default to Google
}
notification_time_arr = {
    "update_day": "0",                  # When to refresh notification flag for a new week, (0 = Monday)
    "week_day": "2",                    # When to send notification, (2 = Wednesday)
    "wkly_noti_after": "43200",         # When to send notification, value is in seconds in a day (43200=12pm,12)
    "no_noti_before": "25200",          # Stop sending notification before this time, value is in seconds in a day (25200=7am,7)
    "no_noti_after": "79200",           # Stop sending notification after this time, value is in seconds in a day (79200=10pm,22)
    "last_notify_time": ""              # Record of last notification time, auto set by program
                                        # **DO NOT MODIFY THIS VALUE**
}

# global functions
def sec2datetime(seconds):
    sec = timedelta(seconds)
    return (datetime(1,1,1) + sec)

def datetime2sec(date):
    sec = (date - date.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return int(sec)


class ConfigManager:
    
    # default constructor
    def __init__(self):
        logger.info("Constructing ConfigManager object...")
        self.__config = ConfigParser()
        logger.info("Constructed self.__config")
        config_file_exist_flag = False
        config_file_has_size_flag = False
        try:
            if os.path.exists(os.getcwd()+"/config.ini"):
                config_file_exist_flag = True
            if os.path.getsize(os.getcwd()+"/config.ini") > 0:
                config_file_has_size_flag = True
        except:
            config_file_exist_flag = False
            config_file_has_size_flag = False
        if not config_file_exist_flag and not config_file_has_size_flag:
            logger.info("Cannot find config.ini, create & write basic info to a new file")
            self.write_basic_info2Config()
        else:
            logger.info("Found config.ini, read from it")
            self.__config.read("./config.ini")
    
    
    # checking config.ini missing
    def check_config_missing(self):
        have_all_config = False
        missing_configs = list()
        
        logger.info("Checking config file")
        while not have_all_config:
            logger.info("Reload config.ini")
            self.__config.read("./config.ini")
            missing_configs.clear()
            # check config.ini
            all_sections = self.__config.sections()
            
            # process admin notification configs
            enable_notiAdm_val = self.__config.get("user_info", "enable_notify_admin")
            adm_EmailAddr_val = self.__config.get("user_info", "admin_email_addr")
            if len(enable_notiAdm_val) <= 0 and len(adm_EmailAddr_val) <= 0:
                missing_configs.append("[%s], %s" % ("user_info", "enable_notify_admin"))
                missing_configs.append("[%s], %s" % ("user_info", "admin_email_addr"))
            elif (self.__config.getboolean("user_info", "enable_notify_admin") == True and
                len(adm_EmailAddr_val) <= 0):
                missing_configs.append("[%s], %s" % ("user_info", "admin_email_addr"))
            
            at_admin_config_sect = False
            counter = 0
            for sec in all_sections:
                all_options = self.__config.options(sec)
                for opt in all_options:
                    item = self.__config.get(sec, opt)
                    if opt == "admin_email_addr":
                        at_admin_config_sect = True
                    if len(item) <= 0: # empty string
                        # skip empty last_notify_time
                        if opt == "last_notify_time" or opt == "enable_notify_admin" or opt == "admin_email_addr": 
                            continue
                        else:
                            have_all_config = False
                            if not at_admin_config_sect:
                                missing_configs.insert(counter, "[%s], %s" % (sec, opt))
                                counter += 1
                            else: # at_admin_config_sect
                                missing_configs.append("[%s], %s" % (sec, opt))
            if len(missing_configs) == 0:
                have_all_config = True
                print("Config file is complete")
                logger.info("Config file is complete")
                break
            # prompt user to fill in config.ini
            for mis in missing_configs:
                print("Please fill in missing configuration: %s" % mis)
            input("Press any key to reload config.ini")
    
    # writting to config.ini
    def write_basic_info2Config(self):
        self.__config["user_info"] = user_info_arr
        self.__config["settings"] = settings_arr
        self.__config["notification_time"] = notification_time_arr
        with open("./config.ini", "w") as file:
            self.__config.write(file)
    
    def write2config(self, section, key, val):
        self.__config.set(section, key, val)
        with open("./config.ini", "w") as f:
            self.__config.write(f)
    
    # reading from config.ini
    def read_from_config(self, section):
        return self.__config.items(section)
    
    def read_from_config_key(self, section, key):
        return self.__config.get(section, key)
    
    
    def getMsgsFromFile(self):
        msg_filepath = self.__config.get("user_info", "messages_file_path")
        if msg_filepath == None:
            logger.warning("Canont open message file due to missing filepath")
            return None
        msg_str_arr = list()
        logger.info("Open message file: %s" % self.__config.get("user_info", "messages_file_path"))
        with open(msg_filepath, 'r', encoding="utf-8") as msg_file:
            # buffers
            msg_str = msg_file.read()
            pos1 = 0
            pos2 = 0
            # loop through whole file & search for message blocks
            counter = msg_str.find("begin]")
            while counter >= 0:
                counter += 6
                pos1 = msg_str.find("begin]", pos2)+6
                logger.info("Loading message block: %s" % (msg_str[msg_str.find("[",pos2+1):pos1-7]+"]"))
                pos2 = msg_str.find("[", pos1)
                msg_str_arr.append(msg_str[pos1:pos2])
                counter = msg_str.find("begin]", counter)
            msg_file.close()
        return msg_str_arr
    
    # setters
    
    def setLastNotifyTime(self, time):
        self.__config.set("notification_time", "last_notify_time", time.isoformat()[0:10])
    
    def setSentWklyEmail(self, flag):
        self.__config.set("settings", "sent_weekly_email", "true" if flag else "false")
    
    
    # getters
    
    # get config data
    def getConfig(self):
        if self.__config != None:
            return self.__config
        return None
    
    
    # user_info
    def getUserName(self):
        return self.__config.get("user_info", "contact_person_name")
    
    def getUserNum(self):
        return self.__config.get("user_info", "contact_person_number")
    
    def getUserEmailAddr(self):
        return self.__config.get("user_info", "sender_email_addr")
    
    def getUserEmailPsw(self):
        return self.__config.get("user_info", "sender_email_password")
    
    def isEnableNotiAdmin(self):
        return self.__config.get("user_info", "enable_notify_admin")
    
    def getAdminEmailAddr(self):
        return self.__config.get("user_info", "admin_email_addr")
    
    def getSpreadsheetID(self):
        return self.__config.get("user_info", "spreadsheet_id")
    
    def getSpreadsheetRange(self):
        return self.__config.get("user_info", "spreadsheet_range")
    
    def getMsgSbj(self):
        return self.__config.get("user_info", "message_subject")
    
    def getMsgFilePath(self):
        return self.__config.get("user_info", "messages_file_path")
    
    
    # settings
    def getWeeklyEmailCondition_bool(self):
        return self.__config.getboolean("settings", "sent_weekly_email")
    
    def getInternetConnection_bool(self):
        return self.__config.getboolean("settings", "internet_connection")
    
    def getWklyChkDay(self):
        return self.__config.get("settings", "weekly_checking_day")
    
    def getWklyChkTime(self):
        return self.__config.get("settings", "weekly_checking_time")
    
    def getSMTPserver(self):
        return self.__config.get("settings", "smtp_server")
    
    def getSleepTimeSec_int(self, curr_time):
        wkly_chk_day = self.__config.getint("settings", "weekly_checking_day")
        wkly_chk_time = self.__config.getint("settings", "weekly_checking_time")
        sent_wkly_email = self.__config.getboolean("settings", "sent_weekly_email")
        
        # get next notification datetime
        if curr_time.weekday() <= wkly_chk_day and not sent_wkly_email: # today is before/equal set wkly_chk_day (weekday)
            wkly_chk_day_datetime = datetime(curr_time.year, curr_time.month, curr_time.day)
            wkly_chk_day_datetime += timedelta(wkly_chk_day-curr_time.weekday())
        else: # today is after set wkly_chk_day (weekday)
            wkly_chk_day_datetime = datetime(curr_time.year, curr_time.month, curr_time.day)
            wkly_chk_day_datetime -= timedelta(curr_time.weekday()-wkly_chk_day)
            wkly_chk_day_datetime += timedelta(7)
        
        # add exact hh:mm:ss to next notification datetime
        wkly_chk_day_datetime += timedelta(0, wkly_chk_time)
        
        # get total seconds between next notification datetime and now
        sec = int((wkly_chk_day_datetime - curr_time).total_seconds())
        return sec
    
    
    # notification_time
    def getNotificationTime(self):
        return self.__config.items("notification_time")
    
    def getNotificationUpdateDay(self):
        return self.__config.getint("notification_time", "update_day")
    
    def getNotificationTime_wkDay(self):
        return int(self.__config.getint("notification_time", "week_day"))
    
    def getNotificationTime_WklyNotiAfter(self):
        return int(self.__config.getint("notification_time", "wkly_noti_after"))
    
    def getNotificationTime_NoNotiBef(self):
        return int(self.__config.getint("notification_time", "no_noti_before"))
    
    def getNotificationTime_NoNotiAft(self):
        return int(self.__config.getint("notification_time", "no_noti_after"))
    
    def getLastNotifyTime(self):
        temp = self.__config.get("notification_time", "last_notify_time")
        if temp != None and len(temp) > 0:
            return datetime.strptime(temp, "%Y-%m-%d").date()
        else: return None