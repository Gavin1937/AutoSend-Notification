from urllib.request import urlopen
from datetime import datetime, timedelta
from pytz import timezone
import pytz


class TimeMonitor:
    
    # constructor
    def __init__(self):
        # declare
        self.__internet_connection_flag = None
        self.__time_flag = None
        self.__pdt_time = None
        # update object
        self.updateObj()
    
    # update time and all other boolean flags
    def updateObj(self):
        # update time
        
        # get utc time from url & check internet connection
        try:
            res = urlopen('http://just-the-time.appspot.com/')
            self.__internet_connection_flag = True
        except:
            self.__internet_connection_flag = False
        
        if self.__internet_connection_flag == True:
            result = res.read().strip()
            result_str = result.decode('utf-8')
            
            # convert string to datetime obj
            date_time_obj = datetime.strptime(result_str, '%Y-%m-%d %H:%M:%S')
            
            # set timezone
            self.__pdt_time = date_time_obj.astimezone(timezone('US/Pacific'))
            
            # Subtract 8 hours
            self.__pdt_time = self.__pdt_time - timedelta(hours=8)
            
            # set has_time flag
            self.__time_flag = True
    
    
    # getters
    
    def getDateTimeObj(self):
        if self.__internet_connection_flag == True:
            return self.__pdt_time
    
    def getDateTimeStr(self):
        if self.__internet_connection_flag == True:
            return self.__pdt_time.isoformat()
    
    def getDateTimeStr_ctime(self):
        if self.__internet_connection_flag == True:
            return self.__pdt_time.ctime()
    
    def hasInternetConnection(self):
        return self.__internet_connection_flag
    
    def hasTime(self):
        return self.__time_flag
