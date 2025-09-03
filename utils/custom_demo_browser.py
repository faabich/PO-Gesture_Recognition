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
from PIL import Image
from utils.common import start_HM_window


def add_demo(name, img_path, technology):
    pass

def open_link(url):
    webbrowser.open(url)

def open_browser(main_frame, width, height):
    game_browser = ctk.CTkToplevel(main_frame)
    game_browser.geometry(f"{width}x{height}")
    game_browser.title("Demo browser")
    game_browser.minsize(400,400)
    game_browser.grab_set() # Focus on this window, make the main frame unclickable

    # Alexandre:
    """WINDOW GLOBAL"""
    title_label = ctk.CTkLabel(game_browser, text="GAME HUB", text_color="black", font=ctk.CTkFont(size=60, weight="bold"))
    title_label.grid(row=0, column=0, columnspan=4, pady=20)

    # GRID CONFIGURATION
    game_browser.grid_columnconfigure(0, weight=1)
    game_browser.grid_columnconfigure(1, weight=1)
    game_browser.grid_columnconfigure(2, weight=1)
    game_browser.grid_columnconfigure(3, weight=1)

    def open_earth():
        print("Opening Google Earth...")
        webbrowser.open('https://earth.google.com/')
        try:
            start_HM_window(main_frame, width, height, "earth")
            print("Google Earth HM_window started")
        except Exception as e:
            print(f"Error in open_earth: {e}")

    def open_particle_love():
        print("Opening Particle Love...")
        webbrowser.open('https://particle-love.com/')
        try:
            start_HM_window(main_frame, width, height, "particle-love")
            print("Particle Love HM_window started")
        except Exception as e:
            print(f"Error in open_particle_love: {e}")

    def open_youtube():
        print("Opening YouTube...")
        webbrowser.open('https://www.youtube.com/')
        try:
            start_HM_window(main_frame, width, height, "youtube")
            print("YouTube HM_window started")
        except Exception as e:
            print(f"Error in open_youtube: {e}")

    def open_btd4():
        print("Opening BTD4...")
        webbrowser.open('https://www.crazygames.com/game/bloons-tower-defense-4')
        try:
            start_HM_window(main_frame, width, height, "btd4")
            print("BTD4 HM_window started")
        except Exception as e:
            print(f"Error in open_btd4: {e}")


    """img LINK LIST"""
    # Get path to project root (parent of utils folder)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_folder = os.path.join(root_dir, "img")

    img_earth = ctk.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "earth.png")),
        dark_image=Image.open(os.path.join(img_folder, "earth.png")),
        size=(200, 200)
    )

    img_particlelove = ctk.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "particlelove.png")),
        dark_image=Image.open(os.path.join(img_folder, "particlelove.png")),
        size=(200, 200)
    )

    img_youtube = ctk.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "youtube.png")),
        dark_image=Image.open(os.path.join(img_folder, "youtube.png")),
        size=(200, 200)
    )

    img_btd4 = ctk.CTkImage(
        light_image=Image.open(os.path.join(img_folder, "btd4.jpg")),
        dark_image=Image.open(os.path.join(img_folder, "btd4.jpg")),
        size=(200, 200)
    )


    """BUTTONS"""

    earth_button = ctk.CTkButton(game_browser, text="google earth", command=open_earth,
                                           image=img_earth, compound="top", fg_color="white", text_color="black",
                                           hover_color="lightgray",
                                           font=ctk.CTkFont(size=20, weight="bold"))
    earth_button.grid(column=0, row=1, padx=20, pady=20)

    particle_love_button = ctk.CTkButton(game_browser, text="Particle Love Javascript Demo", command=open_particle_love,
                                            image=img_particlelove, compound="top", fg_color="white", text_color="black",
                                            hover_color="lightgray",
                                            font=ctk.CTkFont(size=20, weight="bold"))
    particle_love_button.grid(column=1, row=1, padx=20, pady=20)

    youtube_button = ctk.CTkButton(game_browser, text="youtube", command=open_youtube,
                                             image=img_youtube, compound="top", fg_color="white", text_color="black",
                                             hover_color="lightgray",
                                             font=ctk.CTkFont(size=20, weight="bold"))
    youtube_button.grid(column=2, row=1, padx=20, pady=20)

    btd4_button = ctk.CTkButton(game_browser, text="bloons tower deffense 4", command=open_btd4,
                                          image=img_btd4, compound="top", fg_color="white", text_color="black",
                                          hover_color="lightgray",
                                          font=ctk.CTkFont(size=20, weight="bold"))
    btd4_button.grid(column=3, row=1, padx=20, pady=20)


def open_link(url):
    webbrowser.open(url)

