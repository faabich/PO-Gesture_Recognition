"""
Name:         camera.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Camera creation with opencv
"""

import cv2


class VideoCamera(object):
    def __init__(self, width=1600, height=900):
        # Video camera input
        self.cap = cv2.VideoCapture(0)
        self.width = width
        self.height = height

        # Width and height of window
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()