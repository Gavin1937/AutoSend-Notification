import logging

# Create an configure logger
LOG_FORMAT = "[%(levelname)s][%(asctime)s]:%(funcName)s - %(message)s"
logging.basicConfig(filename = "./AutoSend_Notification.log",
                    level = logging.DEBUG,
                    format = LOG_FORMAT)
logger = logging.getLogger()
