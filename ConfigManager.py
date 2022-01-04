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
def sec2datetime(seconds: int) -> datetime:
    """Convert seconds into datetime since 1970"""
    sec = timedelta(seconds)
    return (datetime(1,1,1) + sec)

def datetime2sec(date: datetime) -> int:
    """Get total seconds since start of input date"""
    if date != None:
        total_sec = date.second + (date.minute*60) + (date.hour*3600)
        return int(total_sec)
    else: return 0

# get current system time string fmt=%Y-%m-%d %H:%M:%S.%f
def getSysTimeStr():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


class ConfigManager:
    
    # default constructor
    def __init__(self):
        # import libs
        import os
        from configparser import ConfigParser
        
        logger.info("Constructing ConfigManager object...")
        self.__config = ConfigParser()
        self.__config_allset = False
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
        
        # checking config.ini status
        self.check_config()
    
    
    # check config.ini completion & logic
    def check_config(self):
        # check config.ini
        logger.info("Checking config file")
        while True:
            self.__config_allset = True
            self.update_config()
            
            # prompt user to fill in config.ini
            for mis in self.__check_config_missing():
                print(f"[{getSysTimeStr()}] - Please fill in missing configuration: {mis}")
            for lg in self.__check_config_logic():
                print(f"[{getSysTimeStr()}] - {lg}")
            
            if not self.__config_allset:
                input("Press any key to reload config.ini")
            else:
                print(f"[{getSysTimeStr()}] - Config file is complete")
                logger.info("Config file is complete")
                break
    
    def update_config(self):
        """Write data in RAM to config.ini to update it"""
        logger.info("Update config.ini")
        file = open("./config.ini", 'w')
        self.__config.write(file)
        file.close()
    
    def reload_config(self):
        """Read data from config.ini to reload config in RAM"""
        logger.info("Reload config.ini")
        self.__config.read("./config.ini")
    
    def update_reload_config(self):
        self.update_config()
        self.reload_config()
    
    # checking config.ini missing
    def __check_config_missing(self):
        missing_configs = list()
        
        # process admin notification configs
        enable_notiAdm_val = self.__config.get("user_info", "enable_notify_admin")
        adm_EmailAddr_val = self.__config.get("user_info", "admin_email_addr")
        if len(enable_notiAdm_val) <= 0 and len(adm_EmailAddr_val) <= 0:
            missing_configs.append("[user_info], enable_notify_admin")
            missing_configs.append("[user_info], admin_email_addr")
        elif (self.__config.getboolean("user_info", "enable_notify_admin") == True and
            len(adm_EmailAddr_val) <= 0):
            missing_configs.append("[user_info], admin_email_addr")
        
        at_admin_config_sect = False
        counter = 0
        for sec in self.__config.sections():
            for opt in self.__config.options(sec):
                item = self.__config.get(sec, opt)
                if opt == "admin_email_addr":
                    at_admin_config_sect = True
                if len(item) <= 0: # empty string
                    # skip empty last_notify_time
                    if opt == "last_notify_time" or opt == "enable_notify_admin" or opt == "admin_email_addr": 
                        continue
                    else:
                        if not at_admin_config_sect:
                            missing_configs.insert(counter, f"[{sec}], {opt}")
                            self.__config_allset = False
                            counter += 1
                        else: # at_admin_config_sect
                            missing_configs.append(f"[{sec}], {opt}")
                            self.__config_allset = False
        
        return missing_configs
    
    # check logic in config.ini options
    def __check_config_logic(self):
        msg = list()
        
        if (self.getWeeklyEmailCondition_bool() == True and
            self.getLastNotifyTime() == None):
            msg.append("[notification_time], last_notify_time cannot be empty if [settings], sent_weekly_email = true.")
            self.__config_allset = False
        
        return msg
    
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
        logger.info(f"Open message file: {self.__config.get('user_info', 'messages_file_path')}")
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
                logger.info(f"Loading message block: {msg_str[msg_str.find('[',pos2+1):pos1-7]}]")
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
        last_notitime = datetime.strptime(
            self.__config.get("notification_time", "last_notify_time"),
            "%Y-%m-%d"
        )
        next_updatetime = curr_time
        
        if sent_wkly_email and curr_time > last_notitime: # already sent this week's email
            # calc how many days to next week's checking date
            weekday_counter = 1
            while True:
                if ((curr_time.weekday()+weekday_counter) % 7) == wkly_chk_day:
                    break
                weekday_counter += 1
            
            tmp = curr_time + timedelta(seconds=weekday_counter*24*3600)
            next_updatetime = datetime(tmp.year, tmp.month, tmp.day) + timedelta(seconds=wkly_chk_time)
            
        else: # did not sent this week's email
            wkly_noti_after = self.__config.getint("notification_time", "wkly_noti_after")
            no_noti_before = self.__config.getint("notification_time", "no_noti_before")
            no_noti_after = self.__config.getint("notification_time", "no_noti_after")
            curr_sec = datetime2sec(curr_time)
            
            # find next avaliable time
            if ((curr_sec >= no_noti_before) and
                (curr_sec <= no_noti_after) and
                (curr_sec >= wkly_noti_after)
            ): # current time within a day's avaliable sending time
                # update now
                return 0
                
            else: # current time is out of a day's avaliable sending time
                # update in tomorrow at wkly_noti_after time
                next_updatetime = (
                    datetime(curr_time.year, curr_time.month, curr_time.day) +
                    timedelta(seconds=24*3600) + timedelta(seconds=wkly_noti_after)
                )
        
        # get total seconds between next notification datetime and now
        sec = int((next_updatetime - curr_time).total_seconds()) + 1
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