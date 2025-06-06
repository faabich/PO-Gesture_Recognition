"""
Name:         gesture.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.2 - Refactored Zoom Implementation
Description:  Multiple gesture recognition
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
        # --- (Your existing __init__ code remains unchanged) ---
        # Configuration ctypes pour Windows
        self.user32 = ctypes.windll.user32
        self.SCREEN_WIDTH = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN constant
        self.SCREEN_HEIGHT = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN constant
        self.MOUSEEVENTF_LEFTDOWN = 0x0002
        self.MOUSEEVENTF_LEFTUP = 0x0004

        self.previous_time = 0
        self.clicking = False  # state of the clic to avoid clic repetitions

        # Clicking states
        self.hand_states = {"Left": False, "Right": False}
        self.last_click_time = {"Left": 0, "Right": 0}

        # Initialize class
        self.root = tk.Tk()
        self.initialize_gesture()

        # Variables clicks
        self.click_cooldown = 0.5  # Temps minimum entre les clics en secondes

        # Création du canvas pour dessiner
        self.canvas = tk.Canvas(
            self.root,
            width=self.SCREEN_WIDTH,
            height=self.SCREEN_HEIGHT,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack()

        self.detected_hands = set()

        # NEW: State variable to track the current gesture mode
        # Can be 'none', 'grab', or 'zoom'
        self.gesture_mode = 'none'

        # --- (The rest of your __init__ is unchanged) ---
        self.hand_closed = {"Left": False, "Right": False}
        self.last_x = {"Left": None, "Right": None}
        self.last_y = {"Left": None, "Right": None}
        self.current_positions = {"Left": (0, 0), "Right": (0, 0)}
        self.last_gesture_change_time = {"Left": 0, "Right": 0}
        self.debounce_time = 0.2  # seconds

        self.zoom_mode = False
        self.initial_distance = None
        self.zoom_threshold = 50  # Minimum distance change to trigger zoom
        self.zoom_center_x = None
        self.zoom_center_y = None
        self.last_zoom_distance = None
        self.zoom_sensitivity = 2.0  # Adjust this to make zoom more/less sensitive


    # --- (All your other methods like initialize_gesture, make_click_through, etc., remain here unchanged) ---
    def initialize_gesture(self):
        # Création de la fenêtre Tkinter transparente
        self.root.title("Hand Circles")
        self.root.attributes("-topmost", True)  # Toujours au premier plan
        self.root.attributes("-alpha", 1.0)  # Transparence globale (1.0 = opaque)
        self.root.attributes("-transparentcolor", "black")  # Couleur à rendre transparente
        self.root.geometry(f"{self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}+0+0")  # Plein écran
        self.root.overrideredirect(True)  # Pas de bordures de fenêtre
        self.root.wm_attributes("-disabled", True)  # Désactiver les interactions avec la fenêtre
        self.root.config(bg="black")  # Fond noir (qui sera transparent)
        self.make_click_through()


    # Une fonction spéciale pour rendre la fenêtre "click-through"
    def make_click_through(self):
        try:
            self.hwnd = ctypes.windll.user32.FindWindowW(None, "Hand Circles")
            self.style = ctypes.windll.user32.GetWindowLongW(self.hwnd, -20)  # GWL_EXSTYLE
            self.style |= 0x00000020 | 0x80000  # WS_EX_TRANSPARENT | WS_EX_LAYERED
            ctypes.windll.user32.SetWindowLongW(self.hwnd, -20, self.style)
            return True
        except:
            return False


    def perform_click(self, x, y, hand_id):
        """Effectue un clic à la position spécifiée"""
        current_time = time.time()

        # Vérifier si suffisamment de temps s'est écoulé depuis le dernier clic
        if current_time - self.last_click_time[hand_id] < self.click_cooldown:
            return

        # Convertir les coordonnées (0-1) en coordonnées d'écran
        screen_x = int(x * self.SCREEN_WIDTH)
        screen_y = int(y * self.SCREEN_HEIGHT)
        touch.touchDown(x, y, holdEvents=True)

        # Mettre à jour le temps du dernier clic
        self.last_click_time[hand_id] = current_time
        print(f"Clic effectué par la main {hand_id} à ({screen_x}, {screen_y})")


    def perform_unclick(self, x, y, hand_id):
        # # Convertir les coordonnées (0-1) en coordonnées d'écran
        screen_x = int(x * self.SCREEN_WIDTH)
        screen_y = int(y * self.SCREEN_HEIGHT)
        # sendTouchUp(screen_x, screen_y)
        print(f"Unclic effectué par la main")


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

        # print(f"distance1: {distance1}, distance2: {distance2}, distance3: {distance3}")

        return distance1 < threshold and distance2 < threshold and distance3 < threshold   # Seuil de détection


    def update_circles(self, hand_positions):
        """Met à jour l'affichage des cercles"""
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
                tags = "circles"
            )

        # Mettre à jour l'interface
        self.root.update()

        self.make_click_through()

    # This function can now be removed, as its logic is integrated into the new touchscreen_mode
    # def handle_touch_for_hand(self, hand_id, x, y, is_closed):

    # These functions are no longer needed as we are not using the flawed touchPinch approach
    # def handle_zoom_gesture(self, left_pos, right_pos):
    # def simulate_zoom_in(self, center_x, center_y, zoom_amount):
    # def simulate_zoom_out(self, center_x, center_y, zoom_amount):

    def touchscreen_mode(self, landmarks, mp_drawing, mp_hands, frame, has_cursor):
        hand_info = {} # Store position and closed state for each hand

        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                # Determine hand ID ("Left" or "Right")
                hand_id = landmarks.multi_handedness[idx].classification[0].label

                # Check if hand is closed
                is_closed = self.is_fingers_closed(hand_landmarks.landmark)

                # Get hand position (wrist) and scale to screen
                palm_hand = hand_landmarks.landmark[0]
                screen_x = int(palm_hand.x * self.SCREEN_WIDTH * 1.2 - 0.1 * self.SCREEN_WIDTH)
                screen_y = int(palm_hand.y * self.SCREEN_HEIGHT * 1.2 - 0.1 * self.SCREEN_HEIGHT)

                # Store all info for this frame
                hand_info[hand_id] = {'pos': (screen_x, screen_y), 'closed': is_closed}

                # Display hand state on the CV2 frame
                cv2.putText(frame, f"Main {hand_id}: {'Closed' if is_closed else 'Open'}",
                            (10, 30 + idx * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # --- GESTURE LOGIC ---

        num_hands = len(hand_info)
        closed_hands = [hand for hand, info in hand_info.items() if info['closed']]
        num_closed_hands = len(closed_hands)

        # State: Zooming (two hands are closed)
        if num_closed_hands == 2:
            if self.gesture_mode != 'zoom':
                # --- Start of Zoom ---
                print("Starting Zoom Mode")
                self.gesture_mode = 'zoom'
                left_pos = hand_info['Left']['pos']
                right_pos = hand_info['Right']['pos']
                # finger 0 for Left, finger 1 for Right
                touch.touchDown(left_pos[0], left_pos[1], finger=0)
                touch.touchDown(right_pos[0], right_pos[1], finger=1)
            else:
                # --- Continue Zoom ---
                left_pos = hand_info['Left']['pos']
                right_pos = hand_info['Right']['pos']
                print(f"Updating Zoom Left: {left_pos[0]}, {left_pos[1]} | Right: {right_pos[0]}, {right_pos[1]}")
                touch.touchMove(left_pos[0], left_pos[1], finger=0)
                touch.touchMove(right_pos[0], right_pos[1], finger=1)

        # State: Grabbing (exactly one hand is closed)
        elif num_closed_hands == 1:
            hand_id = closed_hands[0]
            pos = hand_info[hand_id]['pos']

            # Use finger 0 for left hand grab, finger 1 for right hand grab
            finger_index = 0 if hand_id == "Left" else 1

            if self.gesture_mode != 'grab':
                # --- Start of Grab ---
                print(f"Starting Grab with {hand_id} hand")
                self.gesture_mode = 'grab'
                # If we were just zooming, make sure the other finger is lifted
                touch.touchUp(0, 0, finger=1 - finger_index) # Send a 'safe' touchUp
                touch.touchDown(pos[0], pos[1], finger=finger_index)
            else:
                # --- Continue Grab ---
                print(f"Moving with {hand_id} hand")
                touch.touchMove(pos[0], pos[1], finger=finger_index)

        # State: Idle (no hands are closed)
        else:
            if self.gesture_mode != 'none':
                # --- End of Gesture ---
                print(f"Ending gesture: {self.gesture_mode}")
                # Release all touch points to be safe
                touch.touchUp(0, 0, finger=0)
                touch.touchUp(0, 0, finger=1)
                self.gesture_mode = 'none'

        # Update the visual circles on the transparent window
        self.update_circles({hand: info['pos'] for hand, info in hand_info.items()})

        return self.root

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