import threading
import customtkinter as ctk
from utils.HM_window import HM_window

hm_lock = threading.Lock()
hm_window = None
hm_thread = None

def update_status_label(app, message):
    status_label = ctk.CTkLabel(app, text=message)
    status_label.grid(row=6, column=1, padx=10, pady=10)
    app.after(5000, status_label.destroy)

def stop_hm_window(app=None):
    global hm_window, hm_thread
    with hm_lock:
        print("Entering stop_hm_window")
        if hm_window is not None:
            print("hm_window is not None - proceeding to stop")
            try:
                hm_window.stop()
                if hm_thread is not None and hm_thread.is_alive():
                    print("Waiting for thread to join...")
                    hm_thread.join(timeout=5.0)
                    if hm_thread.is_alive():
                        print("Warning: Thread did not terminate within timeout")
                if app and hm_window.label:
                    app.after(0, lambda: hm_window.label.destroy())
                hm_window = None
                hm_thread = None
                print("Camera thread stopped")
                if app:
                    app.after(0, lambda: update_status_label(app, "Camera thread stopped"))
            except Exception as e:
                print(f"Error stopping HM_window: {e}")
                if app:
                    app.after(0, lambda: update_status_label(app, f"Error stopping camera: {e}"))
        else:
            print("hm_window is None - no action needed")
            if app:
                app.after(0, lambda: update_status_label(app, "No camera thread running"))

def start_HM_window(app, width, height, mode=None, num_hands=1, canvas=None):
    global hm_window, hm_thread
    with hm_lock:
        try:
            stop_hm_window(app)
            video_label = ctk.CTkLabel(app, text="")
            video_label.grid(row=5, column=0, columnspan=3, padx=10, pady=10)
            hm_window = HM_window(width, height, mode, app=app, num_hands=num_hands, canvas=canvas)
            hm_window.set_video_label(video_label)
            hm_thread = threading.Thread(target=hm_window.run, daemon=True)
            hm_thread.start()
            app.after(0, lambda: update_status_label(app, f"Camera thread started ({mode})"))
            return hm_thread
        except Exception as e:
            print(f"Error starting HM_window: {e}")
            app.after(0, lambda: update_status_label(app, f"Error: {e}"))