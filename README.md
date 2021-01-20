# AutoSending Notification program

This program will send notification through Gmail automatically every week. 

<br>

You can modify the day to send notification in program generated config.ini file.

```
[settings]
sleep_time_sec = 21600  // sleep for how long, in second, before next time & internet checking


[notification_time]
week_day = 2            // week day to send email, from Mon~Sun (0~6)
hour = 12               // send email at which hour, from 0~23
min = 0                 // send email at which min, from 0~59
sec = 0                 // send email at which sec, from 0~59
```

<br>

Program Python module requirement:
* smtplib
* googleapiclient
* google
* urllib

<br>

This program requires several extra steps to be done before running:

1. Enable a service account for reading data from a Google Spreadsheet
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

2. Enable "Less secure app access" for the Gmail that you want to use as email sender
   * I recommend to use a secondary Gmail account as email sender
   * Enable in this link: https://myaccount.google.com/lesssecureapps

3. Set up a "contact_list.json" file
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

4. Configure "MsgGenerator.py" file, fill in your own messages