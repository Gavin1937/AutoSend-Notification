import json 

# store all contact info on RAM
class Contact:
    
    # constructor
    def __init__(self):
        
        self.__file_exist_flag = True
        self.__contact_list = list()
        
        # Opening JSON file 
        try:
            f = open('contact_list.json',) 
        except:
            self.__file_exist_flag = False
            raise Exception("Cannot Open file \"contact_list.json\" under current directory")
        
        if self.__file_exist_flag == True:
            # returns JSON object as  
            # a dictionary 
            data = json.load(f) 
        
            # load all data to __contact_list
            for i in data['contact_list']: 
                self.__contact_list.append(i)
        
            # Closing file 
            f.close() 
    
    
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
    
    def getData(self):
        if self.__file_exist_flag == True:
            return self.__contact_list
    
    