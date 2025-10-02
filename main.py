from utils.gesture import Gesture
import customtkinter as ctk
import utils.HM_window as HM_window
import utils.float_spinbox as sb
import os
import subprocess
import webbrowser
import threading
import cv2
from PIL import Image
import traceback  # AI generated (threading optimization)

width = 1600
height = 900

# Default camera resolution
cam_width = 1600
cam_height = 900

app = ctk.CTk()  # MOVED BEFORE image creation
app.title("Hand Gesture Recognition Configurator")
app.geometry(f"{1600}x{900}")
app.minsize(400, 400)

title_label = ctk.CTkLabel(
    app, text="GAME HUB", text_color="black", font=ctk.CTkFont(size=60, weight="bold")
)
title_label.grid(row=0, column=0, columnspan=4, pady=20)

app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure(2, weight=1)
app.grid_columnconfigure(3, weight=1)
app.grid_columnconfigure(0, weight=1)

hm_window = HM_window

# Keep a Gesture instance if the project expects it
try:
    gestures = Gesture()
except Exception:
    gestures = None


def change_preset(preset):
    try:
        if gestures and preset:
            match preset:
                case "earth":
                    gestures.touchscreen_mode(None)
                case "particle love":
                    pass
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


"""BUTTONS"""
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
# _images = {
#     'earth': load_ctk_image_safe("earth.png", size=(200,200)),
#     'particlelove': load_ctk_image_safe("particlelove.png", size=(200,200)),
#     'paint': load_ctk_image_safe("paint.jpg", size=(200,200)),
#     'btd4': load_ctk_image_safe("btd4.jpg", size=(200,200)),
#     'chess': load_ctk_image_safe("chess.png", size=(200,200)),
#     'ssp': load_ctk_image_safe("ssp.png", size=(200,200)),
# }
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
            app,
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
            app,
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
    lambda: open_url(
        "https://earth.google.com/web/", preset="earth"
    ),
    "earth",
)

particle_love_button = make_button(
    1,
    1,
    "Particle Love Javascript Demo",
    lambda: open_url(
        "https://particle-love.com/", preset="particle love"
    ),
    "particlelove",
)

paint_button = make_button(
    2,
    1,
    "Paint",
    lambda: open_url(
        "https://sketch.io/sketchpad/", preset="paint"
    ),
    "paint",
)

btd4_button = make_button(
    3,
    1,
    "bloons tower deffense 4",
    lambda: open_url(
        "https://www.crazygames.com/game/bloons-tower-defense-4", preset="btd4"
    ),
    "btd4",
)

chess_button = make_button(
    0,
    2,
    "Play Chess",
    lambda: open_url(
        "https://plainchess.timwoelfle.de/", preset="chess"
    ),
    "chess",
)

ssp_button = make_button(
    1,
    2,
    "Sound Space+",
    lambda: open_program("ssp", "SoundSpacePlus.exe", preset="ssp"),
    "ssp",
)


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
        thread = threading.Thread(
            target=threaded_hm_window_runner, args=(HM_width, HM_height), daemon=True
        )
        thread.start()
        print("started Hand Movement Window")
    except Exception as e:
        print(f"Error in HM_window thread: {e}")


app.after(100, lambda: start_HM_window(cam_width, cam_height))

app.geometry(f"{width}x{height}")
app.mainloop()
