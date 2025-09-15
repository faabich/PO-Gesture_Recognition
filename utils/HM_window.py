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
from utils.common import *
import cv2
import time
import threading

class HM_window:
    def __init__(self, width, height, mode=None, app=None, num_hands=1, canvas=None):
        self.CAMERA_WIDTH = width
        self.CAMERA_HEIGHT = height
        self.cap = None
        self.hand_detector = HandDetector(max_num_hands=num_hands)
        self.gestures = Gesture(canvas=canvas)
        self._stop_event = threading.Event()
        self.mode = (mode or "").replace('-', ' ').lower().strip()
        self.app = app
        self.label = None

    def set_video_label(self, label):
        self.label = label

    def stop(self):
        self._stop_event.set()

    def run(self):
        print("HM_window started")
        try:
            self.cap = VideoCamera(self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
            print("Camera initialized successfully")
        except RuntimeError as e:
            print(f"Failed to initialize camera: {e}")
            if self.app:
                self.app.after(0, lambda: update_status_label(self.app, f"Camera error: {e}"))
            self._stop_event.set()
            self._cleanup()
            return

        while not self._stop_event.is_set():
            start_time = time.time()
            success, frame = self.cap.read()
            if not success:
                print("Failed to read frame from camera.")
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            hand_landmarks_results, mp_drawing_utils, mp_hands_solutions = self.hand_detector.get_hand_landmarks(frame)

            mode = self.mode
            match mode:
                case "earth":
                    self.gestures.touchscreen_mode(hand_landmarks_results, frame, self.CAMERA_WIDTH, self.CAMERA_HEIGHT, False)
                case "particle love":
                    self.gestures.move_mouse(hand_landmarks_results, frame, self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
                    self.gestures.click_mouse(hand_landmarks_results, frame)
                case "paint" | "btd4" | "chess" | "ssp":
                    self.gestures.touchscreen_mode(hand_landmarks_results, frame, self.CAMERA_WIDTH, self.CAMERA_HEIGHT, True)

            cv2.imshow("Camera Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()

            processing_time = time.time() - start_time
            time.sleep(max(0.01, 0.033 - processing_time))  # Target ~30 FPS

        self._cleanup()
        print("HM_window stopped")

    def _cleanup(self):
        if self.cap is not None:
            try:
                self.cap.release()
                cv2.destroyAllWindows()
            except Exception as e:
                print(f"Error releasing camera: {e}")
            self.cap = None
        if self.label and self.app:
            self.app.after(0, lambda: self.label.configure(image=None))
        cv2.destroyAllWindows()
        print("HM_window resources released")