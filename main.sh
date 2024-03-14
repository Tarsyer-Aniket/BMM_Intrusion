#!/bin/bash

# Get the current hour using the date command
#HOUR=$(date +%H)

# Check if the current hour is between 7 AM and 7 PM
#if [ $HOUR -ge 7 ] && [ $HOUR -lt 19 ]
#then
    # Run the main.py file
python3 main.py
#else
    # It's not daytime, so sleep for 10 minutes
#    echo "It's nighttime, sleeping for 10 minutes"
#    sleep 10m
#fi

