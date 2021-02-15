from urllib.request import urlopen
from datetime import datetime, timedelta
import time
from time import mktime
from pytz import timezone
import pytz

# external module
import ntplib

from My_Logger import logger

class TimeMonitor:
    
    # constructor
    def __init__(self):
        logger.info("Constructing TimeMonitor object...")
        # declare
        self.__internet_connection_flag = None
        self.__time_flag = None
        self.__pst_time = None
        # update object
        try:
            logger.info("Trying to update TimeMonitor object")
            self.updateTime()
        except Exception as err:
            logger.warning(f"Cannot update TimeMonitor object. Exception: {str(err)}")
            raise err
    
    # update time and all other boolean flags
    def updateTime(self):
        # update time
        output_err = None
        
        # get utc time from url & check internet connection
        try:
            logger.info("Trying to open url to check time & internet connection with ntplib")
            logger.info("Create NTPClient")
            client = ntplib.NTPClient()
            logger.info("Requesting time form \"pool.ntp.org\"")
            response = client.request('pool.ntp.org')
            logger.info("Setting datetime object and internet_connection_flag")
            t = time.localtime(response.tx_time)
            self.__pst_time = datetime.fromtimestamp(mktime(t))
            self.__internet_connection_flag = True
            self.__time_flag = True
            output_err = None
        except Exception as err:
            self.__internet_connection_flag = False
            logger.warning(f"Cannot sync with time server. Exception: {str(err)}")
            output_err = err
        
        if output_err != None:
            logger.info("Fail to check time & internet with ntplib, try with url")
            try:
                logger.info("Trying to open url to check time & internet connection with url")
                res = urlopen('http://just-the-time.appspot.com/')
                self.__internet_connection_flag = True
                logger.info("Successfully open url to check time & internet connection")
            except Exception as err:
                self.__internet_connection_flag = False
                logger.warning(f"Fail to open url to check time & internet connection. Exception: {str(err)}")
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
