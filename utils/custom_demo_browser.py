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
    from main import start_HM_window  # Local import to avoid circular dependency
    game_browser = ctk.CTkToplevel(main_frame)
    game_browser.geometry(f"{width}x{height}")
    game_browser.title("Demo browser")
    game_browser.minsize(400,400)
    game_browser.grab_set() # Focus on this window, make the main frame unclickable

    """WINDOW GLOBAL"""
    title_label = customtkinter.CTkLabel(game_browser, text="GAME HUB", text_color="black",
                                         font=customtkinter.CTkFont(size=60, weight="bold"))
    title_label.grid(row=0, column=0, columnspan=4, pady=20)

    # SIZE OF THE WINDOW
    width = game_browser.winfo_screenwidth() - 15

    height = game_browser.winfo_screenheight()
    game_browser.geometry("%dx%d+0+0" % (width, height))

    # GRID CONFIGURATION
    game_browser.grid_columnconfigure(0, weight=1)
    game_browser.grid_columnconfigure(1, weight=1)
    game_browser.grid_columnconfigure(2, weight=1)
    game_browser.grid_columnconfigure(3, weight=1)

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
        """Start an executable located in the repository's games/<folder>/ directory
        and then start the HM_window with an optional preset.
        """
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
        dark_image=Image.open(os.path.join(img_folder, "earth.png")),
        size=(200, 200)
    )

    img_particlelove = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "particlelove.png")),
        dark_image=Image.open(os.path.join(img_folder, "particlelove.png")),
        size=(200, 200)
    )

    img_paint = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "paint.jpg")),
        dark_image=Image.open(os.path.join(img_folder, "paint.jpg")),
        size=(200, 200)
    )

    img_btd4 = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "btd4.jpg")),
        dark_image=Image.open(os.path.join(img_folder, "btd4.jpg")),
        size=(200, 200)
    )

    img_chess = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "chess.png")),
        dark_image=Image.open(os.path.join(img_folder, "chess.png")),
        size=(200, 200)
    )

    img_ssp = customtkinter.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "ssp.png")),
        dark_image=Image.open(os.path.join(img_folder, "ssp.png")),
        size=(200, 200)
    )

    """BUTTONS"""

    earth_button = customtkinter.CTkButton(game_browser, text="Google Earth", command=lambda: open_url('https://earth.google.com/web/@46.82164296,6.50019955,1077.83283169a,556.60504226d,35y,238.80930889h,45t', preset="earth"),
                                           image=img_earth, compound="top", fg_color="white", text_color="black",
                                           hover_color="lightgray",
                                           font=customtkinter.CTkFont(size=20, weight="bold"))
    earth_button.grid(column=0, row=1, padx=20, pady=20)

    particle_love_button = customtkinter.CTkButton(game_browser, text="Particle Love Javascript Demo", command=lambda: open_url('https://particle-love.com/', preset="particle love"),
                                            image=img_particlelove, compound="top", fg_color="white", text_color="black",
                                            hover_color="lightgray",
                                            font=customtkinter.CTkFont(size=20, weight="bold"))
    particle_love_button.grid(column=1, row=1, padx=20, pady=20)

    paint_button = customtkinter.CTkButton(game_browser, text="Paint", command=lambda: open_url('https://sketch.io/sketchpad/', preset="paint"),
                                             image=img_paint, compound="top", fg_color="white", text_color="black",
                                             hover_color="lightgray",
                                             font=customtkinter.CTkFont(size=20, weight="bold"))
    paint_button.grid(column=2, row=1, padx=20, pady=20)

    btd4_button = customtkinter.CTkButton(game_browser, text="bloons tower deffense 4", command=lambda: open_url('https://www.crazygames.com/game/bloons-tower-defense-4', preset="btd4"),
                                          image=img_btd4, compound="top", fg_color="white", text_color="black",
                                          hover_color="lightgray",
                                          font=customtkinter.CTkFont(size=20, weight="bold"))
    btd4_button.grid(column=3, row=1, padx=20, pady=20)

    chess_button = customtkinter.CTkButton(game_browser, text="Play Chess", command=lambda: open_url('https://plainchess.timwoelfle.de/', preset="chess"),
                                           image=img_chess, compound="top", fg_color="white", text_color="black",
                                           hover_color="lightgray",
                                           font=customtkinter.CTkFont(size=20, weight="bold"))
    chess_button.grid(column=0, row=2, padx=20, pady=20)

    ssp_button = customtkinter.CTkButton(game_browser, text="Sound Space+", command=lambda: open_program("ssp", "SoundSpacePlus.exe", preset="ssp"),
                                         image=img_ssp, compound="top", fg_color="white", text_color="black",
                                         hover_color="lightgray",
                                         font=customtkinter.CTkFont(size=20, weight="bold"))
    ssp_button.grid(column=1, row=2, padx=20, pady=20)