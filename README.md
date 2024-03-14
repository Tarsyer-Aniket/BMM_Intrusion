# BMM_top_Intrusion_entry

### RTSP LINK: 
```
rtsp://admin:industrail@10.0.59.15
```

### Intrusion ROI
```
Intrusion_entry_points = np.array([[80, 4], [53, 85], [106, 119], [173, 164], [251, 229], [298, 126], [267, 82], [203, 54], [137, 25], [80, 4] ], np.int32)
```

### Workflow of the pipeline
```
First it will be in Motion Detector, if motion detected for 
continuous 3 frames then will go into object detector
if no object detected for 3 continuous frames then back to motion 
detector

saved alert images are in "/tmp/BMM_ppe_detection" directory
for sending mail it will check if any new image there in directory
if found then will send the image as alert
```


