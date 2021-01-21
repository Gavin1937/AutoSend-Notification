from configparser import ConfigParser
import os
from datetime import datetime, timedelta
from My_Logger import *


# global variables
user_info_arr = {
    "contact_person_name": "",
    "contact_person_number": "",
    "sender_email_addr": "",
    "sender_email_password": "",
    "spreadsheet_id": "",
    "spreadsheet_range": "",
    "messages_file_path": ""
}
settings_arr = {
    "internet_connection": "false",
    "sent_weekly_email": "false",
    "daily_checking_num": "4" # how many times to check time & internet connection in a day, cannot be 0
}
notification_time_arr = {
    "update_day": "0", # When to refresh notification flag for a new week, (0 = Monday)
    "week_day": "2", # When to send notification, (2 = Wednesday)
    "wkly_noti_after": "43200", # When to send notification, value is in seconds in a day (43200=12pm,12)
    "no_noti_before": "25200", # Stop sending notification before this time, value is in seconds in a day (25200=7am,7)
    "no_noti_after": "79200", # Stop sending notification after this time, value is in seconds in a day (79200=10pm,22)
    "last_notify_time": "" # Record of last notification time, auto set by program
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
    
    def getSpreadsheetID(self):
        return self.__config.get("user_info", "spreadsheet_id")
    
    def getSpreadsheetRange(self):
        return self.__config.get("user_info", "spreadsheet_range")
    
    def getMsgFilePath(self):
        return self.__config.get("user_info", "messages_file_path")
    
    
    # settings
    def getWeeklyEmailCondition_bool(self):
        return self.__config.getboolean("settings", "sent_weekly_email")
    
    def getInternetConnection_bool(self):
        return self.__config.getboolean("settings", "internet_connection")
    
    def getDlyChkNum(self):
        return self.__config.get("settings", "daily_checking_num")
    
    def getSleepTimeSec_int(self):
        sec = (24*3600) / self.__config.getint("settings", "daily_checking_num")
        return int(sec)
    
    
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
        return datetime.strptime(self.__config.get("notification_time", "last_notify_time"), "%Y-%m-%d").date()