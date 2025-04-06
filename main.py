"""
Name:         main.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Entry point for the HandGesture application
"""

from utils.hand_detector import HandDetector
from utils.camera import VideoCamera
from utils.gesture import Gesture
import cv2
import time


# Constants variables
CAMERA_WIDTH = 1600
CAMERA_HEIGHT = 900

# Camera initialisation
cap = VideoCamera(width=CAMERA_WIDTH, height=CAMERA_HEIGHT)

hand_detector = HandDetector()

gestures = Gesture()

while True:
    current_time = time.time()
    success, frame = cap.read()
    if success:
        # flip for mirror effect
        frame = cv2.flip(frame, 1)

        # Get landmarks
        landmarks = hand_detector.findHandsLandMarks(frame, draw=True)

        # Select gesture
        gestures.move_mouse(landmarks, frame, CAMERA_WIDTH, CAMERA_HEIGHT)

        # Show frame
        cv2.imshow("capture image", frame)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
