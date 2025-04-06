"""
Name:         gesture.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Multiple gesture recognition
"""

import cv2
import math
import time
import pyautogui


class Gesture:
    def __init__(self):
        self.previous_time = 0
        self.clicking = False  # state of the clic to avoid clic repetitions

        # screen size parameters
        self.screen_width, self.screen_height = pyautogui.size()

    def click_mouse(self, landmarks, frame):
        # Process each hand's landmarks
        for hand_idx, hand_landmarks in enumerate(landmarks):
            x1, y1 = hand_landmarks[1][1], hand_landmarks[1][2]
            x2, y2 = hand_landmarks[2][1], hand_landmarks[2][2]

            # Calculatte length between index and thumb
            length = math.hypot(x2 - x1, y2 - y1)

            # print(length)

            # Dots and lines on hands
            cv2.circle(frame, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 5, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # click detection
            if length < 30 and not self.clicking:
                print("Clicked")
                pyautogui.mouseDown()
                self.clicking = True
            elif self.clicking:
                pyautogui.mouseUp()
                self.clicking = False

    def move_mouse(self, landmarks, frame, camera_width, camera_height):
        current_time = time.time()
        for hand_idx, hand_landmarks in enumerate(landmarks):
            # get the index finger reference
            index_finger_x, index_finger_y = hand_landmarks[0][1], hand_landmarks[0][2]

            # Normalize coordinates (0-1)
            norm_x = index_finger_x / camera_width
            norm_y = index_finger_y / camera_height

            # convert to screen x and y coordinates
            screen_x = int(norm_x * self.screen_width)
            screen_y = int(norm_y * self.screen_height)

            # move the mouse around
            if current_time - self.previous_time > 0.001:  # 1ms delay
                pyautogui.moveTo(screen_x, screen_y)
                self.previous_time = current_time

            # draw the circle
            cv2.circle(frame, (index_finger_x, index_finger_y), 5, (0, 255, 0), -1) # -1 parameter for a full dot