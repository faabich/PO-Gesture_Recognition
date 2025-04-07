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
import ctypes

class Gesture:
    def __init__(self):
        self.previous_time = 0
        self.clicking = False  # state of the clic to avoid clic repetitions

        # screen size parameters
        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN constant
        self.screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN constant

    def click_mouse(self, landmarks, frame):
        # Process each hand's landmarks
        for hand_idx, hand_landmarks in enumerate(landmarks):
            # Solution 1
            thumb_x, thumb_y = hand_landmarks[1][1], hand_landmarks[1][2]
            index_x, index_y = hand_landmarks[2][1], hand_landmarks[2][2]

            # Solution 2
            # wrist_x, wrist_y = hand_landmarks[0][1], hand_landmarks[0][2]
            # midfing_x, midfing_y = hand_landmarks[3][1], hand_landmarks[3][2]
            # pinky_x, pinky_y = hand_landmarks[4][1], hand_landmarks[4][2]

            # Calculatte length between index and thumb
            # Solution 1
            thumbindex_length = math.hypot(thumb_x - index_x, thumb_y - index_y)

            # Solution 2
            # wristindex_length = math.hypot(wrist_x - index_x, wrist_y - index_y)
            # wristmidfing_length = math.hypot(wrist_x - midfing_x, wrist_y - midfing_y)
            # wristpinky_length = math.hypot(wrist_x - pinky_x, wrist_y - pinky_y)

            # print(f"{wristpinky_length} | {wristindex_length} | {wristmidfing_length}")

            # Dots and lines on hands
            # Solution 1
            cv2.circle(frame, (index_x, index_y), 5, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (thumb_x, thumb_y), 5, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 255), 3)

            # Solution 2
            # cv2.circle(frame, (index_x, index_y), 5, (255, 0, 255), cv2.FILLED)
            # cv2.circle(frame, (midfing_x, midfing_y), 5, (255, 0, 255), cv2.FILLED)
            # cv2.circle(frame, (pinky_x, pinky_y), 5, (255, 0, 255), cv2.FILLED)
            # cv2.line(frame, (wrist_x, wrist_y), (index_x, index_y), (255, 0, 255), 3)
            # cv2.line(frame, (wrist_x, wrist_y), (midfing_x, midfing_y), (255, 0, 255), 3)
            # cv2.line(frame, (wrist_x, wrist_y), (pinky_x, pinky_y), (255, 0, 255), 3)

            # Index-thumb detection
            if thumbindex_length < 30 and not self.clicking:
                print("Clicked")
                ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # Left down
                self.clicking = True
            elif self.clicking:
                ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # Left up
                self.clicking = False

            # # Closed hand detection
            # if (wristindex_length < 150 and wristmidfing_length < 150 and wristpinky_length < 150) and not self.clicking:
            #     print("Clicked")
            #     ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # Left down
            #     self.clicking = True
            # else:
            #     ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # Left up
            #     self.clicking = False

    def move_mouse(self, landmarks, frame, camera_width, camera_height):
        current_time = time.time()
        for hand_idx, hand_landmarks in enumerate(landmarks):
            # get the wrist reference
            wrist_x, wrist_y = hand_landmarks[0][1] + 100, hand_landmarks[0][2] - 100   # + 100 and - 100 for centering position

            # # Claude IA movements smoothing
            # # Add a buffer zone (e.g., only use the middle 80% of the camera frame)
            # # This gives you more precision and avoids edge detection issues
            # buffer_x = camera_width * 0.2
            # buffer_y = camera_height * 0.2
            #
            # # Normalize coordinates to 0-1 range within the usable area
            # norm_x = max(0, min(1, (wrist_x - buffer_x) / (camera_width - 2 * buffer_x)))
            # norm_y = max(0, min(1, (wrist_y - buffer_y) / (camera_height - 2 * buffer_y)))
            #
            # # Map to screen coordinates
            # screen_x = int(norm_x * self.screen_width)
            # screen_y = int(norm_y * self.screen_height)
            #
            # # Add smoothing to prevent jitter (optional)
            # if not hasattr(self, 'last_x'):
            #     self.last_x, self.last_y = screen_x, screen_y
            #
            # # Apply some smoothing (e.g., 20% current position, 80% previous position)
            # smoothing = 0.8
            # smooth_x = int(smoothing * self.last_x + (1 - smoothing) * screen_x)
            # smooth_y = int(smoothing * self.last_y + (1 - smoothing) * screen_y)
            #
            # # Update last position
            # self.last_x, self.last_y = smooth_x, smooth_y

            # Movements without smoothing
            factor_x = self.screen_width / camera_width
            factor_y = self.screen_height / camera_height

            screen_x = wrist_x * factor_x
            screen_y = wrist_y * factor_y

            # move the mouse around
            if current_time - self.previous_time > 0.008:  # 8ms delay
                ctypes.windll.user32.SetCursorPos(int(screen_x), int(screen_y))
                self.previous_time = current_time

            # draw the circle
            cv2.circle(frame, (wrist_x - 100, wrist_y + 100), 5, (0, 255, 0), -1) # -1 parameter for a full dot