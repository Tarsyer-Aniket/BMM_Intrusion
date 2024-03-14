import os

CAMERA_NO = 1
VIDEO_INPUT = 'rtsp://admin:bmm%4012345@192.168.1.94/Streaming/Channels/201'
#VIDEO_INPUT = 'test.mp4'
file_fps = 25

SKIP_FRAME = 10

MIN_CONTOUR_AREA = 1
CONFIDENCE_THRESH = 0.4

MODEL_TYPE = 'TFLITE'

HEIGHT, WIDTH = 300, 300
MODEL_PATH = 'models/person_detect_mobilenet_v1.tflite'
    
INPUT_SHAPE = [HEIGHT, WIDTH]
print(INPUT_SHAPE)
DEBUG = True
VIDEO_WRITE = False
IMAGE_SHOW = True
IMAGE_WRITE = True
SEND_ALERT = False
CAPTURE_PERSON = False

MOTION_CONTROL = True     # Make it True to turn off the motion detector and run obj detector continuosly


alert_images_directory = "/tmp/BMM_unauthorised_entry" # successfully sent directory
alert_image_check = "/tmp/alert_check" # save
debug_images_directory = "/tmp/BMM_unauthorised_entry_debug"
person_check_directory = "/tmp/person_check_images"
if not os.path.exists(alert_images_directory):
    os.makedirs(alert_images_directory)
if not os.path.exists(debug_images_directory):
    os.makedirs(debug_images_directory)
if not os.path.exists(alert_image_check):
    os.makedirs(alert_image_check)
if not os.path.exists(person_check_directory):
    os.makedirs(person_check_directory)




if VIDEO_WRITE:
    if VIDEO_INPUT == 0:
        VIDEO_INPUT = 'webcam'
    output_filename = 'processed_video/'+VIDEO_INPUT.split('/')[-1].split('.')[0]+'_'+MODEL_TYPE+ '_' + str(CONFIDENCE_THRESH*100) + '_result2dev.mp4'

    saving_fps = file_fps/SKIP_FRAME
