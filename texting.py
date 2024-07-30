import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import re

#Function that is used to validate whether a phone number adhers to 10 digit format
def phone_check(phone_number):
    pattern = re.compile(r'^\d{10}$')
    return bool(pattern.match(phone_number))

#Function that is used to send a text message to a user
def text_to_user(phone_number, carrier, name, bio):

    #Check whether phone number is valid
    temp = phone_check(phone_number)

    if temp == False:
        print("This is not a standard 10 digit phone number")
        return 0
    else:

        if carrier == "Verizon":
            msg_append = "@vtext.com"
        elif carrier == "AT&T":
            msg_append = "@txt.att.net"
        elif carrier == "Tmobile":
            msg_append = "@tmomail.net"
        else:
            print("Phone carrier not supported")
            return 0
        
        to = phone_number + msg_append
        
        #Load environment variables from env file
        load_dotenv()
        user = os.getenv('HOST_EMAIL')
        password = os.getenv('APP_PASSWORD')

        #Set up message contents
        msg = EmailMessage()
        msg.set_content(bio)
        msg['subject']= f"{name} has been identified"
        msg['to'] = to

        #Send message
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(user,password)

        server.quit()

        return 1
