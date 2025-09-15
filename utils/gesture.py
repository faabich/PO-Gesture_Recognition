"""
Name:         gesture.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.3 - Fixed Windows Touch Injection Error 87
Description:  Multiple gesture recognition with robust error handling
"""

import cv2
import math
import time
import ctypes
import numpy as np
import utils.touch as touch

user32 = ctypes.windll.user32
keybd_event = ctypes.windll.user32.keybd_event

class Gesture:
    def __init__(self, canvas=None):
        # Configuration for Windows API
        self.user32 = ctypes.windll.user32
        self.SCREEN_WIDTH = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        self.SCREEN_HEIGHT = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        self.MOUSEEVENTF_LEFTDOWN = 0x0002
        self.MOUSEEVENTF_LEFTUP = 0x0004
        self.previous_time = 0
        self.clicking = False
        self.hand_states = {"Left": False, "Right": False}
        self.last_click_time = {"Left": 0, "Right": 0}
        self.click_cooldown = 0.5  # Minimum time between clicks
        self.canvas = canvas  # Use provided canvas (from main Tkinter app)
        self.detected_hands = set()
        self.gesture_mode = 'none'  # 'none', 'grab', 'zoom'
        self.gesture_start_time = 0
        self.last_gesture_change = 0
        self.gesture_debounce = 0.1  # 100ms debounce
        self.hand_closed = {"Left": False, "Right": False}
        self.last_x = {"Left": None, "Right": None}
        self.last_y = {"Left": None, "Right": None}
        self.current_positions = {"Left": (0, 0), "Right": (0, 0)}
        self.last_gesture_change_time = {"Left": 0, "Right": 0}
        self.debounce_time = 0.2
        self.zoom_mode = False
        self.initial_distance = None
        self.zoom_threshold = 50
        self.zoom_center_x = None
        self.zoom_center_y = None
        self.last_zoom_distance = None
        self.zoom_sensitivity = 2.0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        self.last_error_time = 0
        self.error_recovery_delay = 1.0


    def update_circles(self, hand_positions, app):
        """Update hand position circles on the provided canvas in the main thread."""
        if not self.canvas or not app:
            return
        try:
            def update():
                self.canvas.delete("all")
                for hand_id, (x, y) in hand_positions.items():
                    radius = 30
                    color = "#00FF00" if hand_id == "Left" else "#FF0000"
                    self.canvas.create_oval(
                        x - radius, y - radius, x + radius, y + radius,
                        fill=color, stipple="gray50", tags="circles"
                    )
            app.after(0, update)  # Schedule update in main thread
        except Exception as e:
            print(f"Error updating circles: {e}")

    def safe_touch_operation(self, operation, *args, **kwargs):
        """Wrapper for touch operations with error recovery."""
        current_time = time.time()
        if (self.consecutive_errors >= self.max_consecutive_errors and
                current_time - self.last_error_time < self.error_recovery_delay):
            return False
        try:
            result = operation(*args, **kwargs)
            if result:
                self.consecutive_errors = 0
                return True
            else:
                self.consecutive_errors += 1
                self.last_error_time = current_time
                if operation == touch.touchUp:
                    print(f"TouchUp operation failed but continuing (non-critical)")
                    return True
                return False
        except Exception as e:
            print(f"Exception in touch operation: {e}")
            self.consecutive_errors += 1
            self.last_error_time = current_time
            return False

    def emergency_cleanup(self):
        """Emergency cleanup of touch contacts."""
        print("Performing emergency cleanup of touch contacts")
        try:
            for finger in [0, 1]:
                if touch.finger_in_contact[finger]:
                    print(f"Releasing stuck finger {finger}")
                    touch.touchUp(0, 0, finger=finger)
                else:
                    print(f"Finger {finger} not in contact, skipping")
                time.sleep(0.02)
            self.gesture_mode = 'none'
            self.consecutive_errors = 0
        except Exception as e:
            print(f"Error during emergency cleanup: {e}")
            touch.finger_in_contact[0] = False
            touch.finger_in_contact[1] = False
            self.gesture_mode = 'none'

    def touchscreen_mode(self, landmarks, frame, camera_width, camera_height, has_cursor):
        """Touchscreen mode with gesture state machine."""
        current_time = time.time()
        hand_info = {}
        if self.consecutive_errors >= self.max_consecutive_errors:
            if current_time - self.last_error_time > self.error_recovery_delay:
                self.emergency_cleanup()
            return

        # Process hands from MediaPipe
        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                hand_id = landmarks.multi_handedness[idx].classification[0].label
                is_closed = self.is_fingers_closed(hand_landmarks.landmark)
                palm = hand_landmarks.landmark[0]
                x = int(palm.x * self.SCREEN_WIDTH * 1.2 - 0.1 * self.SCREEN_WIDTH)
                y = int(palm.y * self.SCREEN_HEIGHT * 1.2 - 0.1 * self.SCREEN_HEIGHT)
                x = max(0, min(x, self.SCREEN_WIDTH - 1))
                y = max(0, min(y, self.SCREEN_HEIGHT - 1))
                hand_info[hand_id] = {"pos": (x, y), "closed": is_closed}
                cv2.putText(frame, f"{hand_id}: {'Closed' if is_closed else 'Open'}",
                           (10, 30 + idx * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Gesture State Machine
        num_closed = sum(1 for h in hand_info.values() if h["closed"])
        closed_hands = [h for h, info in hand_info.items() if info["closed"]]
        if current_time - self.last_gesture_change < self.gesture_debounce:
            self.update_circles({h: info["pos"] for h, info in hand_info.items()}, self.canvas.master)
            return

        # Zoom Mode
        if num_closed == 2:
            left_pos = hand_info["Left"]["pos"]
            right_pos = hand_info["Right"]["pos"]
            if self.gesture_mode != "zoom":
                if self.gesture_mode == "grab":
                    print("Upgrading Grab → Zoom")
                    grab_hand = closed_hands[0]
                    grab_finger = 0 if grab_hand == "Left" else 1
                    other_hand = "Right" if grab_hand == "Left" else "Left"
                    other_finger = 1 - grab_finger
                    other_pos = hand_info[other_hand]["pos"]
                    ok2 = False
                    for attempt in range(3):
                        ok2 = self.safe_touch_operation(
                            touch.touchDown, *other_pos, finger=other_finger, fingerRadius=5, holdEvents=True
                        )
                        if ok2:
                            break
                        time.sleep(0.02)  # Reduced sleep
                    if ok2:
                        self.gesture_mode = "zoom"
                        self.last_gesture_change = current_time
                        print("Zoom started correctly")
                    else:
                        print("Failed to add second finger for zoom")
                        self.gesture_mode = "grab"
                else:
                    print(">>> Entering Zoom Mode fresh")
                    self.safe_touch_operation(touch.touchUp, *left_pos, finger=0)
                    self.safe_touch_operation(touch.touchUp, *right_pos, finger=1)
                    time.sleep(0.02)
                    ok1 = self.safe_touch_operation(
                        touch.touchDown, *left_pos, finger=0, fingerRadius=5, holdEvents=True
                    )
                    time.sleep(0.02)
                    ok2 = self.safe_touch_operation(
                        touch.touchDown, *right_pos, finger=1, fingerRadius=5, holdEvents=True
                    )
                    if ok1 and ok2:
                        self.gesture_mode = "zoom"
                        self.last_gesture_change = current_time
                        print("Zoom started correctly")
                    else:
                        print("Zoom start failed")
                        self.gesture_mode = "none"
            else:
                if not self.safe_touch_operation(touch.touchMove, *left_pos, finger=0, fingerRadius=5):
                    print("Zoom update error (Left)")
                    self.emergency_cleanup()
                if not self.safe_touch_operation(touch.touchMove, *right_pos, finger=1, fingerRadius=5):
                    print("Zoom update error (Right)")
                    self.emergency_cleanup()
        # Grab Mode
        elif num_closed == 1:
            hand_id = closed_hands[0]
            pos = hand_info[hand_id]["pos"]
            finger = 0 if hand_id == "Left" else 1
            if self.gesture_mode != "grab":
                print(f">>> Entering Grab Mode ({hand_id})")
                self.safe_touch_operation(touch.touchUp, *pos, finger=1 - finger)
                if self.gesture_mode == "zoom":
                    self.safe_touch_operation(touch.touchUp, *pos, finger=0)
                    self.safe_touch_operation(touch.touchUp, *pos, finger=1)
                success = self.safe_touch_operation(touch.touchDown, *pos, fingerRadius=5, holdEvents=True, finger=finger)
                if success:
                    self.gesture_mode = "grab"
                    self.last_gesture_change = current_time
                else:
                    print("Grab start failed")
                    self.gesture_mode = "none"
            else:
                if not self.safe_touch_operation(touch.touchMove, *pos, fingerRadius=5, finger=finger):
                    print("Grab update error")
                    self.emergency_cleanup()
        # Idle Mode
        else:
            if self.gesture_mode != "none":
                print(f">>> Exiting {self.gesture_mode} Mode")
                self.safe_touch_operation(touch.touchUp, 0, 0, finger=0)
                self.safe_touch_operation(touch.touchUp, 0, 0, finger=1)
                self.gesture_mode = "none"
                self.last_gesture_change = current_time

        # Cursor Movement
        if has_cursor and "Right" in hand_info:
            if current_time - self.previous_time > 0.008:
                x, y = hand_info["Right"]["pos"]
                ctypes.windll.user32.SetCursorPos(x, y)
                self.previous_time = current_time

        # Update UI Overlay
        self.update_circles({h: info["pos"] for h, info in hand_info.items()}, self.canvas.master)
        return

    def is_fingers_closed(self, landmarks):
        """Detect if hand is closed for clicking."""
        threshold = 0.2
        wrist = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z])
        index_tip = np.array([landmarks[8].x, landmarks[8].y, landmarks[8].z])
        midfing_tip = np.array([landmarks[12].x, landmarks[12].y, landmarks[12].z])
        pinky_tip = np.array([landmarks[20].x, landmarks[20].y, landmarks[20].z])
        distance1 = np.linalg.norm(wrist - index_tip)
        distance2 = np.linalg.norm(wrist - midfing_tip)
        distance3 = np.linalg.norm(wrist - pinky_tip)
        return distance1 < threshold and distance2 < threshold and distance3 < threshold

    def click_mouse(self, landmarks, frame):
        """Simulate mouse clicks based on hand gestures."""
        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                wrist_x, wrist_y = hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y
                index_x, index_y = hand_landmarks.landmark[2].x, hand_landmarks.landmark[2].y
                midfing_x, midfing_y = hand_landmarks.landmark[3].x, hand_landmarks.landmark[3].y
                pinky_x, pinky_y = hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y
                wristindex_length = math.hypot(wrist_x - index_x, wrist_y - index_y)
                wristmidfing_length = math.hypot(wrist_x - midfing_x, wrist_y - midfing_y)
                wristpinky_length = math.hypot(wrist_x - pinky_x, wrist_y - pinky_y)
                cv2.circle(frame, (int(index_x * frame.shape[1]), int(index_y * frame.shape[0])), 5, (255, 0, 255), cv2.FILLED)
                cv2.circle(frame, (int(midfing_x * frame.shape[1]), int(midfing_y * frame.shape[0])), 5, (255, 0, 255), cv2.FILLED)
                cv2.circle(frame, (int(pinky_x * frame.shape[1]), int(pinky_y * frame.shape[0])), 5, (255, 0, 255), cv2.FILLED)
                cv2.line(frame, (int(wrist_x * frame.shape[1]), int(wrist_y * frame.shape[0])),
                        (int(index_x * frame.shape[1]), int(index_y * frame.shape[0])), (255, 0, 255), 3)
                cv2.line(frame, (int(wrist_x * frame.shape[1]), int(wrist_y * frame.shape[0])),
                        (int(midfing_x * frame.shape[1]), int(midfing_y * frame.shape[0])), (255, 0, 255), 3)
                cv2.line(frame, (int(wrist_x * frame.shape[1]), int(wrist_y * frame.shape[0])),
                        (int(pinky_x * frame.shape[1]), int(pinky_y * frame.shape[0])), (255, 0, 255), 3)
                if (wristindex_length < 0.05 and wristmidfing_length < 0.05 and wristpinky_length < 0.05) and not self.clicking:
                    print("Clicked")
                    ctypes.windll.user32.mouse_event(self.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    self.clicking = True
                elif wristindex_length > 0.05 and wristmidfing_length > 0.05 and wristpinky_length > 0.05 and self.clicking:
                    ctypes.windll.user32.mouse_event(self.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    print("Un-Clicked")
                    self.clicking = False

    def move_mouse(self, landmarks, frame, camera_width, camera_height):
        """Move mouse cursor based on hand position."""
        current_time = time.time()
        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                wrist = hand_landmarks.landmark[0]
                circle_center_x = int(wrist.x * frame.shape[1])
                circle_center_y = int(wrist.y * frame.shape[0])
                cv2.circle(frame, (circle_center_x, circle_center_y), 5, (0, 255, 0), -1)
                wrist_x_mouse, wrist_y_mouse = wrist.x, wrist.y
                factor_x = self.SCREEN_WIDTH / camera_width
                factor_y = self.SCREEN_HEIGHT / camera_height
                screen_x = wrist_x_mouse * factor_x * self.SCREEN_WIDTH
                screen_y = wrist_y_mouse * factor_y * self.SCREEN_HEIGHT
                if current_time - self.previous_time > 0.008:
                    ctypes.windll.user32.SetCursorPos(int(screen_x), int(screen_y))
                    self.previous_time = current_time

    def driving_wheel(self, landmarks, frame):
        """Simulate keyboard inputs for driving games."""
        imgH, imgW, _ = frame.shape
        mid_y_up = imgH // 2 + 50
        mid_y_down = imgH // 2 - 50
        if landmarks.multi_hand_landmarks:
            keybd_event(0x57, 0, 0, 0)  # Press W
            print("W")
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                index_y_pos = hand_landmarks.landmark[8].y * imgH
                if index_y_pos < mid_y_down:
                    keybd_event(0x41, 0, 0, 0)  # Press A
                    keybd_event(0x44, 0, 2, 0)  # Release D
                    print("A")
                elif index_y_pos > mid_y_up:
                    keybd_event(0x44, 0, 0, 0)  # Press D
                    keybd_event(0x41, 0, 2, 0)  # Release A
                    print("D")
                else:
                    keybd_event(0x41, 0, 2, 0)  # Release A
                    keybd_event(0x44, 0, 2, 0)  # Release D
                    print("Zone grise")
        else:
            keybd_event(0x57, 0, 2, 0)  # Release W
            keybd_event(0x41, 0, 2, 0)  # Release A
            keybd_event(0x44, 0, 2, 0)  # Release D

    def pong(self, landmarks):
        """Simulate keyboard inputs for pong game."""
        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                hand_id = landmarks.multi_handedness[idx].classification[0].label if landmarks.multi_handedness else ("Left" if idx == 0 else "Right")
                if self.is_index_only_extended(hand_landmarks.landmark):
                    indexUp = self.index_up(hand_landmarks.landmark)
                    if hand_id == "Left":
                        if indexUp == "up":
                            keybd_event(0x57, 0, 0, 0)  # Press W
                            keybd_event(0x53, 0, 2, 0)  # Release S
                            print("Index up → W")
                        else:
                            keybd_event(0x53, 0, 0, 0)  # Press S
                            keybd_event(0x57, 0, 2, 0)  # Release W
                            print("Index down → S")
                    elif hand_id == "Right":
                        if indexUp == "up":
                            keybd_event(0x26, 0, 0, 0)  # Press UP
                            keybd_event(0x28, 0, 2, 0)  # Release DOWN
                            print("Index up → UP")
                        else:
                            keybd_event(0x28, 0, 0, 0)  # Press DOWN
                            keybd_event(0x26, 0, 2, 0)  # Release UP
                            print("Index down → DOWN")
                else:
                    self.unpress_keys()
                    print("unknown gesture → stop")
        else:
            self.unpress_keys()
            print("no hand detected → stop")

    def finger_folded(self, landmarks, tip_id, mid_id):
        return landmarks[tip_id].y > landmarks[mid_id].y

    def is_index_only_extended(self, landmarks):
        return (self.finger_folded(landmarks, 12, 10) and
                self.finger_folded(landmarks, 16, 14) and
                self.finger_folded(landmarks, 20, 18))

    def index_up(self, landmarks):
        return "up" if landmarks[8].y < landmarks[6].y else "down"

    def unpress_keys(self):
        keybd_event(0x57, 0, 2, 0)  # Release W
        keybd_event(0x53, 0, 2, 0)  # Release S
        keybd_event(0x26, 0, 2, 0)  # Release UP
        keybd_event(0x28, 0, 2, 0)  # Release DOWN