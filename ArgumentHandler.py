from My_Logger import logger


class ArgumentHandler:
    
    # constructor
    def __init__(self, argv):
        logger.info("Constructing ArgumentHandler object...")
        self.__send2all_msg = ""
        self.__hasSend2AllMsg_flag = False
        self.__hasHelp_flag = False
        for ind, args in enumerate(argv):
            if args != None:
                if args == "--send2all":
                    with open(argv[ind+1], 'r', encoding="utf-8") as msg_file:
                        logger.info("Get message from file: %s" % argv[ind+1])
                        self.__send2all_msg = msg_file.read()
                        if self.__send2all_msg != None:
                            self.__hasSend2AllMsg_flag = True
                if args == "-h" or args == "--help":
                    self.__hasHelp_flag = True
        logger.info("Finish construction, hasArg: [%r]" % self.hasArg())
    
    # getter
    
    def getSend2AllMsg(self):
        if len(self.__send2all_msg) > 0:
            return self.__send2all_msg
    
    def printHelp(self):
        print(
"""
    Arguments
    
    --send2all      Send email to all people in contact_list.json with a text file contains messages
                    Message text file don't need to have square brackets to indicate message blocks
                    So this file can only contain one message
                    Charactor '#' will be use to indicate contact person's refer_name in message text file
    
    syntax: python main.py --send2all [path_to_message_file.txt]
"""
        )
    
    def hasArg(self):
        flag = (
            self.hasSend2AllMsg() or
            self.hasHelp()
        )
        return flag
    
    def hasSend2AllMsg(self):
        return self.__hasSend2AllMsg_flag
    
    def hasHelp(self):
        return self.__hasHelp_flag