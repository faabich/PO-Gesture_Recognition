"""
Name:         main.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Entry point for the HandGesture application
"""

import mediapipe as mp
import cv2
import math
from utils.hand_detector import HandDetector
from utils.camera import VideoCamera

cap = VideoCamera()
handDetector = HandDetector(min_detection_confidence=0.7)

while True:
    status, image = cap.read()
    handLandmarks = handDetector.findHandLandMarks(image=image, draw=True)

    if(len(handLandmarks) != 0):
        x1, y1 = handLandmarks[4][1], handLandmarks[4][2]
        x2, y2 = handLandmarks[8][1], handLandmarks[8][2]
        length = math.hypot(x2-x1, y2-y1)
        print(length)

        cv2.circle(image, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(image, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(image, (x1, y1), (x2, y2), (255, 0, 255), 3)

    cv2.imshow("Volume", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
