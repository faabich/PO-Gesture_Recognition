"""
Name:         main.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Entry point for the HandGesture application
"""

import customtkinter as ctk
import cv2
from utils.common import start_HM_window, stop_hm_window, update_status_label
from utils.camera import VideoCamera
from utils.hand_detector import HandDetector
import utils.float_spinbox as sb
from utils.custom_demo_browser import open_browser
import time

width = 425
height = 225
cam_width = 640
cam_height = 480

app = ctk.CTk()
app.title("Hand Gesture Recognition Configurator")

# Create a transparent canvas for hand overlay
canvas = ctk.CTkCanvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight(), bg="black", highlightthickness=0)
canvas.grid(row=0, column=0, rowspan=10, columnspan=3, sticky="nsew")

# Create a new frame for custom options
custom_options_frame = ctk.CTkFrame(app)
custom_options_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
custom_options_frame.forget()
custom_options_frame.grid_columnconfigure(0, weight=1)
custom_options_frame.grid_columnconfigure(1, weight=1)
custom_options_frame.grid_columnconfigure(2, weight=1)

def checkbox_event():
    pass

def open_hand_selection_utility():
    pass

def checkbox_event_show_more_options():
    if custom_options_checkbox_var.get() == "on":
        custom_options_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        app.geometry("425x600")
    else:
        custom_options_frame.grid_forget()
        app.geometry("425x225")

def open_browser_wrapper():
    stop_hm_window(app)
    try:
        open_browser(main_frame=app, width=800, height=600)
    except Exception as e:
        print(f"Error in open_browser: {e}")
        app.after(0, lambda: update_status_label(app, f"Error opening browser: {e}"))

def on_closing():
    stop_hm_window(app)
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)

description = ctk.CTkLabel(
    app,
    text="Hand Gesture Recognition Demo Configurator Utility:\nTo quickly start a common demo, you can browse the\nready-to-use programs by clicking on the button below.",
    font=("Arial", 16)
)
description.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

demo_browser_button = ctk.CTkButton(
    app,
    text="Browse ready-to-use programs",
    command=lambda: open_browser(main_frame=app, width=800, height=600)
)
demo_browser_button.grid(row=1, column=1, padx=10, pady=10)

bottom_description = ctk.CTkLabel(
    app,
    text="To start a custom demo, you can set the camera resolution\nand the main window size below.",
    font=("Arial", 16)
)
bottom_description.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

custom_options_checkbox_var = ctk.StringVar(value="off")
custom_options_checkbox = ctk.CTkCheckBox(
    app,
    text="Use custom options",
    variable=custom_options_checkbox_var,
    onvalue="on",
    offvalue="off",
    command=checkbox_event_show_more_options
)
custom_options_checkbox.grid(row=3, column=1, columnspan=1, padx=10, pady=10)

hand_tracking_method = "touchscreen"
def optionmenu_callback(choice):
    global hand_tracking_method
    hand_tracking_method = choice
    print(f"Selected option: {choice}")

technology_label = ctk.CTkLabel(custom_options_frame, text="Technology:")
technology_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

optionmenu_var = ctk.StringVar(value="choose a technology")
optionmenu = ctk.CTkOptionMenu(
    custom_options_frame,
    values=["mouse-like", "touchscreen", "multiple-input"],
    command=optionmenu_callback,
    variable=optionmenu_var
)
optionmenu.grid(row=0, column=2, padx=10, pady=10, sticky="w")

num_hands_label = ctk.CTkLabel(custom_options_frame, text="Number of hands to track")
num_hands_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")
spinbox = sb.FloatSpinbox(custom_options_frame, width=140, step_size=1)
spinbox.grid(row=1, column=2, padx=10, pady=10, sticky="w")

open_hand_points_selection_utility_button = ctk.CTkButton(
    custom_options_frame,
    text="Open hand points selection utility",
    command=open_hand_selection_utility
)
open_hand_points_selection_utility_button.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

launch_button = ctk.CTkButton(
    custom_options_frame,
    text="Launch main window",
    command=lambda: start_HM_window(app, cam_width, cam_height, hand_tracking_method, int(spinbox.get()), canvas)
)
launch_button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

def test_camera_and_hand_detection(width, height, num_hands=1):
    try:
        cap = VideoCamera(width, height)
        detector = HandDetector(max_num_hands=num_hands)
        start_time = time.time()
        success, frame = cap.read()
        if not success:
            print("Camera test failed: Could not read frame")
            cap.release()
            return
        frame = cv2.flip(frame, 1)
        results, _, _ = detector.get_hand_landmarks(frame)
        processing_time = time.time() - start_time
        print(f"Camera and hand detection test successful, processed frame in {processing_time:.3f} seconds")
        if results.multi_hand_landmarks:
            print(f"Detected {len(results.multi_hand_landmarks)} hand(s)")
        else:
            print("No hands detected")
        cap.release()
    except Exception as e:
        print(f"Camera/hand detection test failed: {e}")

test_button = ctk.CTkButton(
    app,
    text="Test Camera & Hand Detection",
    command=lambda: test_camera_and_hand_detection(cam_width, cam_height, int(spinbox.get()))
)
test_button.grid(row=4, column=2, padx=10, pady=10)

# Ensure canvas is below other widgets after all are created
app.update()  # Update the window to ensure all widgets are rendered
canvas.lower()  # Lower the canvas relative to other widgets

app.geometry(f"{width}x{height}")
app.mainloop()