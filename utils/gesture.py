"""
Name:         gesture.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.3 - Fixed Windows Touch Injection Error 87
Description:  Multiple gesture recognition
"""

import time
import ctypes
import tkinter as tk
import numpy as np
import utils.touch as touch
from queue import Queue
from threading import Lock


user32 = ctypes.windll.user32
keybd_event = ctypes.windll.user32.keybd_event


class Gesture:
    def __init__(self, app, camera):
        # Configuration ctypes pour Windows
        self.user32 = ctypes.windll.user32
        self.SCREEN_WIDTH = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN constant
        self.SCREEN_HEIGHT = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN constant
        self.landmarks = None
        self.preset = None

        self.app = app
        self.camera = camera

        # Images
        self.images = {}
        self.previous_time = 0
        self.clicking = False  # state of the clic to avoid clic repetitions

        self.hand_data_queue = Queue(maxsize=2)  # Limite pour éviter l'accumulation
        self.lock = Lock()

        # Enhanced hand tracking
        self.manager = touch.TouchManager(2)
        self.hand_info = {}
        self.hand_positions = {"Left": (0, 0), "Right": (0, 0)}

        # Initialize class
        self.root = None
        self.canvas = None

        self.initialize_tkinter_window()

    def initialize_tkinter_window(self):
        """Initialise la fenêtre Tkinter"""
        if self.root is not None:
            return  # Déjà initialisé

        # Create tkinter window
        self.root = tk.Tk()
        self.root.title("Hand Circles")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 1.0)
        self.root.attributes("-transparentcolor", "black")
        self.root.geometry(f"{self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}+0+0")
        self.root.overrideredirect(True)
        self.root.config(bg="black")

        # Create canvas ffor circles
        self.canvas = tk.Canvas(
            self.root,
            width=self.SCREEN_WIDTH,
            height=self.SCREEN_HEIGHT,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack()

        # Make window click-through
        self.make_click_through()

    # Claude IA: how to make a tkinter window click-through in windows using ctypes
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


    # Check if fingers are closed from landmarks
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

    # Update circles display
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
        """Touchscreen mode using manager to inject touches based on hand gestures"""
        # --- Process hands and get positions ---
        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                hand_id = landmarks.multi_handedness[idx].classification[0].label
                is_closed = self.is_fingers_closed(hand_landmarks.landmark)

                # Use a key point (e.g., wrist/palm landmark 0) for position
                palm = hand_landmarks.landmark[0]
                x = int((1 - palm.x) * self.SCREEN_WIDTH)       # 1 - x pour inverser l'axe
                y = int(palm.y * self.SCREEN_HEIGHT)

                # Keep position inside screen bounds
                x = max(0, min(x, self.SCREEN_WIDTH - 1))
                y = max(0, min(y, self.SCREEN_HEIGHT - 1))

                self.hand_info[hand_id] = {"pos": (x, y), "closed": is_closed}
                self.hand_positions[hand_id] = (x, y)

                # Afficher les cercles
                self.update_circles({h: info["pos"] for h, info in self.hand_info.items()})

        # Tracker les mains en fonction de l'id
        hand_map = {"Left": 0, "Right": 1}

        # Loop dans les mains détectées
        for hand_id, touch_id in hand_map.items():
            if hand_id in self.hand_info:
                pos = self.hand_info[hand_id]["pos"]
                is_closed = self.hand_info[hand_id]["closed"]

                if is_closed:
                    self.manager.press(id=touch_id, x=pos[0], y=pos[1])
                else:
                    self.manager.up(id=touch_id)
            else:
                self.manager.up(id=touch_id)

        # Appliquer les changements
        self.manager.apply_touches()

        time.sleep(0.01)


    def mouse_mode(self, landmarks):
        current_time = time.time()
        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                hand_id = landmarks.multi_handedness[idx].classification[0].label
                is_closed = self.is_fingers_closed(hand_landmarks.landmark)
                # get the wrist reference
                wrist = hand_landmarks.landmark[0]

                x = int((1 - wrist.x) * self.SCREEN_WIDTH)      # 1 - x pour inverser l'axe
                y = int(wrist.y * self.SCREEN_HEIGHT)

                # Keep position inside screen bounds
                x = max(0, min(x, self.SCREEN_WIDTH - 1))
                y = max(0, min(y, self.SCREEN_HEIGHT - 1))

                if current_time - self.previous_time > 0.008:  # 8ms delay
                    ctypes.windll.user32.SetCursorPos(int(x), int(y))
                    self.previous_time = current_time

                self.hand_info[hand_id] = {"pos": (x, y), "closed": is_closed}
                self.hand_positions[hand_id] = (x, y)

                if is_closed:
                    print("Clicked")
                    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # Left down
                    self.clicking = True
                elif not is_closed:
                    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # Left up
                    print("Un-Clicked")
                    self.clicking = False

                # Circles display
                self.update_circles({h: info["pos"] for h, info in self.hand_info.items()})



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