"""
Name:         main.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Entry point for the HandGesture application
"""

import cv2
from utils.hand_detector import HandDetector
from utils.camera import VideoCamera
from utils.gesture import Gesture


cap = VideoCamera()
handDetector = HandDetector(max_num_hands=4, min_detection_confidence=0.7)
gesture = Gesture()

while True:
    status, frame = cap.read()
    handsLandmarks = handDetector.findHandsLandMarks(frame=frame, draw=True)

    gesture.click_gesture(handsLandmarks, frame)

    cv2.imshow("Hand detector", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
