

def getSermonMsg(message_block, name):
    output = message_block
    output = output.replace("#", name)
    return output


def getWorshipMsg(message_block, name):
    output = message_block
    output = output.replace("#", name)
    return output


def getFullEmailMsg(message_block, main_body_msg, contact_email):
    output = message_block
    output = output.replace("#", main_body_msg, 1)
    output = output.replace("#", contact_email)
    return output
