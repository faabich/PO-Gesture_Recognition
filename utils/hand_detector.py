"""
Name:         hand_detector.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Hand detector class using mediapipe
"""

import mediapipe as mp
import cv2


class HandDetector:
    def __init__(self, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(max_num_hands=max_num_hands, min_detection_confidence=min_detection_confidence,
                                   min_tracking_confidence=min_tracking_confidence)
        self.original_image = ""

    # Get hand landmarks from a frame
    def get_hand_landmarks(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # mediapipe needs RGB
        results = self.hands.process(frame)

        return results