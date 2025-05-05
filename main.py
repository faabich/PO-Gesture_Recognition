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
import threading
import cv2

width = 425
height = 225

# Default camera resolution
cam_width = 1600
cam_height = 900

app = ctk.CTk()
app.title("Hand Gesture Recognition Configurator")

def start_HM_window(HM_width, HM_height):
    import cv2
    try:
        cv2.destroyAllWindows()  # Close any existing OpenCV windows
        cv2.startWindowThread() # Start a new thread to launch the OpenCV window in
        hm_window = HM_window.HM_window(HM_width, HM_height)
        hm_window.run()
        print("hello")
    except Exception as e:
        print(f"Error in HM_window thread: {e}")

def checkbox_event():
    pass

def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)

def checkbox_event_show_more_options():
    if custom_options_checkbox_var.get()=="on":
        # Show the additional options

        label.grid(row=4, column=0, columnspan=1)
        spinbox.grid(row=4, column=1, columnspan=2)
        optionmenu.grid(row=5, column=0, columnspan=3)
        button.grid(row=7, column=1, columnspan=1)
        app.geometry("425x600")
    else:
        spinbox.grid_forget()
        label.grid_forget()
        optionmenu.grid_forget()
        button.grid_forget()
        app.geometry("425x225")

def open_custom_demo_browser():
    import utils.custom_demo_browser
    custom_demo_browser.open_custom_demo_browser()

description = ctk.CTkLabel(app, text="Hand Gesture Recognition Demo Configurator Utility:\nTo quickly start a common demo, you can browse the\nready-to-use programs by clicking on the button below.", font=("Arial", 16))
description.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

demo_browser_button = ctk.CTkButton(app, text="Browse ready-to-use programs", command=open_custom_demo_browser)
demo_browser_button.grid(row=1, column=1, padx=10, pady=10)

bottom_description = ctk.CTkLabel(app, text="To start a custom demo, you can set the camera resolution\nand the main window size below.", font=("Arial", 16))
bottom_description.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

custom_options_checkbox_var = ctk.StringVar(value="off")
custom_options_checkbox = ctk.CTkCheckBox(app, text="Use custom options",variable=custom_options_checkbox_var, onvalue="on", offvalue="off", command=checkbox_event_show_more_options)
custom_options_checkbox.grid(row=3, column=1, columnspan=1, padx=10, pady=10)

spinbox = sb.FloatSpinbox(app, width=150, step_size=1)

label = ctk.CTkLabel(app,text="Number of hands\n to track")

optionmenu_var = ctk.StringVar(value="option 2")
optionmenu = ctk.CTkOptionMenu(app,values=["option 1", "option 2"], command=optionmenu_callback, variable=optionmenu_var)

check_var = ctk.StringVar(value="off")
# custom_res_cb = ctk.CTkCheckBox(app, text="Use a custom resolution", command=checkbox_event, variable=check_var, onvalue="on", offvalue="off")

button = ctk.CTkButton(app, text="Launch main window", command=lambda: start_HM_window(cam_width, cam_height))

app.geometry(f"{width}x{height}")
app.mainloop()