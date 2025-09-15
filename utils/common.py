import threading
import customtkinter as ctk
from utils.HM_window import HM_window

# Protect access to these globals
hm_lock = threading.Lock()
hm_window = None
hm_thread = None

def update_status_label(app, message):
    status_label = ctk.CTkLabel(app, text=message)
    status_label.grid(row=6, column=1, padx=10, pady=10)
    app.after(5000, status_label.destroy)

def stop_hm_window(app=None, timeout=1.0):
    """
    Stop the running HM_window thread if any.
    This function avoids holding the global lock while waiting for the thread to terminate,
    preventing deadlocks / UI freeze.
    """
    global hm_window, hm_thread

    # Grab references under lock, then operate on them outside the lock
    with hm_lock:
        local_window = hm_window
        local_thread = hm_thread
        # set globals to None immediately so other callers see 'stopped' state
        hm_window = None
        hm_thread = None

    if local_window is None:
        # No camera running
        if app:
            app.after(0, lambda: update_status_label(app, "No camera thread running"))
        return

    try:
        print("Stopping HM_window...")
        local_window.stop()  # signal thread to stop (non-blocking)
    except Exception as e:
        print(f"Exception when signaling stop: {e}")

    # Wait a short time for thread to finish, but DON'T block UI thread for long
    if local_thread is not None:
        local_thread.join(timeout=timeout)
        if local_thread.is_alive():
            # thread didn't stop quickly — warn but don't keep blocking
            print("Warning: camera thread did not terminate within timeout")
            if app:
                app.after(0, lambda: update_status_label(app, "Warning: camera thread did not stop quickly"))
        else:
            print("Camera thread joined successfully")

    # Cleanup UI label if still present — schedule on main thread
    try:
        if app and getattr(local_window, "label", None):
            app.after(0, lambda: local_window.label.destroy())
    except Exception as e:
        print(f"Exception cleaning up label: {e}")

    if app:
        app.after(0, lambda: update_status_label(app, "Camera thread stopped"))

def start_HM_window(app, width, height, mode=None, num_hands=1, canvas=None):
    """
    Start the HM_window in a background thread. This function will:
    - call stop_hm_window() to stop any running instance (stop is non-blocking)
    - create the HM_window and start a new thread
    """
    global hm_window, hm_thread

    # First, request a stop of any running instance (this does not hold hm_lock)
    stop_hm_window(app)

    # Now create + start, under the lock so globals are consistent
    with hm_lock:
        try:
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
            # if something failed, ensure globals are cleared
            hm_window = None
            hm_thread = None
            return None