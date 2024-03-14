#!/bin/bash

# $1 IP
# $2 Duration in mins
Date=$(date +'%d-%m-%Y')
Time=$(date +'%H-%M')

ffmpeg -rtsp_transport tcp -ss 00:00:03 -i "rtsp://admin:industrail@10.0.59.$1" -c:v copy -t 00:$2:00 raw_videos/${Date}_ip_$1_${Time}_$2_mins.mp4
