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
import tkinter as tk
import numpy as np
import utils.touch as touch


user32 = ctypes.windll.user32
keybd_event = ctypes.windll.user32.keybd_event


def driving_wheel_unpress_keys(key_code):
    keybd_event(key_code, 0, 2, 0)

class Gesture:
    def __init__(self):
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

        # Initialize variables to track finger state
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

    def handle_touch_for_hand(self, hand_id, x, y, is_closed):
        """
        Handle touch events for a specific hand with improved touch handling
        """
        current_time = time.time()
        # Use finger 0 for Left hand, finger 1 for Right hand
        finger_index = 0 if hand_id == "Left" else 1

        # Check if gesture has changed with debouncing
        if is_closed != self.hand_closed[hand_id] and (
                current_time - self.last_gesture_change_time[hand_id]) > self.debounce_time:
            self.last_gesture_change_time[hand_id] = current_time

            # Update hand state
            self.hand_closed[hand_id] = is_closed

            if is_closed:
                print(f"{hand_id} hand: Touch down at {x}, {y}")
                # With the new library, just specify which finger index to use
                touch.touchDown(x, y, fingerRadius=5, holdEvents=True, finger=finger_index)
            else:
                print(f"{hand_id} hand: Touch up at {x}, {y}")
                # Just specify which finger index to release
                touch.touchUp(x, y, fingerRadius=5, finger=finger_index)

        # If hand is closed and position has changed, simulate move
        elif is_closed and (self.last_x[hand_id] is None or self.last_y[hand_id] is None or
                            abs(x - self.last_x[hand_id]) > 5 or abs(y - self.last_y[hand_id]) > 5):
            print(f"{hand_id} hand: Touch move to {x}, {y}")
            # Each hand moves its own touch point
            touch.touchMove(x, y, fingerRadius=5, finger=finger_index)

        # Update last known position
        self.last_x[hand_id] = x
        self.last_y[hand_id] = y

    def touchscreen_mode(self, landmarks, mp_drawing, mp_hands, frame, has_cursor):
        # Your existing code...
        hand_positions = {}
        both_hands_closed = True
        detected_hands_this_frame = set()

        if landmarks.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                # Determine hand ID
                if landmarks.multi_handedness:
                    hand_id = landmarks.multi_handedness[idx].classification[0].label
                else:
                    hand_id = "Left" if idx == 0 else "Right"

                detected_hands_this_frame.add(hand_id)

                # Check if hand is closed
                is_clicking = self.is_fingers_closed(hand_landmarks.landmark)

                # Get hand position
                palm_hand = hand_landmarks.landmark[0]
                screen_x = int(palm_hand.x * self.SCREEN_WIDTH * 1.2 - 0.1 * self.SCREEN_WIDTH)
                screen_y = int(palm_hand.y * self.SCREEN_HEIGHT * 1.2 - 0.1 * self.SCREEN_HEIGHT)

                # Store hand position and state
                hand_positions[hand_id] = (screen_x, screen_y)

                # Check if this hand is NOT closed
                if not is_clicking:
                    both_hands_closed = False

                # Display hand state
                cv2.putText(frame, f"Main {hand_id}: {'Clic' if is_clicking else 'Repos'}",
                            (10, 30 + idx * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Check for zoom gesture (both hands detected and both closed)
            if len(detected_hands_this_frame) == 2 and both_hands_closed:
                if "Left" in hand_positions and "Right" in hand_positions:
                    self.handle_zoom_gesture(hand_positions["Left"], hand_positions["Right"])
            else:
                # Reset zoom mode if conditions not met
                if self.zoom_mode:
                    self.zoom_mode = False
                    print("Zoom mode ended")

            # Handle individual hand touch events (only if not in zoom mode)
            if not self.zoom_mode:
                for idx, hand_landmarks in enumerate(landmarks.multi_hand_landmarks):
                    if landmarks.multi_handedness:
                        hand_id = landmarks.multi_handedness[idx].classification[0].label
                    else:
                        hand_id = "Left" if idx == 0 else "Right"

                    is_clicking = self.is_fingers_closed(hand_landmarks.landmark)
                    palm_hand = hand_landmarks.landmark[0]
                    screen_x = int(palm_hand.x * self.SCREEN_WIDTH * 1.2 - 0.1 * self.SCREEN_WIDTH)
                    screen_y = int(palm_hand.y * self.SCREEN_HEIGHT * 1.2 - 0.1 * self.SCREEN_HEIGHT)

                    self.handle_touch_for_hand(hand_id, screen_x, screen_y, is_clicking)

            # Update circles display
            self.update_circles(hand_positions)

        return self.root

    def calculate_hand_distance(self, pos1, pos2):
        """Calculate distance between two hand positions"""
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def get_zoom_center(self, pos1, pos2):
        """Get the center point between two hands for zoom focus"""
        center_x = (pos1[0] + pos2[0]) // 2
        center_y = (pos1[1] + pos2[1]) // 2
        return center_x, center_y

    def handle_zoom_gesture(self, left_pos, right_pos):
        """Handle zoom in/out based on hand distance"""
        current_distance = self.calculate_hand_distance(left_pos, right_pos)
        center_x, center_y = self.get_zoom_center(left_pos, right_pos)

        if not self.zoom_mode:
            # Start zoom mode
            self.zoom_mode = True
            self.initial_distance = current_distance
            self.last_zoom_distance = current_distance
            self.zoom_center_x = center_x
            self.zoom_center_y = center_y
            print(f"Zoom mode started at distance: {current_distance}")
            return

        # Calculate distance change
        distance_change = current_distance - self.last_zoom_distance

        # Only process if change is significant enough
        if abs(distance_change) > self.zoom_threshold:
            # Calculate zoom factor based on distance change
            zoom_factor = distance_change * self.zoom_sensitivity

            # Determine zoom direction and simulate pinch gesture
            if distance_change > 0:
                # Hands moving apart - zoom in
                self.simulate_zoom_in(center_x, center_y, abs(zoom_factor))
                print(f"Zoom IN - Distance: {current_distance}, Change: {distance_change}")
            else:
                # Hands moving closer - zoom out
                self.simulate_zoom_out(center_x, center_y, abs(zoom_factor))
                print(f"Zoom OUT - Distance: {current_distance}, Change: {distance_change}")

            self.last_zoom_distance = current_distance

    def simulate_zoom_in(self, center_x, center_y, zoom_amount):
        """Simulate zoom in by moving touch points apart from center"""
        # Calculate offset based on zoom amount
        offset = int(zoom_amount)

        # Start positions (close together at center)
        start_left = (center_x - 20, center_y)
        start_right = (center_x + 20, center_y)

        # End positions (further apart)
        end_left = (center_x - 20 - offset, center_y)
        end_right = (center_x + 20 + offset, center_y)

        # Use the touchPinch function from touch.py
        touch.touchPinch(start_left, end_left, start_right, end_right, count=5, duration=0.3)

    def simulate_zoom_out(self, center_x, center_y, zoom_amount):
        """Simulate zoom out by moving touch points toward center"""
        # Calculate offset based on zoom amount
        offset = int(zoom_amount)

        # Start positions (far apart)
        start_left = (center_x - 20 - offset, center_y)
        start_right = (center_x + 20 + offset, center_y)

        # End positions (closer together at center)
        end_left = (center_x - 20, center_y)
        end_right = (center_x + 20, center_y)

        # Use the touchPinch function from touch.py
        touch.touchPinch(start_left, end_left, start_right, end_right, count=5, duration=0.3)

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
        # Logic to simulate the keypress based on the Y position of the hand
        # if len(landmarks) > 0:
        for hand_idx, hand_landmarks in enumerate(landmarks):
            # We use the y position of the landmark 8 (index finger tip)
            index_y_pos = hand_landmarks[2][2]  # id=8 is the index finger tip
            imgH, imgW, imgC = original_image.shape
            mid_y_up = imgH // 2 + 50
            mid_y_down = imgH // 2 - 50

            # Determine if the Y position is above or below the middle and simulate keypress
            # if index_y_pos < mid_y:
            #     driving_wheel_press_keys(KEY_A)
            #     print("A")
            #     if index_y_pos == mid_y:
            if index_y_pos < mid_y_down:
                keybd_event(0x1E, 0, 0, 0)
                print("A")
            elif index_y_pos > mid_y_up:
                keybd_event(0x20, 0, 0, 0)
                print("D")
            elif index_y_pos > mid_y_down and index_y_pos < mid_y_up:
                print("Zone grise")
                keybd_event(0x1E, 0, 2, 0)
                keybd_event(0x20, 0, 2, 0)