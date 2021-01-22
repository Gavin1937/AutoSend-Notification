import json 
from My_Logger import logger

# store all contact info on RAM
class Contact:
    
    # constructor
    def __init__(self):
        logger.info("Constructing Contact object...")
        self.__file_exist_flag = True
        self.__contact_list = list()
        
        # Opening JSON file 
        try:
            logger.info("Trying to open contact_list.json")
            f = open('contact_list.json',) 
            logger.info("Successfully open contact_list.json")
        except:
            logger.warning("Cannot open contact_list.json. Exception: Cannot Open file \"contact_list.json\" under current directory")
            self.__file_exist_flag = False
            raise Exception("Cannot Open file \"contact_list.json\" under current directory")
        
        if self.__file_exist_flag == True:
            # returns JSON object as  
            # a dictionary 
            data = json.load(f) 
            logger.info("Load contact_list.json as a dictionary")
            
            # load all data to __contact_list
            logger.info("Load all data to self.__contact_list")
            for i in data['contact_list']: 
                self.__contact_list.append(i)
            logger.info("All data loaded")
            
            # Closing file 
            f.close() 
            logger.info("Closing contact_list.json")
    
    
    # find function
    def findContact(self, name):
        for i in self.__contact_list:
            if i["name"] == name:
                return i
        return None
    
    # find email w/ a name
    def findEmail(self, name):
        person = self.findContact(name)
        if person != None:
            return person["email"]
        else:
            return None
    
    # find refer name w/ a name
    def findReferName(self, name):
        person = self.findContact(name)
        if person != None:
            return person["refer_name"]
        else:
            return None
    
    
    # boolean flags
    
    def isFileExist(self):
        return self.__file_exist_flag
    
    
    
    # getter
    
    def getContactList(self):
        if self.__file_exist_flag == True:
            return self.__contact_list
    
    