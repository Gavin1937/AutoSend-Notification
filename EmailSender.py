import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# This class is created with tutorial from:
# YouTube Video: https://www.youtube.com/watch?v=mP_Ln-Z9-XY
class EmailSender:
    
    # constructor
    def __init__(self, email_addr, password):
        # declare
        self.__email_addr = None
        self.__email_password = None
        self.__server = None
        try:
            self.setServer(email_addr, password)
        except Exception as err:
            raise err
    
    # destructor
    def __del__(self):
        self.__server.quit()
    
    # set server interface, also can re-login to an email
    def setServer(self, email_addr, password):
        if email_addr != None:
            self.__email_addr = email_addr
        if password != None:
            self.__email_password = password
        try:
            self.__server = smtplib.SMTP("smtp.gmail.com:587")
            self.__server.ehlo()
            self.__server.starttls()
            self.__server.login(self.__email_addr, self.__email_password)
        except Exception as err:
            raise err
    
    # send email
    def sendEmail(self, to_email_addr, email_subj, email_msg):
        try:
            if to_email_addr != None and email_subj != None and email_msg != None:
                whole_email_msg = "Subject: {}\n\n{}".format(email_subj, email_msg)
                self.__server.sendmail(self.__email_addr, to_email_addr, whole_email_msg.encode("utf8"))
        except Exception as err:
            raise err
    
    # getters
    
    def getEmailAddr(self):
        return self.__email_addr
    
    def getEmailPassword(self):
        return self.__email_password