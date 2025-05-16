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
import cv2

class HM_window:
    def __init__(self, width, height):
        self.CAMERA_WIDTH = width
        self.CAMERA_HEIGHT = height
        self.cap = VideoCamera(self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
        self.hand_detector = HandDetector()
        self.gestures = Gesture()
        self.running = True

    def run(self):
        print("HM_window started")
        while self.running:
            success, frame = self.cap.read()
            if success:
                print("HM_window running")
                frame = cv2.flip(frame, 1)
                landmarks = self.hand_detector.findHandsLandMarks(frame, draw=False)
                self.gestures.move_mouse(landmarks, frame, self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
                self.gestures.click_mouse(landmarks, frame)
                cv2.imshow("capture image", frame)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    self.stop()

        self.cap.release()
        cv2.destroyAllWindows()
        print("HM_window stopped")

    def stop(self):
        self.running = False