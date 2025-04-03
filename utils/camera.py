"""
Name:         camera.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Camera creation with opencv
"""

import mediapipe as mp
import cv2


class VideoCamera(object):
    def __init__(self, width=640, height=480):
        # Video camera input
        self.cap = cv2.VideoCapture(0)

        # Width and height of window
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # MediaPipe initialization
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hand = mp.solutions.hands
        self.hand = self.mp_hand.Hands()

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()