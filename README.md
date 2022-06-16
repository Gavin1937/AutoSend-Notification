
# This repo is deprecated
## [Deprecate Reason: Google no longer support 3rd-party apps using email & password to send email](https://support.google.com/accounts/answer/6010255)

## You can use other scheduled notification services or check out my new repo [AutoNoti_GAS](https://github.com/Gavin1937/AutoNoti_GAS)


# AutoSending Notification program

This program will send notification through an email provider (like Gmail) automatically every week. 


## Python Version: 3.8.5

## Program Python Module Requirements:
* smtplib
* google-api-python-client
* google-auth-httplib2
* google-auth-oauthlib
* urllib
* ntplib (included .whl file in ./external_modules/)


## How to Run this program:

* Command:
```
python AutoSend_Notification.py
```

* You can call help menu with command:
```
python AutoSend_Notification.py -h
```

* Checkout [Argument List](#argument-list) for more info


## External requirements:


### **Enable a service account for reading data from a Google Spreadsheet**
   * You can refer to tutorial video: https://www.youtube.com/watch?v=4ssigWmExak
   * Go to: https://console.developers.google.com/apis/dashboard
   * Create a new project from left-upper corner
   * Once project is created, go back to this site
   * Find and click "ENABLE APIS AND SERVICES"
   * Search for "Google Sheets API" and enable it
   * Go back to this site again and then click on the "Credentials" tab on the left
   * Click on "CREATE CREDENTIALS" button and create a service account
   * Enter whatever name for your service account and then click on "CREATE
   * In the "Select a role" drop-down menu, select "Viewer" since this program will only read Google spreadsheet data. (You can choose "Editor" for both Read and Write permission)
   * And then click "CONTINUE" and "DONE" button
   * At this point, once you go back to "Credentials" page you should see the Service Account you just create
   * You need to copy your Service Account Email, and then share the Google spreadsheet that you want to use as schedule with this email
   * After that, click into the email url
   * In the new page, scroll down and find button "ADD KEY"
   * Click on that button and choose "Create New Key" and "JSON", and then "CREATE"
   * You will download a .json file. copy this file to the root directory of this repo, and then rename it to "credential_key.json"


### **Enable "Less secure app access" for the Gmail that you want to use as email sender**
   * You can SKIP this step if you don't want to use Gmail as email sender
   * I recommend to use a secondary Gmail account as email sender
   * Enable in this link: https://myaccount.google.com/lesssecureapps


### **Set up a "contact_list.json" file**
   * This is the list that this program will search for contact infos, program will also compare the names in the Google spreadsheet with names in "contact_list.json"
   * Sample "contact_list.json":
    
```json
    {
        "contact_list": [
            {
                "name": "Laura WoodsShubham",
                "refer_name": "Names That will be Called in Email",
                "email": "dafovu@cedte.an"
            },
            {
                "name": "Kate Hanson",
                "refer_name": "Names That will be Called in Email",
                "email": "benonid@tobu.lt"
            },
            {
                "name": "Leonard Gomez",
                "refer_name": "Names That will be Called in Email",
                "email": "atroda@ami.es"
            }
        ]
    }
```


## Customization Settings


### **You need to modify config.ini file for this program**

* Program will auto create a config.ini after you first time run it
* You need to fill in values for all the items thats not **[AutoGenerate]** and have no default value
* Please **DO NOT MODIFY ANY [AutoGenerate] VALUES**
* **config.ini default values**

```
[user_info]
    contact_person_name =             // Who to contact for questions
    contact_person_number =           // Phone number of this person
    sender_email_addr =               // Sender Email's address
    sender_email_password =           // Sender Email's password
    enable_notify_admin = true        // Whether send an email to notify contact_person (admin) after each email sending, default=true
    admin_email_addr =                // If enable_notify_admin=true, require an email for contact_person (admin)
    spreadsheet_id =                  // Id of Google Spreadsheet to read
    spreadsheet_range =               // Range of Google Spreadsheet to read
    message_subject =                 // Subject for all auto send emails
    messages_file_path =              // Path to text file that contains all message blocks

[settings]
    internet_connection = false       // [AutoGenerate] Whether have internet connection
                                      // **DO NOT MODIFY THIS VALUE**
    sent_weekly_email = false         // [AutoGenerate]  Whether sent current week's email
                                      // **DO NOT MODIFY THIS VALUE**
    weekly_checking_day = 2           // When to check time & internet connection in a week, (2 = Wednesday)
    weekly_checking_time = 43200      // When to check time & internet connection on "weekly_checking_day",
                                      // always start from 0sec of the day
                                      // if weekly_checking_day = 2 and weekly_checking_time = 43200
                                      // then program will check time & internet connection on every Wednesday 12:00:00
    smtp_server = smtp.gmail.com:587  // SMTP server:port, default to Google. (Find yours by google email_provider + smtp server port)

[notification_time]
    update_day = 0                    // When to refresh notification flag for a new week, (0 = Monday)
    week_day = 2                      // When to send notification, (2 = Wednesday)
    wkly_noti_after = 43200           // When to send notification, value is in seconds in a day (43200=12pm,12)
    no_noti_before = 25200            // Stop sending notification before this time, value is in seconds in a day (25200=7am,7)
    no_noti_after = 79200             // Stop sending notification after this time, value is in seconds in a day (79200=10pm,22)
    last_notify_time =                // [AutoGenerate] Record of last notification time, auto set by program
                                      // **DO NOT MODIFY THIS VALUE**
```

* You can see which item is missing when running the program



### **Messages**

* Messages in email will be load from a text file like "message.txt"
* A message file should contain messages as blocks
* **A message block need to start with keyword: [MessageBlock Name begin]**
* **A message block need to end with keyword: [MessageBlock Name end]**
* **2 keywords must start and end with square brackets**
* You can insert your messages between 2 keywords
* **You should modify "MsgGenerator.py" file to satisfy your needs for auto-generated messages**
* messages.txt example:
```
[full message begin]
#



line 1
line 2
-----------------------------------------------------------------------------------------------------------------------------------
line 3

Phone No.: #
[full message end]
```
* I use "#" as indicator for functions in "MsgGenerator.py" to replace with other strings, but you can change that base on your prefer



### **Google Spreadsheet Format**

* Function __find_curr_year_column() in class Schedule is responsible to process 2-D array __values of the class
* You should modify __find_curr_year_column() function to fit your Google Spreadsheet format


### **Log File**

* Log file is "AutoSend_Notification.log"
* Log file have size **limitation of 5MB**, and will **backup 1 file**, so **totally 10MB of size limit**
* You can edit this size limitation in "My_Logger.py" file, in RotatingFileHandler(), maxBytes= 


## Program Arguments

### Argument List
```
    Arguments
    
    --send2all          Send email to all people in contact_list.json with a text file contains messages
                        Message text file don't need to have square brackets to indicate message blocks
                        So this file can only contain one message
                        Charactor '#' will be use to indicate contact person's refer_name in message text file
    
    syntax: python main.py --send2all [path_to_message_file.txt]
    
    --sheet-col         Print column in the Google Spreadsheet for current week
    
    -h, --help          Print this help message
```

