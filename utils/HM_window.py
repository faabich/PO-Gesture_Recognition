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

class HM_window:

    # Constants variables
    CAMERA_WIDTH = 1600
    CAMERA_HEIGHT = 900

    # Camera initialisation
    cap = VideoCamera(CAMERA_WIDTH, CAMERA_HEIGHT)

    # Create hand detector object for landmarks
    hand_detector = HandDetector()

    # Create gesture object for further calls
    gestures = Gesture()

    while True:
        success, frame = cap.read()
        if success:
            # flip for mirror effect
            frame = cv2.flip(frame, 1)

            # Get landmarks
            landmarks = hand_detector.findHandsLandMarks(frame, draw=False)

            # Select gestures
            gestures.move_mouse(landmarks, frame, CAMERA_WIDTH, CAMERA_HEIGHT)
            gestures.click_mouse(landmarks, frame)

            # Show frame
            cv2.imshow("capture image", frame)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
