import threading
import customtkinter as ctk
from utils.HM_window import HM_window


hm_window = None


def update_status_label(app, message):
    status_label = ctk.CTkLabel(app, text=message)
    status_label.grid(row=6, column=1, padx=10, pady=10)
    app.after(5000, status_label.destroy)


# Manage HM_window secondary thread
def stop_hm_window():
    global hm_window
    if hm_window is not None:
        hm_window.stop()
        hm_window = None
        print("Camera thread stopped")


def start_HM_window(app, width, height, mode=None):
    global hm_window
    try:
        stop_hm_window()
        hm_window = HM_window(width, height)  # Lightweight initialization
        thread = threading.Thread(target=hm_window.run, args=(mode,), daemon=True)
        thread.start()
        app.after(0, lambda: update_status_label(f"Camera thread started ({mode})"))
    except Exception as e:
        print(f"Error starting HM_window: {e}")
        app.after(0, lambda: update_status_label(f"Error: {e}"))