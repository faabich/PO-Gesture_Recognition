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

# Constants variables
CAMERA_WIDTH = 1600
CAMERA_HEIGHT = 900

# Camera initialisation
cap = VideoCamera(CAMERA_WIDTH, CAMERA_HEIGHT)

# Create hand detector object for landmarks
hand_detector = HandDetector()

# Create gesture object for further calls
gestures = Gesture()
if not gestures.make_click_through():
    print("Impossible de configurer le click-through, utilisation de méthode alternative.")
else:
    while True:
        success, frame = cap.read()
        if success:
            # flip for mirror effect
            frame = cv2.flip(frame, 1)

            # Get landmarks
            landmarks, mp_drawing, mp_hands = hand_detector.get_hand_landmarks(frame)

            # Select gestures
            # gestures.move_mouse(landmarks, frame, CAMERA_WIDTH, CAMERA_HEIGHT)
            # gestures.click_mouse(landmarks, frame)
            root = gestures.touchscreen_mode(landmarks, mp_drawing, mp_hands, frame, False)

            if cv2.waitKey(5) & 0xFF == ord('q'):
                root.destroy()
                break
# Nettoyage
cap.release()
cv2.destroyAllWindows()
