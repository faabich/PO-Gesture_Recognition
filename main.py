"""
Name:         main.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Entry point for the HandGesture application
"""

import customtkinter as ctk
import utils.HM_window as HM_window
import threading

width = 400
height = 480

app = ctk.CTk()

def start_HM_window(HM_width, HM_height):
    def run_HM_window():
        hm_window = HM_window.HM_window(HM_width, HM_height)
        hm_window.run()

    # AI GENERATED:'how to run tkinter and the hand gesture window at the same time ?'
    # Create a new thread for the HM_window to make it run separately
    thread = threading.Thread(target=run_HM_window)
    thread.daemon = True
    thread.start()

def checkbox_event():
    pass
#   show_resolution_options = ctk.

def slider_event(value):
    print(value)



def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)

slider = ctk.CTkSlider(app, from_=0, to=10, command=slider_event)
slider.grid(row=4, column=1, colspan=2)

label = ctk.CTkLabel(app,text="Select a resolution for the window")
label.grid(row=1, column=1, padx=10, pady=10)

optionmenu_var = ctk.StringVar(value="option 2")
optionmenu = ctk.CTkOptionMenu(app,values=["option 1", "option 2"],
                                         command=optionmenu_callback,
                                         variable=optionmenu_var)
optionmenu.grid(row=1, column=2, padx=10, pady=10)

check_var = ctk.StringVar(value="off")
custom_res_cb = ctk.CTkCheckBox(app, text="Use a custom resolution", command=checkbox_event, variable=check_var, onvalue="on", offvalue="off")
custom_res_cb.grid(row=2, column=1, pady=10)

button = ctk.CTkButton(app, text="Launch main window", command=lambda: start_HM_window(width, height))
button.grid(row=3, column=1, pady=10)


app.geometry(f"{width}x{height}")
app.mainloop()