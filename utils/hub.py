"""
Name:         hub.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         27.10.2025
Version:      0.1
Description:  The tkinter hub with buttons to launch games or open urls
"""

import os
import customtkinter as ctk
from PIL import Image, ImageTk
from utils.camera import VideoCamera
from utils.gesture import Gesture
import ctypes
import subprocess
import webbrowser
import time
import threading
import queue


class Hub(ctk.CTk):
    def __init__(self, width, height):
        super().__init__()
        self.name = "Hub"
        self.width = width
        self.height = height
        self.canvas = None
        self.preset = None
        self.landmarks = None

        # Objects
        self.camera = VideoCamera(self)
        self.gestures = Gesture(self, self.camera)

        # Configuration ctypes pour Windows
        self.user32 = ctypes.windll.user32
        self.SCREEN_WIDTH = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN constant
        self.SCREEN_HEIGHT = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN constant

        # Hub parameters
        self.title("Hand Gesture Recognition Configurator")
        self.geometry(f"{self.width}x{self.height}")
        self.minsize(400, 400)

        self.title_label = ctk.CTkLabel(self, text="GAME HUB", text_color="black", font=ctk.CTkFont(size=60, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=4, pady=20)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Thread-safe queue for frame processing
        self.frame_queue = queue.Queue(maxsize=1)
        self.stop_event = threading.Event()

        self.initialize()
        self.update_gesture()

    def initialize(self):
        # Wait for camera to be ready
        while not self.camera.success:
            print("waiting for camera...")
            time.sleep(0.5)

        # BUTTONS
        # Resolve img folder relative to THIS file's project root (main.py is at project root)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        img_folder = os.path.join(root_dir, "img")

        # safe loader: returns a valid CTkImage or None
        def load_ctk_image_safe(name, size=(200, 200)):
            path = os.path.join(img_folder, name)
            if not os.path.exists(path):
                return None
            try:
                pil_img = Image.open(path).convert("RGBA").copy()
                return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
            except Exception:
                return None

        # Create images AFTER app is created and keep references in a dict so they are not GC'd (KEPT REF)
        _images = {
            'earth': load_ctk_image_safe("earth.png", size=(200,200)),
            'particlelove': load_ctk_image_safe("particlelove.png", size=(200,200)),
            'paint': load_ctk_image_safe("paint.jpg", size=(200,200)),
            'btd4': load_ctk_image_safe("btd4.jpg", size=(200,200)),
            'chess': load_ctk_image_safe("chess.png", size=(200,200)),
            'ssp': load_ctk_image_safe("ssp.png", size=(200,200)),
        }
        _images = {
            "earth": None,
            "particlelove": None,
            "paint": None,
            "btd4": None,
            "chess": None,
            "ssp": None,
        }

        def make_button(col, row, text, cmd, img_key):
            img = _images.get(img_key)
            if img is not None:
                btn = ctk.CTkButton(
                    self,
                    text=text,
                    command=cmd,
                    image=img,
                    compound="top",
                    fg_color="white",
                    text_color="black",
                    hover_color="lightgray",
                    font=ctk.CTkFont(size=20, weight="bold"),
                )
                btn._image_ref = img  # keep reference
            else:
                btn = ctk.CTkButton(
                    self,
                    text=text,
                    command=cmd,
                    fg_color="white",
                    text_color="black",
                    hover_color="lightgray",
                    font=ctk.CTkFont(size=20, weight="bold"),
                )
            btn.grid(column=col, row=row, padx=20, pady=20)
            return btn

        earth_button = make_button(
            0,
            1,
            "Google Earth",
            lambda: self.open_url(
                "https://earth.google.com/web/", preset="earth"
            ),
            "earth",
        )

        particle_love_button = make_button(
            1,
            1,
            "Particle Love Javascript Demo",
            lambda: self.open_url(
                "https://particle-love.com/", preset="particle love"
            ),
            "particlelove",
        )

        paint_button = make_button(
            2,
            1,
            "Paint",
            lambda: self.open_url(
                "https://sketch.io/sketchpad/", preset="paint"
            ),
            "paint",
        )

        btd4_button = make_button(
            3,
            1,
            "bloons tower deffense 4",
            lambda: self.open_url(
                "https://www.crazygames.com/game/bloons-tower-defense-4", preset="btd4"
            ),
            "btd4",
        )

        chess_button = make_button(
            0,
            2,
            "Play Chess",
            lambda: self.open_url(
                "https://plainchess.timwoelfle.de/", preset="chess"
            ),
            "chess",
        )

        ssp_button = make_button(
            1,
            2,
            "Sound Space+",
            lambda: self.open_program("ssp", "SoundSpacePlus.exe", preset="ssp"),
            "ssp",
        )

    def load_images(self):
        folder_dir = "img/"
        for images in os.listdir(folder_dir):
            img_pil = Image.open(images)
            img_tk_ref = ImageTk.PhotoImage(img_pil.resize((64, 64)))
            self.canvas._img_tk_ref = img_tk_ref  # Persistent reference

            # Create the canvas item
            image_item_id = self.canvas.create_image(0, 0, image=img_tk_ref, anchor="center" )
            self.gestures.images[images] = image_item_id

            # Final reference confirmation
            self.canvas.itemconfig(image_item_id, image=img_tk_ref)

    def update_gesture(self):
        if self.camera.success:
            self.landmarks = self.camera.get_landmarks()

            if self.landmarks is not None:
                match self.preset:
                    case "earth":
                        self.gestures.touchscreen_mode(self.landmarks)
                    case "particle love":
                        self.gestures.mouse_mode(self.landmarks)

        self.after(5, self.update_gesture)      # Continuously update gestures

    def open_program(self, folder, program_name, preset=None):
        try:
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            exe_path = os.path.join(parent_dir, "games", folder, program_name)
            if os.path.exists(exe_path):
                subprocess.Popen([exe_path], shell=False)
            else:
                print(f"Executable not found: {exe_path}")
        except Exception as e:
            print("open_program error:", e)

        self.preset = preset


    def open_url(self, url, preset=None):
        try:
            webbrowser.open(url)
            self.preset = preset
        except Exception as e:
            print("open_url error:", e)
