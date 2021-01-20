import smtplib

from My_Logger import *

# This class is created with tutorial from:
# YouTube Video: https://www.youtube.com/watch?v=mP_Ln-Z9-XY
class EmailSender:
    
    # constructor
    def __init__(self, email_addr, password):
        logger.info("Constructing EmailSender object...")
        # declare
        self.__email_addr = None
        self.__email_password = None
        self.__server = None
        try:
            logger.info("Setting SMTP server...")
            self.setServer(email_addr, password)
        except Exception as err:
            logger.warning("Something wrong during setting SMTP server. Exception:%s" % str(err))
            raise err
    
    # destructor
    def __del__(self):
        self.__server.quit()
        logger.info("Destruct EmailSender object & Quit from SMTP server")
    
    # set server interface, also can re-login to an email
    def setServer(self, email_addr, password):
        if email_addr != None:
            self.__email_addr = email_addr
        if password != None:
            self.__email_password = password
        try:
            logger.info("Trying to set up SMTP server")
            
            self.__server = smtplib.SMTP("smtp.gmail.com:587")
            logger.info("Set up SMTP server domain:port")
            
            self.__server.ehlo()
            logger.info("Identify to Gmail ESMTP server")
            
            self.__server.starttls()
            logger.info("Put the SMTP connection in TLS (Transport Layer Security) mode")
            
            self.__server.login(self.__email_addr, self.__email_password)
            logger.info("Login to Gmail")
            logger.info("Successfully set up SMTP server")
            
        except Exception as err:
            logger.warning("Something is wrong during setting up SMTP server. Exception: %s" % str(err))
            raise err
    
    # send email
    def sendEmail(self, to_email_addr, email_subj, email_msg):
        try:
            logger.info("Trying to send an email")
            if to_email_addr != None and email_subj != None and email_msg != None:
                whole_email_msg = "Subject: {}\n\n{}".format(email_subj, email_msg)
                self.__server.sendmail(self.__email_addr, to_email_addr, whole_email_msg.encode("utf8"))
                logger.info("Sent email with SMTP sendmail()")
        except Exception as err:
            logger.warning("Fail to send email. Exception: %s" % str(err))
            raise err
    
    # getters
    
    def getEmailAddr(self):
        return self.__email_addr
    
    def getEmailPassword(self):
        return self.__email_password