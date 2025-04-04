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
import mediapipe as mp
import cv2
import pyautogui
import time


# Constants variables
CAMERA_WIDTH = 1600
CAMERA_HEIGHT = 900

# Video camera input
cap = cv2.VideoCapture(0)
# Width and height of window
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

# screen size parameters
screen_width, screen_height = pyautogui.size()

previous_time = 0

# mediapipe drawing solution
mp_drawing = mp.solutions.drawing_utils
# mediapipe hand solution
mp_hand = mp.solutions.hands
hand = mp_hand.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1)

while True:
    current_time = time.time()
    success, frame = cap.read()
    if success:
        # flip for mirror effect
        frame = cv2.flip(frame, 1)

        RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hand.process(RGB_frame)

        # print(hand_landmarks)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hand.HAND_CONNECTIONS)

                # get the index finger reference
                index_finger = hand_landmarks.landmark[8]
                x, y = int(index_finger.x * CAMERA_WIDTH), int(index_finger.y * CAMERA_HEIGHT)

                # convert to screen x and y coordinates
                screen_x = int(index_finger.x * screen_width)
                screen_y = int(index_finger.y * screen_height)

                # move the mouse around
                if current_time - previous_time > 0.01:
                    pyautogui.moveTo(screen_x, screen_y)
                    prev_time = current_time

                # draw the circle
                cv2.circle(frame, (x, y), 10, (0, 255, 0), -1) # -1 parameter for a full dot

        cv2.imshow("capture image", frame)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
