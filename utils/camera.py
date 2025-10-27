"""
Name:         camera.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         27.10.2025
Version:      0.1
Description:  Camera creation with opencv and queue for threading
"""

from utils.hand_detector import HandDetector
import cv2
import queue
import threading


class VideoCamera(object):
    def __init__(self,app, width=1600, height=900):
        self.app = app
        self.hand_detector = HandDetector()
        self.cap = cv2.VideoCapture(0)
        self.width = width
        self.height = height
        self.status = True
        self.frame = None
        self.success = False
        self.frame_queue = queue.Queue(maxsize=2)           # IA: How to transfer images between threads
        self.landmarks_queue = queue.Queue(maxsize=2)

        # Width and height of window
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Start camera thread
        self.camera_thread = threading.Thread(
            target=self.camera_worker,
            daemon=True,
            name="CameraThread"
        )
        self.camera_thread.start()

        self.update_frame()

    def camera_worker(self):
        while self.status:
            self.success, frame = self.cap.read()
            if self.success:
                landmarks = self.hand_detector.get_hand_landmarks(frame)
                if not self.frame_queue.full():         # IA: How to transfer images between threads
                    self.frame_queue.put(frame)
                if not self.landmarks_queue.full():
                    self.landmarks_queue.put(landmarks)

    def update_frame(self):
        try:
            frame = self.frame_queue.get_nowait()       # IA: How to transfer images between threads
            self.landmarks_queue.get_nowait()
            if frame is not None:
                cv2.imshow("capture image", frame)        # Activate/deactivate camera visualisation
        except queue.Empty:
            pass

        self.app.after(15, self.update_frame)  # Update frame each 30 ms ~30fps

    def get_landmarks(self):
        try:
            return self.landmarks_queue.get_nowait()        # IA: How to transfer images between threads
        except queue.Empty:
            return None

    # Close camera
    def release(self):
        self.status = False
        self.cap.release()