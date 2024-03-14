from datetime import datetime, timedelta
import logging
import csv
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
import os
import mimetypes
import pandas as pd

LOG_FILE_PATH="email.log"
logging.basicConfig(filename=LOG_FILE_PATH, format='%(asctime)s: %(levelname)s:  %(message)s', level=logging.INFO, datefmt='%d/%m/%Y %I:%M:%S %p')

def send_mail(PATH_TO_IMAGE):

    sender_email="tarsyer.alerts@gmail.com"
    sender_email_password="rapeisqowzklgocg"

    # creates SMTP session 
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, sender_email_password)
        # receiver_email_id=["msshaktawat@birlacorp.com", "Sumantra.Naik@birlacorp.com", "Priykant.Upadhyay@birlacorp.com", "Vinod.Paliwal@birlacorp.com", "amit.tanwar@birlacorp.com", "thomas.cheriyan@birlacorp.com", "vinod.s.kumar@birlacorp.com", "naveen.pachauri@birlacorp.com", "ashutosh.shrivastava@birlacorp.com", "rameshwar.gadri@birlacorp.com", "bhupesh.sharma@birlacorp.com"]
        # cc_email_id=["ashutosh.bhagwat@tarsyer.com", "aniket.tayade@tarsyer.com", "hemant.ghuge@tarsyer.com", "vnayar@tarsyer.com"]

        receiver_email_id = ["aniket.tayade@tarsyer.com", "hemant.ghuge@tarsyer.com", "ashutosh.bhagwat@tarsyer.com", "vnayar@tarsyer.com"]
        cc_email_id = ["aniket.tayade@tarsyer.com"]


        # Setting up the mail
        message = MIMEMultipart("alternative")
        message["Subject"] = "BMMTop Project - Intrusion entry found at BMM-Top"
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_email_id)
        message["Cc"] = ", ".join(cc_email_id)

        # Attaching text
        mail_message = '<p><b>Intrusion Zone Entry Alert</b>, </p><p>Person found in Intrusion zone area at BMM-Top</p><p>Tarsyer Insights</p>'
        text = MIMEText(mail_message, "html")
        text.add_header('Content-Type','text/html')
        message.attach(text)

        ctype, encoding = mimetypes.guess_type(PATH_TO_IMAGE)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'

        maintype, subtype = ctype.split('/', 1)
        with open(PATH_TO_IMAGE, 'rb') as fp:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())

        # Encode the payload using Base64
        encoders.encode_base64(msg)
        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=str(PATH_TO_IMAGE).split('/')[-1])
        message.attach(msg)
        # Now send or store the message
        composed = message.as_string()

        # sending the mail 
        server.sendmail(sender_email, receiver_email_id+cc_email_id, composed)
        logging.info('mail sent successfully')


    except Exception as e:
        # Print any error messages to stdout
        logging.info(str(e))
        print(e)
    finally:
        server.quit() 
        s = smtplib.SMTP('smtp.gmail.com', 587) 


#send mail
#PATH_TO_IMAGE = '1.jpg'
#send_mail(PATH_TO_IMAGE)
