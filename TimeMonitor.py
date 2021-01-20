from urllib.request import urlopen
from datetime import datetime, timedelta
from pytz import timezone
import pytz


class TimeMonitor:
    
    # constructor
    def __init__(self):
        self.updateObj()
    
    # update time and all other boolean flags
    def updateObj(self):
        # update time
        
        # get utc time from url & check internet connection
        try:
            res = urlopen('http://just-the-time.appspot.com/')
            self.__internet_connection = True
        except:
            self.__internet_connection = False
        
        if self.__internet_connection == True:
            result = res.read().strip()
            result_str = result.decode('utf-8')
            
            # convert string to datetime obj
            date_time_obj = datetime.strptime(result_str, '%Y-%m-%d %H:%M:%S')
            
            # set timezone
            self.__pdt_time = date_time_obj.astimezone(timezone('US/Pacific'))
            
            # Subtract 8 hours
            self.__pdt_time = self.__pdt_time - timedelta(hours=8)
            
            # set has_time flag
            self.__time = True
    
    
    # getters
    
    def getDateTimeObj(self):
        if self.__internet_connection == True:
            return self.__pdt_time
    
    def getDateTimeStr(self):
        if self.__internet_connection == True:
            return self.__pdt_time.isoformat()
    
    def getDateTimeStr_ctime(self):
        if self.__internet_connection == True:
            return self.__pdt_time.ctime()
    
    def hasInternatConnection(self):
        return self.__internet_connection
    
    def hasTime(self):
        return self.__time