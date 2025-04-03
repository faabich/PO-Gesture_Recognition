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
handDetector = HandDetector(max_num_hands=4, min_detection_confidence=0.7)

while True:
    status, frame = cap.read()
    handsLandmarks = handDetector.findHandsLandMarks(frame=frame, draw=True)

    # Process each hand's landmarks
    for hand_idx, hand_landmarks in enumerate(handsLandmarks):
        # print(f"Hand #{hand_idx + 1} has {len(hand_landmarks)} landmarks:")
        x1, y1 = hand_landmarks[4][1], hand_landmarks[4][2]
        x2, y2 = hand_landmarks[8][1], hand_landmarks[8][2]

        # Calculatte length between index and thumb
        length = math.hypot(x2 - x1, y2 - y1)

        # Dots and lines on hands
        cv2.circle(frame, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
        cv2.circle(frame, (x2, y2), 5, (255, 0, 255), cv2.FILLED)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

    cv2.imshow("Hand detector", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
