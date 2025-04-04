"""
Name:         gesture.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Multiple gesture recognition
"""

import cv2
import math


class Gesture:
    def __init__(self):
        pass

    @staticmethod
    def click_gesture(handsLandmarks, frame):
        # Process each hand's landmarks
        for hand_idx, hand_landmarks in enumerate(handsLandmarks):
            x1, y1 = hand_landmarks[4][1], hand_landmarks[4][2]
            x2, y2 = hand_landmarks[8][1], hand_landmarks[8][2]

            # print(hand_landmarks)

            # Calculatte length between index and thumb
            length = math.hypot(x2 - x1, y2 - y1)

            print(length)

            # Dots and lines on hands
            cv2.circle(frame, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 5, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)