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
            # hand_landmarks: [[[0, x, y], [0, x, y], [12, x, y], [20, x, y]]]
            wrist_x, wrist_y = hand_landmarks[0][1], hand_landmarks[0][2]
            index_x, index_y = hand_landmarks[1][1], hand_landmarks[1][2]
            midfing_x, midfing_y = hand_landmarks[2][1], hand_landmarks[2][2]
            pinky_x, pinky_y = hand_landmarks[3][1], hand_landmarks[3][2]

            # Calculatte length between index and thumb
            wristindex_length = math.hypot(wrist_x - index_x, wrist_y - index_y)
            wristmidfing_length = math.hypot(wrist_x - midfing_x, wrist_y - midfing_y)
            wristpinky_length = math.hypot(wrist_x - pinky_x, wrist_y - pinky_y)

            # print(f"{wristpinky_length} | {wristindex_length} | {wristmidfing_length}")

            # Dots and lines on hands
            cv2.circle(frame, (index_x, index_y), 5, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (midfing_x, midfing_y), 5, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (pinky_x, pinky_y), 5, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (wrist_x, wrist_y), (index_x, index_y), (255, 0, 255), 3)
            cv2.line(frame, (wrist_x, wrist_y), (midfing_x, midfing_y), (255, 0, 255), 3)
            cv2.line(frame, (wrist_x, wrist_y), (pinky_x, pinky_y), (255, 0, 255), 3)

            # Index-thumb detection
            # if thumbindex_length < 30 and not self.clicking:
            #     print("Clicked")
            #     pyautogui.mouseDown()
            #     self.clicking = True
            # elif self.clicking:
            #     pyautogui.mouseUp()
            #     self.clicking = False

            # Closed hand detection
            if (wristindex_length < 150 and wristmidfing_length < 150 and wristpinky_length < 150) and not self.clicking:
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
            wrist_x, wrist_y = hand_landmarks[0][1], hand_landmarks[0][2]

            # Get scaling factor
            factor_x = self.screen_width / camera_width
            factor_y = self.screen_height / camera_height

            # convert to screen x and y coordinates
            screen_x = int(wrist_x * factor_x)
            screen_y = int(wrist_y * factor_y)

            # move the mouse around
            if current_time - self.previous_time > 0.008:  # 1ms delay
                pyautogui.moveTo(screen_x, screen_y)
                self.previous_time = current_time

            # draw the circle
            cv2.circle(frame, (wrist_x, wrist_y), 5, (0, 255, 0), -1) # -1 parameter for a full dot