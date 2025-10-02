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
import threading


class HM_window:
    def __init__(self, width, height):
        self.CAMERA_WIDTH = width
        self.CAMERA_HEIGHT = height
        self.cap = VideoCamera(self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
        self.hand_detector = HandDetector()
        self.gestures = Gesture()
        self.running = True
        self.camera_thread = None
        self.parameter = None

    def start_camera_thread(self, parameter):
        """Démarre le thread de traitement de la caméra"""
        self.parameter = parameter
        self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.camera_thread.start()
        print("Camera thread started")

    def _camera_loop(self):
        """Boucle de traitement de la caméra (dans un thread séparé)"""
        print("Camera loop started in separate thread")

        while self.running:
            success, frame = self.cap.read()

            if not success:
                print("Failed to read frame from camera.")
                continue

            # Flip frame
            frame = cv2.flip(frame, 1)

            # Detect hands
            hand_landmarks_results, mp_drawing_utils, mp_hands_solutions = self.hand_detector.get_hand_landmarks(frame)

            # Process gestures based on parameter
            if self.parameter == "basic" or self.parameter == "earth":
                self.gestures.touchscreen_mode(hand_landmarks_results)
            elif self.parameter == "particle love":
                self.gestures.move_mouse(hand_landmarks_results, frame, self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
                self.gestures.click_mouse(hand_landmarks_results, frame)
            elif self.parameter in ["paint", "btd4", "chess", "ssp"]:
                self.gestures.touchscreen_mode(hand_landmarks_results)

            # Show camera feed
            cv2.imshow("capture image", frame)

            # Check for quit
            if cv2.waitKey(10) & 0xFF == ord('q'):
                self.stop()
                break

        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("Camera loop stopped")

    def run_tkinter(self):
        """Lance la boucle Tkinter (DOIT être appelé depuis le thread principal)"""
        print("Initializing Tkinter window in main thread...")
        self.gestures.initialize_tkinter_window()

        # Lancer la mainloop Tkinter (bloquant)
        self.gestures.root.mainloop()
        print("Tkinter mainloop ended")

    def stop(self):
        """Arrête le traitement"""
        self.running = False
        if self.gestures.root:
            self.gestures.root.quit()

# class HM_window:
#     def __init__(self, width, height):
#         self.CAMERA_WIDTH = width
#         self.CAMERA_HEIGHT = height
#         self.cap = VideoCamera(self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
#         self.hand_detector = HandDetector()
#         self.gestures = Gesture()
#         self.running = True
#
#     def run(self, parameter=None):
#         print("HM_window started")
#         print("Attempting to read from camera...")
#         while self.running:
#             success, frame = self.cap.read()
#             if not success:
#                 print("Failed to read frame from camera.")
#             if success:
#                 frame = cv2.flip(frame, 1)
#                 hand_landmarks_results, mp_drawing_utils, mp_hands_solutions = self.hand_detector.get_hand_landmarks(frame)
#                 match parameter:
#                     case "basic":
#                         self.gestures.touchscreen_mode(hand_landmarks_results)
#                     case "earth":
#                         self.gestures.touchscreen_mode(hand_landmarks_results)
#                     case "particle love":
#                         self.gestures.move_mouse(hand_landmarks_results, frame, self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
#                         self.gestures.click_mouse(hand_landmarks_results, frame)
#                     case "paint":
#                         self.gestures.touchscreen_mode(hand_landmarks_results, frame, self.CAMERA_WIDTH, self.CAMERA_HEIGHT,True)
#                     case "btd4":
#                         self.gestures.touchscreen_mode(hand_landmarks_results, frame, self.CAMERA_WIDTH, self.CAMERA_HEIGHT,True)
#                     case "chess":
#                         self.gestures.touchscreen_mode(hand_landmarks_results, frame, self.CAMERA_WIDTH, self.CAMERA_HEIGHT,True)
#                     case "ssp":
#                         self.gestures.touchscreen_mode(hand_landmarks_results, frame, self.CAMERA_WIDTH, self.CAMERA_HEIGHT,True)
#                 cv2.imshow("capture image", frame)
#                 if cv2.waitKey(10) & 0xFF == ord('q'):
#                     self.stop()
#
#         self.cap.release()
#         cv2.destroyAllWindows()
#         print("HM_window stopped")
#
#     def stop(self):
#         self.running = False