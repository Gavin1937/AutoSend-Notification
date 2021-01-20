from configparser import ConfigParser
import os
from My_Logger import *


class ConfigManager:
    
    # default constructor
    def __init__(self):
        logger.info("Constructing ConfigManager object...")
        self.__config = ConfigParser()
        logger.info("Constructed self.__config")
        if os.path.exists("./config.ini\n") and os.path.getsize("./config.ini\n") > 0:
            logger.info("Cannot find config.ini, create & write basic info to a new file")
            self.write_basic_info2Config()
        else:
            logger.info("Found config.ini, read from it")
            self.__config.read("./config.ini")
    
    # writting to config.ini
    def write_basic_info2Config(self):
        self.__config["settings"] = {
            "internet_connection": "false",
            "sent_weekly_email": "false"
        }
        self.__config["notification_time"] = {
            "week_day": "2", # Wednesday
            "hour": "12"
        }
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
    
    
    # getters
    
    # get config data
    def getConfig(self):
        if self.__config != None:
            return self.__config
        return None
    
    def getWeeklyEmailCondition_bool(self):
        return self.__config.getboolean("settings", "sent_weekly_email")
    
    def getInternetConnection_bool(self):
        return self.__config.getboolean("settings", "internet_connection")
    
    def getNotificationTime(self):
        return self.__config.items("notification_time")
    
    def getNotificationTime_wkDay(self):
        return int(self.__config.get("notification_time", "week_day"))
    
    def getNotificationTime_hr(self):
        return int(self.__config.get("notification_time", "hour"))