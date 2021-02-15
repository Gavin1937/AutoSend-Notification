from My_Logger import logger

# This class is created with tutorial from:
# YouTube Video: https://www.youtube.com/watch?v=mP_Ln-Z9-XY
class EmailSender:
    
    # constructor
    def __init__(self, email_addr, password, SMTP_server):
        # import libs
        import smtplib
        
        logger.info("Constructing EmailSender object...")
        # declare
        self.__email_addr = email_addr
        self.__email_password = password
        self.__server_url = SMTP_server
        self.__server = smtplib.SMTP()
        try:
            logger.info("Setting SMTP server...")
            self.setServer(self.__email_addr, self.__email_password, self.__server_url)
        except Exception as err:
            logger.warning(f"Something wrong during setting SMTP server. Exception: {str(err)}")
            raise err
    
    # destructor
    def __del__(self):
        self.__server.quit()
        logger.info("Destruct EmailSender object & Quit from SMTP server")
    
    # set server interface, also can re-login to an email
    def setServer(self, email_addr, password, SMTP_server):
        # import libs
        import smtplib
        
        if email_addr != None:
            self.__email_addr = email_addr
        if password != None:
            self.__email_password = password
        try:
            logger.info("Trying to set up SMTP server")
            
            self.__server = smtplib.SMTP(SMTP_server)
            logger.info("Set up SMTP server domain:port")
            
            self.__server.ehlo()
            logger.info("Identify to Gmail ESMTP server")
            
            self.__server.starttls()
            logger.info("Put the SMTP connection in TLS (Transport Layer Security) mode")
            
            self.__server.login(self.__email_addr, self.__email_password)
            logger.info("Login to Gmail")
            logger.info("Successfully set up SMTP server")
            
        except Exception as err:
            logger.warning(f"Something is wrong during setting up SMTP server. Exception: {str(err)}")
            raise err
    
    # reconnect to SMTP server
    def reconnect(self):
        self.disconnect()
        try:
            logger.info("Reconnecting to SMTP server...")
            self.setServer(self.__email_addr, self.__email_password, self.__server_url)
        except Exception as err:
            logger.warning(f"Something wrong during reconnecting SMTP server. Exception:{str(err)}")
            raise err
    
    # disconnect from SMTP server
    def disconnect(self):
        logger.info("Disconnect to SMTP server")
        self.__server.close()
    
    # send email
    def sendEmail(self, to_email_addr, email_subj, email_msg):
        try:
            logger.info("Trying to send an email")
            if to_email_addr != None and email_subj != None and email_msg != None:
                whole_email_msg = f"Subject: {email_subj}\n\n{email_msg}"
                self.__server.sendmail(self.__email_addr, to_email_addr, whole_email_msg.encode("utf8"))
                logger.info("Sent email with SMTP sendmail()")
        except Exception as err:
            logger.warning(f"Fail to send email. Exception: {str(err)}")
            raise err
    
    
    # getters
    
    def getEmailAddr(self):
        return self.__email_addr
    
    def getEmailPassword(self):
        return self.__email_password