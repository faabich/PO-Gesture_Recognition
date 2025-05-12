import customtkinter as ctk

def add_demo(name, img_path, technology):
    pass

def open_browser(main_frame, width, height):
    game_browser = ctk.CTkToplevel(main_frame)
    game_browser.geometry(f"{width}x{height}")
    game_browser.title("Demo browser")
    game_browser.minsize(400,400)
    game_browser.grab_set() # Focus on this window, make the main frame unclickable

"""
Name:         hub.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         01.05.2025
Version:      0.1
Description:  HUB WINDOW NAVIGATION
"""

import webbrowser
import customtkinter
from PIL import Image



def open_link(url):
    webbrowser.open(url)

"""WINDOW GLOBAL"""
app = customtkinter.CTk(fg_color='white')
app.title("HUB")
title_label = customtkinter.CTkLabel(app,text="GAME HUB", text_color="black", font=customtkinter.CTkFont(size=60, weight="bold"))
title_label.grid(row=0, column=0, columnspan=4, pady=20)

# SIZE OF THE WINDOW
width = app.winfo_screenwidth() - 15

height = app.winfo_screenheight()
app.geometry("%dx%d+0+0" % (width , height))

#GRID CONFIGURATION
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure(2, weight=1)
app.grid_columnconfigure(3, weight=1)

"""WEBSITES LINKS LIST"""
def open_earth ():
    webbrowser.open('https://earth.google.com/')

def open_google ():
    webbrowser.open('https://www.google.com/')

def open_youtube():
    webbrowser.open('https://www.youtube.com/')

def open_btd4 ():
    webbrowser.open('https://www.crazygames.com/game/bloons-tower-defense-4')


"""IMAGES LINK LIST"""

img_earth = customtkinter.CTkImage(light_image=Image.open('..\images\earth.png'),
	dark_image=Image.open('..\images\earth.png'),
	size=(200,200))

img_google = customtkinter.CTkImage(light_image=Image.open('..\images\google.jpg'),
	dark_image=Image.open('..\images\google.jpg'),
	size=(200,200))

img_youtube = customtkinter.CTkImage(light_image=Image.open('..\images\youtube.png'),
	dark_image=Image.open('..\images\youtube.png'),
	size=(200,200))

img_btd4 = customtkinter.CTkImage(light_image=Image.open(r'..\images\btd4.jpg'),
	dark_image=Image.open(r'..\images\btd4.jpg'),
	size=(200,200))

"""BUTTONS"""

earth_button = customtkinter.CTkButton(app, text="google earth", command=open_earth,
image=img_earth, compound="top", fg_color="white", text_color="black", hover_color="lightgray",
font=customtkinter.CTkFont(size=20, weight="bold"))
earth_button.grid(column = 0, row = 1, padx=20, pady=20)

google_button = customtkinter.CTkButton(app, text="google", command=open_google,
image=img_google, compound="top", fg_color="white", text_color="black", hover_color="lightgray",
font=customtkinter.CTkFont(size=20, weight="bold"))
google_button.grid(column = 1, row = 1, padx=20, pady=20)

youtube_button = customtkinter.CTkButton(app, text="youtube", command=open_youtube,
image=img_youtube,compound="top", fg_color="white", text_color="black", hover_color="lightgray",
font=customtkinter.CTkFont(size=20, weight="bold"))
youtube_button.grid(column = 2, row = 1, padx=20, pady=20)

btd4_button = customtkinter.CTkButton(app, text="bloons tower deffense 4", command=open_btd4,
image=img_btd4,compound="top", fg_color="white", text_color="black", hover_color="lightgray",
font=customtkinter.CTkFont(size=20, weight="bold"))
btd4_button.grid(column = 3, row = 1, padx=20, pady=20)


app.mainloop()

