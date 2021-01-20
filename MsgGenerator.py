

def getSermonMsg(name):
    output = """ 
%s，这周将会是你讲道，请记得准备好讲道的题目。
-----------------------------------------------------------------------------------------------------------------------------------
%s, you are the preacher of the sermon in this week,
please remember to prepare the sermon topic for the week.
            """ % (name, name)
    return output


def getWorshipMsg(name):
    output = """ 
%s，这周将会是你带敬拜，请记得准备好敬拜的歌曲。
-----------------------------------------------------------------------------------------------------------------------------------
%s, you are the leader of the worship in this week,
please remember to prepare the worship songs for the week.
            """ % (name, name)
    return output


def getFullEmailMsg(main_body_msg, contact_phone_num):
    output = """
%s



这是一封自动发送的提醒邮件，请勿回复此邮件。
如果您对此邮件的信息有任何的问题，请询问在 Whatsapp 上询问 Gavin
-----------------------------------------------------------------------------------------------------------------------------------
This is an auto-pushed notification email, please Do Not reply to this email.
If you have any question about this notification, please ask Gavin on Whatsapp
for help.

Gavin's phone #: %s
    """ % (main_body_msg, contact_phone_num)
    return output