"""
Name:         main.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Entry point for the HandGesture application
"""

import cv2
import math
from utils.hand_detector import HandDetector
from utils.camera import VideoCamera

cap = VideoCamera()
handDetector = HandDetector(min_detection_confidence=0.7)

while True:
    status, frame = cap.read()
    handLandmarks = handDetector.findHandLandMarks(image=frame, draw=True)

    if(len(handLandmarks) != 0):
        x1, y1 = handLandmarks[4][1], handLandmarks[4][2]
        x2, y2 = handLandmarks[8][1], handLandmarks[8][2]
        length = math.hypot(x2-x1, y2-y1)
        print(length)

        cv2.circle(frame, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
        cv2.circle(frame, (x2, y2), 5, (255, 0, 255), cv2.FILLED)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

    cv2.imshow("Hand detector", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
