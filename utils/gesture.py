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
import tkinter as tk
import numpy as np
import utils.touch as touch


user32 = ctypes.windll.user32
keybd_event = ctypes.windll.user32.keybd_event


class Gesture:
    def __init__(self):
        # Configuration ctypes pour Windows
        self.user32 = ctypes.windll.user32
        self.SCREEN_WIDTH = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN constant
        self.SCREEN_HEIGHT = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN constant

        self.previous_time = 0
        self.clicking = False  # state of the clic to avoid clic repetitions

        # Initialize class
        self.root = tk.Tk()
        self.initialize_gesture()

        # Création du canvas pour dessiner
        self.canvas = tk.Canvas(
            self.root,
            width=self.SCREEN_WIDTH,
            height=self.SCREEN_HEIGHT,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack()

        # Enhanced hand tracking
        self.manager = touch.TouchManager(2)
        self.hand_info = {}
        self.hand_positions = {"Left": (0, 0), "Right": (0, 0)}


    def initialize_gesture(self):
        # Création de la fenêtre Tkinter transparente
        self.root.title("Hand Circles")
        self.root.attributes("-topmost", True)  # Toujours au premier plan
        self.root.attributes("-alpha", 1.0)  # Transparence globale (1.0 = opaque)
        self.root.attributes("-transparentcolor", "black")  # Couleur à rendre transparente
        self.root.geometry(f"{self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}+0+0")  # Plein écran
        self.root.overrideredirect(True)  # Pas de bordures de fenêtre
        # self.root.wm_attributes("-disabled", True)  # Désactiver les interactions avec la fenêtre
        self.root.config(bg="black")  # Fond noir (qui sera transparent)
        self.make_click_through()



    def make_click_through(self):
        """Make window click-through with enhanced error handling"""
        try:
            self.hwnd = ctypes.windll.user32.FindWindowW(None, "Hand Circles")
            self.style = ctypes.windll.user32.GetWindowLongW(self.hwnd, -20)  # GWL_EXSTYLE
            self.style |= 0x00000020 | 0x80000  # WS_EX_TRANSPARENT | WS_EX_LAYERED
            ctypes.windll.user32.SetWindowLongW(self.hwnd, -20, self.style)
            return True
        except Exception as e:
            print(f"Failed to make window click-through: {e}")
            return False


    @staticmethod
    def is_fingers_closed(landmarks):
        """
        Détecte si la position de la main correspond à un geste de clic
        (distance entre pouce et index faible)
        """
        threshold = 0.2

        wrist = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z])
        index_tip = np.array([landmarks[8].x, landmarks[8].y, landmarks[8].z])
        midfing_tip = np.array([landmarks[12].x, landmarks[12].y, landmarks[12].z])
        pinky_tip = np.array([landmarks[20].x, landmarks[20].y, landmarks[20].z])

        distance1 = np.linalg.norm(wrist - index_tip)
        distance2 = np.linalg.norm(wrist - midfing_tip)
        distance3 = np.linalg.norm(wrist - pinky_tip)

        return distance1 < threshold and distance2 < threshold and distance3 < threshold

    def update_circles(self, hand_positions):
        """Met à jour l'affichage des cercles avec gestion d'erreur"""
        try:
            # Effacer le canvas
            self.canvas.delete("all")

            # Dessiner les cercles
            for hand_id, (x, y) in hand_positions.items():
                radius = 30

                # Couleur selon la main
                color = "#00FF00" if hand_id == "Left" else "#FF0000"

                # Dessiner le cercle avec une transparence
                self.canvas.create_oval(
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                    fill=color,
                    stipple="gray50",  # Cela crée un effet de transparence
                    tags="circles"
                )

            # Mettre à jour l'interface
            self.root.update()
            self.make_click_through()
        except Exception as e:
            print(f"Error updating circles: {e}")


    def touchscreen_mode(self, landmarks, frame=None, camera_width=None, camera_height=None, enable_visuals=False):
        """Simplified logic for multi-touch using TouchManager.

        Backwards-compatible signature: older callers may pass extra args
        (frame, camera_width, camera_height, enable_visuals). These are
        optional and only used by modes that need visual output or coordinate
        scaling. When only `landmarks` is provided, the method behaves as
        before.
        """
        # --- Process hands and get positions ---
        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                hand_id = landmarks.multi_handedness[idx].classification[0].label
                is_closed = self.is_fingers_closed(hand_landmarks.landmark)

                # Use a key point (e.g., wrist/palm landmark 0) for position
                palm = hand_landmarks.landmark[0]
                x = int(palm.x * self.SCREEN_WIDTH)
                y = int(palm.y * self.SCREEN_HEIGHT)

                # Keep position inside screen bounds
                x = max(0, min(x, self.SCREEN_WIDTH - 1))
                y = max(0, min(y, self.SCREEN_HEIGHT - 1))

                self.hand_info[hand_id] = {"pos": (x, y), "closed": is_closed}
                self.hand_positions[hand_id] = (x, y)

                # Circles display
                # self.update_circles({h: info["pos"] for h, info in self.hand_info.items()})

        # --- Inject touches based on hand state ---
        # Track the fingers using a map
        finger_map = {"Left": 0, "Right": 1}

        # Iterate through all possible hands and update touches
        for hand_id, finger_id in finger_map.items():
            if hand_id in self.hand_info:
                pos = self.hand_info[hand_id]["pos"]
                is_closed = self.hand_info[hand_id]["closed"]

                if is_closed:
                    self.manager.press(id=finger_id, x=pos[0], y=pos[1])
                else:
                    self.manager.up(id=finger_id)
            else:
                self.manager.up(id=finger_id)

        # Apply all changes
        self.manager.apply_touches()

        time.sleep(0.01)

    def click_mouse(self, landmarks, frame):
        # Process each hand's landmarks
        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                # Solution 2
                wrist_x, wrist_y = hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y
                index_x, index_y = hand_landmarks.landmark[2].x, hand_landmarks.landmark[2].y
                midfing_x, midfing_y = hand_landmarks.landmark[3].x, hand_landmarks.landmark[3].y
                pinky_x, pinky_y = hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y

                # Calculatte length between index and thumb
                # Solution 2
                wristindex_length = math.hypot(wrist_x - index_x, wrist_y - index_y)
                wristmidfing_length = math.hypot(wrist_x - midfing_x, wrist_y - midfing_y)
                wristpinky_length = math.hypot(wrist_x - pinky_x, wrist_y - pinky_y)

                # print(f"{wristpinky_length} | {wristindex_length} | {wristmidfing_length}")

                # Dots and lines on hands
                # Solution 2
                cv2.circle(frame, (index_x, index_y), 5, (255, 0, 255), cv2.FILLED)
                cv2.circle(frame, (midfing_x, midfing_y), 5, (255, 0, 255), cv2.FILLED)
                cv2.circle(frame, (pinky_x, pinky_y), 5, (255, 0, 255), cv2.FILLED)
                cv2.line(frame, (wrist_x, wrist_y), (index_x, index_y), (255, 0, 255), 3)
                cv2.line(frame, (wrist_x, wrist_y), (midfing_x, midfing_y), (255, 0, 255), 3)
                cv2.line(frame, (wrist_x, wrist_y), (pinky_x, pinky_y), (255, 0, 255), 3)

                # Index-thumb detection
                # Solution 2
                if (wristindex_length < 150 and wristmidfing_length < 150 and wristpinky_length < 150) and not self.clicking:
                    print("Clicked")
                    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # Left down
                    self.clicking = True
                elif wristindex_length > 150 and wristmidfing_length > 150 and wristpinky_length > 150 and self.clicking:
                    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # Left up
                    print("Un-Clicked")
                    self.clicking = False

    def move_mouse(self, landmarks, frame, camera_width, camera_height):
        current_time = time.time()
        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                # get the wrist reference
                wrist = hand_landmarks.landmark[0]

                # Calculate coordinates for cv2.circle
                frame_height, frame_width, _ = frame.shape
                circle_center_x = int(wrist.x * frame_width)
                circle_center_y = int(wrist.y * frame_height)

                # Draw the circle for the current hand
                cv2.circle(frame, (circle_center_x, circle_center_y), 5, (0, 255, 0), -1)

                # Original mouse movement logic (remains unchanged for now)
                wrist_x_mouse, wrist_y_mouse = wrist.x + 100, wrist.y - 100  # Using different vars to avoid confusion
                factor_x = self.SCREEN_WIDTH / camera_width
                factor_y = self.SCREEN_HEIGHT / camera_height
                screen_x = wrist_x_mouse * factor_x
                screen_y = wrist_y_mouse * factor_y

                if current_time - self.previous_time > 0.008:  # 8ms delay
                    ctypes.windll.user32.SetCursorPos(int(screen_x), int(screen_y))
                    self.previous_time = current_time

    def driving_wheel(self, landmarks, original_image):
        imgH, imgW, imgC = original_image.shape
        mid_y_up = imgH // 2 + 50
        mid_y_down = imgH // 2 - 50

        if landmarks.multi_hand_landmarks:
            #continual forward input when a hand is detected
            keybd_event(0x57, 0, 0, 0)
            print("W")

            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                # get the index fingertip y position
                index_y_pos = hand_landmarks.landmark[8].y * imgH

                # if index fingertip is higher, unpress D and press A
                if index_y_pos < mid_y_down:
                    keybd_event(0x41, 0, 0, 0)
                    keybd_event(0x44, 0, 2, 0)
                    print("A")
                # if index fingertip is lower, unpress A and press D
                elif index_y_pos > mid_y_up:
                    keybd_event(0x44, 0, 0, 0)
                    keybd_event(0x41, 0, 2, 0)
                    print("D")
                else:
                    # if index fingertip is in the neutral area, unpress both A and D
                    keybd_event(0x41, 0, 2, 0)
                    keybd_event(0x44, 0, 2, 0)
                    print("Zone grise")
        else:
            # if no hand is detected, unpress every key
            keybd_event(0x57, 0, 2, 0)
            keybd_event(0x41, 0, 2, 0)
            keybd_event(0x44, 0, 2, 0)

    # function defining when a finger is folded via the y position of the tip and middle joint
    def finger_folded(self, landmarks, tip_id, mid_id):
        return landmarks[tip_id].y > landmarks[mid_id].y

    # function to detect if the other fingers are folded
    def is_index_only_extended(self, landmarks):
        other_folded = (
                self.finger_folded(landmarks, 12, 10) and
                self.finger_folded(landmarks, 16, 14) and
                self.finger_folded(landmarks, 20, 18)
        )
        return other_folded

    def index_up(self, landmarks):
        if landmarks[8].y < landmarks[6].y:
            return "up"

    # function to unpress the W, S UP and DOWN keys
    def unpress_keys(self):
        keybd_event(0x57, 0, 2, 0)
        keybd_event(0x53, 0, 2, 0)
        keybd_event(0x26, 0, 2, 0)
        keybd_event(0x28, 0, 2, 0)

    def pong(self, landmarks):
        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                if landmarks.multi_handedness:
                    hand_id = landmarks.multi_handedness[idx].classification[0].label
                else:
                    hand_id = "Left" if idx == 0 else "Right"
                if self.is_index_only_extended(hand_landmarks.landmark):
                    indexUp = self.index_up(hand_landmarks.landmark)
                    if hand_id == "Left":
                        if indexUp == "up":
                            keybd_event(0x57, 0, 0, 0)
                            keybd_event(0x53, 0, 2, 0)
                            print("Index up → W")
                        else:
                            keybd_event(0x53, 0, 0, 0)
                            keybd_event(0x57, 0, 2, 0)
                            print("Index down → S")
                    elif hand_id == "Right":
                        if indexUp == "up":
                            keybd_event(0x26, 0, 0, 0)
                            keybd_event(0x28, 0, 2, 0)
                            print("Index up → UP")
                        else:
                            keybd_event(0x28, 0, 0, 0)
                            keybd_event(0x26, 0, 2, 0)
                            print("Index down → DOWN")

                else:
                    self.unpress_keys()
                    print("unknown gesture → stop")
        else:
            self.unpress_keys()
            print("no hand detected → stop")