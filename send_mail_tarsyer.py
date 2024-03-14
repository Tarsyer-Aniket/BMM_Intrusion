# Python code to illustrate Sending mail from

# your Gmail account


import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import random
import time
import logging

LOG_FILE_PATH = "send_mail.log"

logging.basicConfig(filename=LOG_FILE_PATH, format='%(asctime)s: %(levelname)s:  %(message)s', level=logging.INFO,
                    datefmt='%d/%m/%Y %I:%M:%S %p')


def send_mail(sender_email_id, password, mail_message, img_path, img_name):
    # creates SMTP session
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    # Create a secure SSL context
    context = ssl.create_default_context()
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email_id, password)
        receiver_email_id = ["hemant.ghuge@tarsyer.com", "aniket.tayade@tarsyer.com", "ashutosh.bhagwat@tarsyer.com"]
        # Setting up the mail
        message = MIMEMultipart("alternative")
        message["Subject"] = "Intrusion Entry found at BMM"
        message["From"] = sender_email_id
        message["To"] = ", ".join(receiver_email_id)
        # Attaching text
        mail_message += '\n'
        text = MIMEText(mail_message, "plain")
        message.attach(text)
        # New way of attaching Image
        f = open(img_path, 'rb')
        # set attachment mime and file name, the image type is png
        mime = MIMEBase('image', 'jpg', filename=img_name)
        # add required header data:
        mime.add_header('Content-Disposition', 'attachment', filename=img_name)
        mime.add_header('X-Attachment-Id', '0')
        mime.add_header('Content-ID', '<0>')
        # read attachment file content into the MIMEBase object
        mime.set_payload(f.read())
        # encode with base64
        encoders.encode_base64(mime)
        # add MIMEBase object to MIMEMultipart object
        message.attach(mime)
        # Old way of attaching an image
        # f = open(annealing_to_mill_img_path, 'rb')
        # img = f.read()
        # image_data = MIMEImage(img, name="Alert Image")
        # message.attach(image_data)
        # sending the mail
        server.sendmail(sender_email_id, receiver_email_id, message.as_string())
        return True


    except Exception as e:
        # Print any error messages to stdout
        logging.info(str(e))
        print(e)
        return False
    finally:
        server.quit()
        s = smtplib.SMTP('smtp.gmail.com', 587)


if __name__ == '__main__':
    sender_email_id = "tarsyer.alerts@gmail.com"
    sender_email_id_password = "rapeisqowzklgocg"
    msg = "Hey There , this is a test mail"
    img_path = r'Tarsyer_Logo_BrandName.png'
    img_name = 'logo'
    send_mail(sender_email_id, sender_email_id_password, msg, img_path, img_name)
