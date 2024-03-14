import shutil

from config import *
from send_mail_birla import *
#from main import *
import os
import time

def move_image(image_path, destination_directory):
    shutil.move(image_path, destination_directory)

def check_directory(directory_path, destination_directory):
    while True:
        time.sleep(1)  # Wait for 1 second before checking again
        for filename in os.listdir(directory_path):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                print(f"Image found :: {filename}")
                image_path = os.path.join(directory_path, filename)
                if SEND_ALERT:
                    print(f"sending mail {filename}")
                    send_mail(image_path)
                    camera_vsq.vsq_logger.info('Mail sent')
                    print(f"sent mail {filename}")
                move_image(image_path, destination_directory)
                #print(f"{filename} moved to {destination_directory}")
directory_path = alert_image_check
destination_directory = alert_images_directory
check_directory(directory_path, destination_directory)
