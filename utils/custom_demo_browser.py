"""
Name:         hub.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         01.05.2025
Version:      0.1
Description:  HUB WINDOW NAVIGATION
"""

import customtkinter as ctk
import webbrowser
import os
import subprocess
from utils.gesture import Gesture
from PIL import Image

# Keep a Gesture instance if the project expects it
try:
    gestures = Gesture()
except Exception:
    gestures = None


def open_browser(parent=None, width=800, height=400):
    """
    Populate the provided `parent` frame with the demo browser widgets.
    This function will NOT create any new top-level window or call geometry/title
    on the passed frame. It clears previous children and attaches widgets inside
    `parent` so they appear inside `demo_browser_frame` from `main.py`.
    If `parent` is None, nothing is done.
    """
    if parent is None:
        return

    # Clear previous children so repeated calls are safe
    for child in parent.winfo_children():
        try:
            child.destroy()
        except Exception:
            pass

    # Create a scrollable content area inside the provided frame
    content_frame = ctk.CTkScrollableFrame(parent, height=max(100, height - 40))
    content_frame.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

    # Ensure parent allows expansion
    try:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
    except Exception:
        pass

    # Title
    title_label = ctk.CTkLabel(content_frame, text="GAME HUB", text_color="black",
                               font=ctk.CTkFont(size=24, weight="bold"))
    title_label.grid(row=0, column=0, columnspan=4, pady=(8,12), padx=8, sticky="w")

    # Configure columns inside content
    for col in range(4):
        try:
            content_frame.grid_columnconfigure(col, weight=1)
        except Exception:
            pass

    # Helpers
    def change_preset(preset):
        try:
            if gestures and preset:
                gestures.touchscreen_mode(None)
        except Exception:
            pass

    def open_url(url, preset=None):
        try:
            webbrowser.open(url)
        except Exception:
            pass
        change_preset(preset)

    def open_program(folder, program_name, preset=None):
        try:
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            exe_path = os.path.join(parent_dir, "games", folder, program_name)
            if os.path.exists(exe_path):
                subprocess.Popen([exe_path], shell=False)
            else:
                print(f"Executable not found: {exe_path}")
        except Exception as e:
            print("open_program error:", e)
        change_preset(preset)

    # Load images (silent fallback)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_folder = os.path.join(root_dir, "img")
    def load_image(name, size=(200,200)):
        try:
            path = os.path.join(img_folder, name)
            img = Image.open(path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception:
            return None

    img_earth = load_image("earth.png")
    img_particlelove = load_image("particlelove.png")
    img_paint = load_image("paint.jpg")
    img_btd4 = load_image("btd4.jpg")
    img_chess = load_image("chess.png")
    img_ssp = load_image("ssp.png")

    # Place buttons inside content_frame
    earth_button = ctk.CTkButton(content_frame, text="Google Earth",
                                 command=lambda: open_url('https://earth.google.com/web/', preset="earth"),
                                 image=img_earth, compound="top")
    earth_button.grid(column=0, row=1, padx=8, pady=8, sticky="nsew")

    particle_love_button = ctk.CTkButton(content_frame, text="Particle Love",
                                         command=lambda: open_url('https://particle-love.com/', preset="particle love"),
                                         image=img_particlelove, compound="top")
    particle_love_button.grid(column=1, row=1, padx=8, pady=8, sticky="nsew")

    paint_button = ctk.CTkButton(content_frame, text="Paint",
                                command=lambda: open_url('https://sketch.io/sketchpad/', preset="paint"),
                                image=img_paint, compound="top")
    paint_button.grid(column=2, row=1, padx=8, pady=8, sticky="nsew")

    btd4_button = ctk.CTkButton(content_frame, text="Bloons TD4",
                                command=lambda: open_url('https://www.crazygames.com/game/bloons-tower-defense-4', preset="btd4"),
                                image=img_btd4, compound="top")
    btd4_button.grid(column=3, row=1, padx=8, pady=8, sticky="nsew")

    chess_button = ctk.CTkButton(content_frame, text="Play Chess",
                                command=lambda: open_url('https://plainchess.timwoelfle.de/', preset="chess"),
                                image=img_chess, compound="top")
    chess_button.grid(column=0, row=2, padx=8, pady=8, sticky="nsew")

    ssp_button = ctk.CTkButton(content_frame, text="Sound Space+",
                               command=lambda: open_program("ssp", "SoundSpacePlus.exe", preset="ssp"),
                               image=img_ssp, compound="top")
    ssp_button.grid(column=1, row=2, padx=8, pady=8, sticky="nsew")

    # Finalize: ensure UI updates
    try:
        parent.update_idletasks()
    except Exception:
        pass
"""
Name:         hub.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         01.05.2025
Version:      0.1
Description:  HUB WINDOW NAVIGATION
"""

import customtkinter as ctk
import webbrowser
import customtkinter
import os
import subprocess
from utils.gesture import *
from utils.hand_detector import *
from PIL import Image
import utils.HM_window as HM_window

gestures = Gesture()

def add_demo(name, img_path, technology):
    pass

def open_link(url):
    webbrowser.open(url)

def open_browser(main_frame, width, height):
    from main import start_HM_window
    app = ctk.CTkScrollableFrame(main_frame)
    app.geometry(f"{width}x{height}")
    app.title("Demo browser")
    app.minsize(400,400)

    """WINDOW GLOBAL"""
    title_label = customtkinter.CTkLabel(app, text="GAME HUB", text_color="black",
                                         font=customtkinter.CTkFont(size=60, weight="bold"))
    title_label.grid(row=0, column=0, columnspan=4, pady=20)

    # SIZE OF THE WINDOW
    width = app.winfo_screenwidth() - 15

    height = app.winfo_screenheight()
    app.geometry("%dx%d+0+0" % (width, height))

    # GRID CONFIGURATION
    app.grid_columnconfigure(0, weight=1)
    app.grid_columnconfigure(1, weight=1)
    app.grid_columnconfigure(2, weight=1)
    app.grid_columnconfigure(3, weight=1)

    def change_preset(preset):
        match preset:
            case "earth":
                gestures.touchscreen_mode(hand_landmarks_results)
            case "particle love":
                gestures.touchscreen_mode(hand_landmarks_results)
            case "paint":
                gestures.touchscreen_mode(hand_landmarks_results)
            case "btd4":
                gestures.touchscreen_mode(hand_landmarks_results)
            case "chess":
                gestures.touchscreen_mode(hand_landmarks_results)
            case "ssp":
                gestures.touchscreen_mode(hand_landmarks_results)
            

    def open_url(url, preset=None):
        webbrowser.open(url)
        try: 
            start_HM_window(width, height, preset)
            print("successfully started HM_window")
        except Exception as e:
            print("Error in start_HM_window:")
            print(e)
        try:
            change_preset(preset)
        except Exception as e:
            print("Error in change_preset:")
            print(e)

    def open_program(folder, program_name, preset=None):
        try:
            # Resolve project root from this file's location
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Path to the executable in the games/<folder> subfolder
            exe_path = os.path.join(parent_dir, "games", folder, program_name)

            # Check if the file exists and launch it
            if os.path.exists(exe_path):
                try:
                    subprocess.Popen([exe_path], shell=True)
                except Exception as e:
                    print("Erreur lors du lancement du jeu:", e)
            else:
                print(f"Erreur: Le fichier {exe_path} n'existe pas")
        except Exception as e:
            print("open_program unexpected error:", e)
        try:
            change_preset(preset)
        except Exception as e:
            print("Error in change_preset:")
            print(e)

    # Old individual open_* helpers removed: buttons call `open_url` or `open_program` directly.


    """img LINK LIST"""
    # Get path to project root (parent of utils folder)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_folder = os.path.join(root_dir, "img")

    img_earth = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "earth.png")),
        size=(200, 200)
    )

    img_particlelove = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "particlelove.png")),
        size=(200, 200)
    )

    img_paint = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "paint.jpg")),
        size=(200, 200)
    )

    img_btd4 = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "btd4.jpg")),
        size=(200, 200)
    )

    img_chess = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "chess.png")),
        size=(200, 200)
    )

    img_ssp = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "ssp.png")),
        size=(200, 200)
    )

    