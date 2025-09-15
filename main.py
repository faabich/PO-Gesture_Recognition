"""
Name:         main.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Entry point for the HandGesture application
"""

import customtkinter as ctk
import utils.HM_window as HM_window
import utils.float_spinbox as sb
from utils.custom_demo_browser import open_browser
import threading
import cv2
import traceback # AI generated (threading optimization)

from utils import custom_demo_browser

width = 425
height = 225

# Default camera resolution
cam_width = 1600
cam_height = 900

app = ctk.CTk()
app.title("Hand Gesture Recognition Configurator")

# Create a new frame for custom options
custom_options_frame = ctk.CTkFrame(app)
custom_options_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
custom_options_frame.forget() # Hide the frame by default

custom_options_frame.grid_columnconfigure(0, weight=1)
custom_options_frame.grid_columnconfigure(1, weight=1)
custom_options_frame.grid_columnconfigure(2, weight=1)

hm_window = HM_window

# AI generated (threading optimization)
def threaded_hm_window_runner(width, height):
    global hm_window
    try:
        hm_window = HM_window.HM_window(width, height)
        hm_window.run("basic")
    except Exception as e:
        print("Error in threaded_hm_window_runner:")
        print(e)
        traceback.print_exc()

def start_HM_window(HM_width, HM_height, preset=None):
    import cv2
    # AI generated (threading optimization)
    try:
        cv2.destroyAllWindows()  # Close any existing OpenCV windows
        thread = threading.Thread(target=threaded_hm_window_runner, args=(HM_width, HM_height), daemon=True)
        thread.start()
        print("started Hand Movement Window")
    except Exception as e:
        print(f"Error in HM_window thread: {e}")

def checkbox_event():
    pass

hand_tracking_method = "touchscreen"

def optionmenu_callback(choice):
    global hand_tracking_method
    hand_tracking_method = choice
    print(f"Selected option: {choice}")

def open_hand_selection_utility():
    pass

def checkbox_event_show_more_options():
    if custom_options_checkbox_var.get()=="on":
        custom_options_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew") # Show the additional options
        app.geometry("425x600")
    else:
        custom_options_frame.grid_forget() # Hide the additional options
        app.geometry("425x225")

description = ctk.CTkLabel(app, text="Hand Gesture Recognition Demo Configurator Utility:\nTo quickly start a common demo, you can browse the\nready-to-use programs by clicking on the button below.", font=("Arial", 16))
description.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

demo_browser_button = ctk.CTkButton(app, text="Browse ready-to-use programs", command=lambda: open_browser(main_frame=app, width=800, height=600))
demo_browser_button.grid(row=1, column=1, padx=10, pady=10)

bottom_description = ctk.CTkLabel(app, text="To start a custom demo, you can set the camera resolution\nand the main window size below.", font=("Arial", 16))
bottom_description.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

custom_options_checkbox_var = ctk.StringVar(value="off")
custom_options_checkbox = ctk.CTkCheckBox(app, text="Use custom options",variable=custom_options_checkbox_var, onvalue="on", offvalue="off", command=checkbox_event_show_more_options)
custom_options_checkbox.grid(row=3, column=1, columnspan=1, padx=10, pady=10)

technology_label = ctk.CTkLabel(custom_options_frame, text="Technology:")
technology_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

# Choosing which 'technology' to use (mouse-like, touchscreen or multiple-input)
optionmenu_var = ctk.StringVar(value="choose a technology")
optionmenu = ctk.CTkOptionMenu(custom_options_frame,values=["mouse-like", "touchscreen", "multiple-input"], command=optionmenu_callback, variable=optionmenu_var)
optionmenu.grid(row=0, column=2, padx=10, pady=10, sticky="w")

num_hands_label = ctk.CTkLabel(custom_options_frame,text="Number of hands to track")
num_hands_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")

spinbox = sb.FloatSpinbox(custom_options_frame, width=140, step_size=1)
spinbox.grid(row=1, column=2, padx=10, pady=10, sticky="w")

check_var = ctk.StringVar(value="off")
# custom_res_cb = ctk.CTkCheckBox(app, text="Use a custom resolution", command=checkbox_event, variable=check_var, onvalue="on", offvalue="off")

track_points_label = ctk.CTkLabel(custom_options_frame, text="Track hand points:")
track_points_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")

open_hand_points_selection_utility_button = ctk.CTkButton(custom_options_frame, text="Open hand points selection utility", command=open_hand_selection_utility)

launch_button = ctk.CTkButton(custom_options_frame, text="Launch main window", command=lambda: start_HM_window(cam_width, cam_height))
launch_button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

start_HM_window(cam_width, cam_height)

app.geometry(f"{width}x{height}")
app.mainloop()