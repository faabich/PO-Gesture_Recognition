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

width = 1600
height = 900

# Default camera resolution
cam_width = 1600
cam_height = 900

app = ctk.CTk()
app.title("Hand Gesture Recognition Configurator")
app.geometry(f"{1600}x{900}")
app.minsize(400,400)

title_label = ctk.CTkLabel(app, text="GAME HUB", text_color="black",
                                        font=ctk.CTkFont(size=60, weight="bold"))
title_label.grid(row=0, column=0, columnspan=4, pady=20)

app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure(2, weight=1)
app.grid_columnconfigure(3, weight=1)
app.grid_columnconfigure(0, weight=1)

hm_window = HM_window

"""BUTTONS"""

earth_button = ctk.CTkButton(app, text="Google Earth", command=lambda: custom_demo_browser.open_url('https://earth.google.com/web/@46.82164296,6.50019955,1077.83283169a,556.60504226d,35y,238.80930889h,45t', preset="earth"),
                                        image=custom_demo_browser.img_earth, compound="top", fg_color="white", text_color="black",
                                        hover_color="lightgray",
                                        font=app.CTkFont(size=20, weight="bold"))
earth_button.grid(column=0, row=1, padx=20, pady=20)

particle_love_button = ctk.CTkButton(app, text="Particle Love Javascript Demo", command=lambda: custom_demo_browser.open_url('https://particle-love.com/', preset="particle love"),
                                        image=custom_demo_browser.img_particlelove, compound="top", fg_color="white", text_color="black",
                                        hover_color="lightgray",
                                        font=app.CTkFont(size=20, weight="bold"))
particle_love_button.grid(column=1, row=1, padx=20, pady=20)

paint_button = ctk.CTkButton(app, text="Paint", command=lambda: custom_demo_browser.open_url('https://sketch.io/sketchpad/', preset="paint"),
                                            image=custom_demo_browser.img_paint, compound="top", fg_color="white", text_color="black",
                                            hover_color="lightgray",
                                            font=app.CTkFont(size=20, weight="bold"))
paint_button.grid(column=2, row=1, padx=20, pady=20)

btd4_button = ctk.CTkButton(app, text="bloons tower deffense 4", command=lambda: custom_demo_browser.open_url('https://www.crazygames.com/game/bloons-tower-defense-4', preset="btd4"),
                                        image=custom_demo_browser.img_btd4, compound="top", fg_color="white", text_color="black",
                                        hover_color="lightgray",
                                        font=app.CTkFont(size=20, weight="bold"))
btd4_button.grid(column=3, row=1, padx=20, pady=20)

chess_button = ctk.CTkButton(app, text="Play Chess", command=lambda: custom_demo_browser.open_url('https://plainchess.timwoelfle.de/', preset="chess"),
                                        image=custom_demo_browser.img_chess, compound="top", fg_color="white", text_color="black",
                                        hover_color="lightgray",
                                        font=app.CTkFont(size=20, weight="bold"))
chess_button.grid(column=0, row=2, padx=20, pady=20)

ssp_button = ctk.CTkButton(app, text="Sound Space+", command=lambda: custom_demo_browser.open_program("ssp", "SoundSpacePlus.exe", preset="ssp"),
                                        image=custom_demo_browser.img_ssp, compound="top", fg_color="white", text_color="black",
                                        hover_color="lightgray",
                                        font=app.CTkFont(size=20, weight="bold"))
ssp_button.grid(column=1, row=2, padx=20, pady=20)

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


start_HM_window(cam_width, cam_height)

app.geometry(f"{width}x{height}")
app.mainloop()