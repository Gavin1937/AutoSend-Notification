from urllib.request import urlopen
from datetime import datetime, timedelta
from pytz import timezone
import pytz

from My_Logger import *

class TimeMonitor:
    
    # constructor
    def __init__(self):
        logger.info("Constructing TimeMonitor object...")
        # declare
        self.__internet_connection_flag = None
        self.__time_flag = None
        self.__pst_time = None
        # update object
        logger.info("Updating TimeMonitor object")
        self.updateObj()
    
    # update time and all other boolean flags
    def updateObj(self):
        # update time
        
        # get utc time from url & check internet connection
        try:
            logger.info("Trying to open url to check time & internet connection")
            res = urlopen('http://just-the-time.appspot.com/')
            self.__internet_connection_flag = True
            logger.info("Successfully open url to check time & internet connection")
        except Exception as err:
            self.__internet_connection_flag = False
            logger.warning("Fail to open url to check time & internet connection. Exception: %s" % str(err))
            raise err
        
        if self.__internet_connection_flag == True:
            result = res.read().strip()
            result_str = result.decode('utf-8')
            
            # convert string to datetime obj
            date_time_obj = datetime.strptime(result_str, '%Y-%m-%d %H:%M:%S')
            
            # set timezone
            self.__pst_time = date_time_obj.astimezone(timezone('US/Pacific'))
            
            # Subtract 8 hours
            self.__pst_time = self.__pst_time - timedelta(hours=8)
            
            # set has_time flag
            self.__time_flag = True
            
            logger.info("Converted utc time to US/Pacific (PST) time")
    
    
    # getters
    
    def getDateTimeObj(self):
        if self.__internet_connection_flag == True:
            return self.__pst_time
    
    def getDateTimeStr(self):
        if self.__internet_connection_flag == True:
            return self.__pst_time.isoformat()
    
    def getDateTimeStr_ctime(self):
        if self.__internet_connection_flag == True:
            return self.__pst_time.ctime()
    
    def hasInternetConnection(self):
        return self.__internet_connection_flag
    
    def hasTime(self):
        return self.__time_flag
