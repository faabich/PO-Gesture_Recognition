"""
Name:         hand_detector.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Hand detector class
"""

import mediapipe as mp
import cv2


class HandDetector:
    def __init__(self, max_num_hands=4, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(max_num_hands=max_num_hands, min_detection_confidence=min_detection_confidence,
                                   min_tracking_confidence=min_tracking_confidence)


    def findHandsLandMarks(self, frame, maxHands=4, draw=False):
        originalImage = frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # mediapipe needs RGB
        results = self.hands.process(frame)
        allHandsLandmarks = []  # List to store landmarks of all hands

        if results.multi_hand_landmarks:
            # Get the number of hands detected (up to maxHands)
            numHands = min(len(results.multi_hand_landmarks), maxHands)

            # Process each hand
            for handIdx in range(numHands):
                hand = results.multi_hand_landmarks[handIdx]
                handLandmarks = []  # Store landmarks for this specific hand

                # Process landmarks for this hand
                for id, landMark in enumerate(hand.landmark):
                    imgH, imgW, imgC = originalImage.shape
                    xPos, yPos = int(landMark.x * imgW), int(landMark.y * imgH)
                    handLandmarks.append([id, xPos, yPos])

                # Add this hand's landmarks to our all hands list
                allHandsLandmarks.append(handLandmarks)

                # Draw landmarks if requested
                if draw:
                    self.mp_drawing.draw_landmarks(originalImage, hand, self.mp_hands.HAND_CONNECTIONS)

        return allHandsLandmarks