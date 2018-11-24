#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Capture continuous video stream with picamera and display it on a screen.

Requires picamera to be installed.
"""

import io
import sys
import os
import time
import threading
from picamera import PiCamera
import RPi.GPIO as GPIO

from PIL import Image

from demo_opts import get_device

try:
    import picamera
except ImportError:
    print("The picamera library is not installed. Install it using 'sudo -H pip install picamera'.")
    sys.exit()


# create a pool of image processors
done = False
lock = threading.Lock()
pool = []

freeze = False
Button = 15

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Button, GPIO.IN, GPIO.PUD_UP)

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()

    def run(self):
        # this method runs in a separate thread
        global done
        global freeze
        while not self.terminated:
            # wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)

                    # read the image and display it on screen
                    photo = Image.open(self.stream)

                    if freeze:
                        pass
                    else:
                        device.display(photo.convert(device.mode))
                        # if button pressed
                        if GPIO.input(Button) == 0:
                            print("Button pressed!")
                            freeze = True
                            os.system(' sudo aplay /home/pi/picamera/remote/assets/camera-shutter-click-03.wav')
                            #The following 2 lines below allow you to save the thumbnail on the OLED screen
                            #oled_thumbnail_location='/home/pi/Desktop/photobooth/bett-img-' + time.strftime("%Y%m%d-%H%M%S") + '_thumbnail.jpg'
                            #photo.save(oled_thumbnail_location)
                            time.sleep(0.5)
                            picture_location='/home/pi/Desktop/photobooth/' + time.strftime("%Y%m%d-%H%M%S") + 'bett_img.jpg'
                            #This will allow you to see the camera feed on a monitor (connected through HDMI
                            #camera.start_preview(fullscreen=False, window = (600, 10, 640, 480))
                            camera.capture(picture_location)
                            time.sleep(0.4)
                            freeze = False

                    # set done to True if you want the script to terminate
                    # at some point
                    # done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()

                    # return ourselves to the pool
                    with lock:
                        pool.append(self)


def streams():
    while not done:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            # when the pool is starved, wait a while for it to refill
            time.sleep(0.1)


cameraResolution = (1800, 900)
cameraFrameRate = 12
device = get_device()

time.sleep(0)

with picamera.PiCamera() as camera:
    pool = [ImageProcessor() for i in range(4)]

    # set camera resolution
    camera.resolution = cameraResolution
    camera.framerate = cameraFrameRate

    print("Starting camera preview...")
    #camera.start_preview()
    time.sleep(2)

    print("Capturing video...")
    try:
        camera.stop_preview()
        camera.capture_sequence(streams(), use_video_port=True, resize=device.size)

        # shut down the processors in an orderly fashion
        while pool:
            with lock:
                processor = pool.pop()
            processor.terminated = True
            processor.join()
    except KeyboardInterrupt:
        pass


 
