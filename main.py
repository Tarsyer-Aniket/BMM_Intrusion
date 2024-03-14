import cv2
import numpy as np
import subprocess as sp
import shlex

from config import *
from video_stream_queue import *
from SSD_TfLite_Detector import *
from centroid_tracker import *
from datetime import datetime
from centroid_check import *
from send_mail_tarsyer import *
from motion_detect import *
from nms import *
from send_mail_birla import *

# Adding logo
LOGO = cv2.imread('Tarsyer_Logo_BrandName.png', -1)
print(LOGO.shape)
LOGO = cv2.resize(LOGO, (100, 100))
y1, y2 = 210, 310
x1, x2 = 0, 100
alpha_s = LOGO[:, :, 3]/255.0
alpha_l = 1.0-alpha_s


camera_vsq = VideoStreamQueue(VIDEO_INPUT, SKIP_FRAME, CAMERA_NO)
# video_cap = cv2.VideoCapture(0)
# video_cap.set(cv2.CAP_PROP_FPS, 10)
# CAMERA_FPS = video_cap.get(cv2.CAP_PROP_FPS)
# CAMERA_FPS = 30 (expected for webcam)
camera_vsq.vsq_logger.info('VSQ in progress')
camera_vsq.start()
total_frame_count = camera_vsq.stream.get(cv2.CAP_PROP_FRAME_COUNT)
print('total_frame_count = {}'.format(total_frame_count))

# Initializing centroid tracker and detector
centroid_tracker = CentroidTracker()
object_detector = SSD_TfLite_Detection(CONFIDENCE_THRESH, MODEL_PATH)


if DEBUG:
    startTime = time.monotonic()
    counter = 0
    fps = 0

if VIDEO_WRITE:
    # Open ffmpeg application as sub-process
    # FFmpeg input PIPE: RAW images in BGR color format
    # FFmpeg output MP4 file encoded with HEVC codec.
    # Arguments list:
    # -y                   Overwrite output file without asking
    # -s {width}x{height}  Input resolution width x height (1344x756)
    # -pixel_format bgr24  Input frame color format is BGR with 8 bits per color component
    # -f rawvideo          Input format: raw video
    # -r {fps}             Frame rate: fps (25fps)
    # -i pipe:             ffmpeg input is a PIPE
    # -vcodec libx265      Video codec: H.265 (HEVC)
    # -pix_fmt yuv420p     Output video color space YUV420 (saving space compared to YUV444)
    # -crf 24              Constant quality encoding (lower value for higher quality and larger output file).
    # {output_filename}    Output file name: output_filename (output.mp4)
    process = sp.Popen(shlex.split(f'/usr/bin/ffmpeg -y -s {WIDTH}x{HEIGHT} -pixel_format bgr24 -f rawvideo -r {saving_fps} -i pipe: -vcodec libx264 -pix_fmt yuv420p -crf 24 {output_filename}'), stdin=sp.PIPE)


camera_vsq.vsq_logger.info('CODE STARTED')

# Initializing all parameters
frame_counter = 0
person_counter = 0
send_api_alert_time_una = time.monotonic() - 60
Intrusion_entry_alert_interval = 60                  # alert interval set on 30 sec
Intrusion_entry_count = 0
motion_confirm = False
motion_thresh_counter = 0
MOTION_CONFIRM_THRESH = 3                               # it will check for motion change for 3 times
prev_frame_time = time.time() - 5000
no_detection_output_counter = 0
NO_OBJECT_THRESH = 3                                    # it will check if no object is there for 3 times
person_check = True

#Intrusion_entry_points = np.array([[80, 4], [53, 85], [106, 119], [173, 164], [251, 229], [298, 126], [267, 82], [203, 54], [137, 25], [80, 4] ], np.int32)
Intrusion_entry_points = np.array([[14, 187], [150, 187], [166, 235], [15, 233], [14, 187]], np.int32)
sender_email_id = "tarsyer.alerts@gmail.com"
sender_email_id_password = "rapeisqowzklgocg"

#alert_images_directory = "/tmp/BMM_unauthorised_entry" # successfully sent directory
#alert_image_check = "/tmp/alert_check" # save
#debug_images_directory = "/tmp/BMM_unauthorised_entry_debug"
#if not os.path.exists(alert_images_directory):
#    os.makedirs(alert_images_directory)
#if not os.path.exists(debug_images_directory):
#    os.makedirs(debug_images_directory)
#if not os.path.exists(alert_image_check):
#    os.makedirs(alert_image_check)

while True:
    current_time = datetime.now()
    current_hour = current_time.hour
    if current_hour >= 19 or current_hour < 8:
        # its night time; will stop service files
        os.system("systemctl --user stop Intrusion.service &")
        os.system("systemctl --user stop Intrusion_mail.service &")
    else:
        camera_dict = camera_vsq.read()
        camera_status = camera_dict['camera_status']
        curr_time = time.time()

        # Will turn off motion detector when its True
        if MOTION_CONTROL:
            motion_confirm = True

        # ret, frame = video_cap.read()
        if camera_status:
        # if ret:
            resized_frame, big_frame = camera_dict['image']
            # print(resized_frame.shape)
            # print(big_frame.shape)
            frame_counter += 1
            #if frame_counter >= (total_frame_count/SKIP_FRAME):
            #    break
            if curr_time - prev_frame_time > 60:
                prev_frame_time = curr_time
                base_frame = resized_frame.copy()
                # print('saving previous frame.')
                logging.info('Changing previous frame for motion detector')

            if DEBUG:
                counter += 1
                current_time = time.monotonic()

                if (current_time - startTime) > 100:
                    fps = counter / (current_time-startTime)
                    counter = 0
                    startTime = current_time
                    print('FPS = {}'.format(round(fps, 2)))

            # Draw the Roi on resized frame
            cv2.polylines(resized_frame, [Intrusion_entry_points], True, (255), 2)

            if not motion_confirm:
                cv2.putText(resized_frame, "Motion detector", (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 100), 1)
                returned_status, _, _ = motion_detection(base_frame, resized_frame, MIN_CONTOUR_AREA)
                if returned_status:
                    motion_thresh_counter += 1
                    print("Motion Detected")

                    if motion_thresh_counter == MOTION_CONFIRM_THRESH:
                        motion_thresh_counter = 0
                        motion_confirm = True
                        person_check = True
                        camera_vsq.vsq_logger.info('Universal: Motion Detected.')

                else:
                    motion_thresh_counter = 0
            else:
                m_time = time.monotonic()
                motion_detect_start_time = time.monotonic()
                bbox_lists, class_lists, scores = object_detector.inference(resized_frame)
                print("Inference time: ", time.monotonic() - m_time)

                if len(bbox_lists) > 0:
                    nms_list = nms(bbox_lists, 0.5)
                else:
                    nms_list = []

                if len(nms_list) == 0:
                    no_detection_output_counter += 1
                    if no_detection_output_counter >= NO_OBJECT_THRESH:
                        no_detection_output_counter = 0
                        motion_confirm = False
                        base_frame = resized_frame.copy()
                        camera_vsq.vsq_logger.info('Universal: Motion confirm False')

                elif len(nms_list) > 0:
                    imp_bbox_lists = []
                    for bboxes, score in zip(nms_list, scores):
                        person_counter += 1
                        bboxes[0] = int(bboxes[0])
                        bboxes[1] = int(bboxes[1])
                        bboxes[2] = int(bboxes[2])
                        bboxes[3] = int(bboxes[3])
                        cv2.rectangle(resized_frame, (bboxes[0], bboxes[3]-30), (bboxes[2], bboxes[3]), (100, 100, 0), -1)
                        cv2.putText(resized_frame, str(round(score, 3)), (bboxes[0] + 5, bboxes[3] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 100), 1)
                        cv2.rectangle(resized_frame, (bboxes[0], bboxes[1]), (bboxes[2], bboxes[3]), (250, 0, 0), 2)
                        #person_image = resized_frame[bboxes[1]: bboxes[3], bboxes[0]: bboxes[2]]
                        #score = round(score, 2)
                        # cv2.imwrite('images/Person_small_{}_{}.jpg'.format(person_counter, score), person_image)
                        #person_image_2 = big_frame[int(2.25*bboxes[1]): int(2.25*bboxes[3]), int(2.25*bboxes[0]): int(2.25*bboxes[2])]
                        #cv2.imwrite('images/Person_{}_{}.jpg'.format(person_counter, score), person_image_2)
                        imp_bbox_lists.append((bboxes[0], bboxes[1], bboxes[2], bboxes[3]))

                    if CAPTURE_PERSON and person_check:
                        person_check = False
                        DateTime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                        person_check_image = f'{DateTime}_Intrusion'
                        person_check_image_path = f'{person_check_directory}/{person_check_image}.jpg'
                        cv2.imwrite(person_check_image_path, big_frame)

                    centroid_check = False
                    for (i, (startX, startY, endX, endY)) in enumerate(imp_bbox_lists):
                        cX = int((startX + endX) / 2.0)
                        cY = int((startY + endY) / 2.0)
                        centroid = (cX, cY)
                        # text = "ID {} centroid {}".format(objectID, centroid)
                        cv2.circle(resized_frame, centroid, 3, (255, 0, 0), 1)     # printing centroid
                        #if endY < 180:
                        if int(endY - startY) > 150:
                            centroid_check = is_point_within_polygon(quadrilateral=Intrusion_entry_points, point=(int(endX), int(endY)))

                        if centroid_check and abs(send_api_alert_time_una - time.monotonic()) > Intrusion_entry_alert_interval:
                            send_api_alert_time_una = time.monotonic()
                            Intrusion_entry_count += 1
                            cv2.putText(resized_frame, "Intrusion Entry Alert", (28, 40),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                        (0, 0, 255), 2)
                            print("Intrusion Entry Alert Sent")
                            DateTime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                            Intrusion_entry_image_name = f'{DateTime}_Camera15_Intrusion-entry_{centroid_check}'
                            Intrusion_debug_image_name = f'{DateTime}_Intrusion_entry_debug'
                            Intrusion_entry_image_path = f'{alert_image_check}/{Intrusion_entry_image_name}.jpg'
                            Intrusion_debug_image_path = f'{debug_images_directory}/{Intrusion_debug_image_name}.jpg'
                            if IMAGE_WRITE:
                                cv2.imwrite(Intrusion_entry_image_path, big_frame)
                                cv2.imwrite(Intrusion_debug_image_path, resized_frame)
                            cv2.putText(resized_frame, "Image Saved", (35, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                        (0, 255, 0), 2)
                            camera_vsq.vsq_logger.info(f'Intrusion_entry')
                            alert = 'Intrusion Entry'
                            alertInfo = f'Intrusion_entry_{Intrusion_entry_count}'
                            objectCount = Intrusion_entry_count
                            # if SEND_ALERT:
                            #     send_mail(sender_email_id, sender_email_id_password, alertInfo,
                            #               Intrusion_entry_image_path, Intrusion_entry_image_name)
                            #     send_mail(Intrusion_entry_image_path)
                            #
                            #     camera_vsq.vsq_logger.info('Mail sent')

                '''
                objects, object_start_time = centroid_tracker.update(imp_bbox_lists)
        
                print(objects, object_start_time)
        
                for (objectID, centroid) in objects.items():
                    text = "ID {}".format(objectID)
                    obj_time = int(time.time()-object_start_time[objectID])
                    # cv2.rectangle(resized_frame, (centroid[0]-20, centroid[1]-30), (centroid[0]+60, centroid[1]+10), (100, 50, 100), -1)
                    # cv2.putText(resized_frame, text + ' T' + str(obj_time), (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                    # cv2.circle(resized_frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
                    bag_count = objectID
        
                cv2.rectangle(resized_frame, (0, 300-20), (320, 300+10), (100, 50, 100), -1)
                #cv2.putText(resized_frame, 'COUNT = '+str(bag_count), (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(resized_frame, 'COUNT = '+str(centroid_tracker.count), (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                
                for c in range(0, 3):
                    resized_frame[y1:y2, x1:x2, c] = (alpha_s * LOGO[:, :, c] + alpha_l * resized_frame[y1:y2, x1:x2, c])
                '''

            if VIDEO_WRITE:
                # write raw video frame to input stream of ffmpeg sub-process
                process.stdin.write(resized_frame.tobytes())
            if IMAGE_SHOW:
                cv2.namedWindow('Frame', cv2.WINDOW_KEEPRATIO)
                cv2.imshow("Frame", resized_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

if VIDEO_WRITE:
    process.stdin.close()
    process.wait()
    process.terminate()
