"""
Name:         main.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         03.04.2025
Version:      0.1
Description:  Entry point for the HandGesture application
"""

import customtkinter
import utils.HM_window

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x150")

        self.button = customtkinter.CTkButton(self, text="Launch main window", command=self.start_HM_window)
        self.button.pack(padx=20, pady=20)

    def start_HM_window(self):
        new_window = HM_window.HM_window(self)

app = App()
app.mainloop()