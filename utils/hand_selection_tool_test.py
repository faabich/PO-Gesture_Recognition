import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
from pathlib import Path

class HandSelectionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Hand Point Selection")
        self.geometry("400x400")

        self.hand_image = Image.open(Path(__file__).parent.parent / "img" / "hand.png") # IA: how to load an image from a path
        self.hand_photo = ImageTk.PhotoImage(self.hand_image)

        self.canvas = ctk.CTkCanvas(self, width=self.hand_image.width, height=self.hand_image.height)
        self.canvas.pack()

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.hand_photo)

        self.points = [
            (50, 50), (100, 100), (150, 150), (200, 200), (250, 250)
        ]  # Example points on the hand

        self.selected_points = []

        for point in self.points:
            self.canvas.create_oval(point[0]-5, point[1]-5, point[0]+5, point[1]+5, fill="red", tags="point")
            self.canvas.tag_bind("point", "<Button-1>", self.on_point_click)

        self.show_popup_button = ctk.CTkButton(self, text="Show Popup", command=self.show_popup)
        self.show_popup_button.pack(pady=20)

    def on_point_click(self, event):
        point = (event.x, event.y)
        if point in self.points:
            if point not in self.selected_points:
                self.selected_points.append(point)
                self.canvas.create_oval(point[0]-5, point[1]-5, point[0]+5, point[1]+5, fill="green", tags="selected_point")
            else:
                self.selected_points.remove(point)
                self.canvas.create_oval(point[0]-5, point[1]-5, point[0]+5, point[1]+5, fill="red", tags="point")

    def show_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Selected Points")
        popup.geometry("200x200")

        label = ctk.CTkLabel(popup, text="Selected Points:")
        label.pack(pady=10)

        for point in self.selected_points:
            point_label = ctk.CTkLabel(popup, text=f"({point[0]}, {point[1]})")
            point_label.pack()

if __name__ == "__main__":
    app = HandSelectionApp()
    app.mainloop()
