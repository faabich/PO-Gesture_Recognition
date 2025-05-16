import ctypes
import ctypes.wintypes
import _thread as thread
import time
import threading

# Touch input constants
TOUCH_MASK_NONE = 0x00000000
TOUCH_MASK_CONTACTAREA = 0x00000001
TOUCH_MASK_ORIENTATION = 0x00000002
TOUCH_MASK_PRESSURE = 0x00000004
TOUCH_MASK_ALL = 0x00000007

TOUCH_FLAG_NONE = 0x00000000

PT_POINTER = 0x00000001
PT_TOUCH = 0x00000002
PT_PEN = 0x00000003
PT_MOUSE = 0x00000004

POINTER_FLAG_NONE = 0x00000000
POINTER_FLAG_NEW = 0x00000001
POINTER_FLAG_INRANGE = 0x00000002
POINTER_FLAG_INCONTACT = 0x00000004
POINTER_FLAG_FIRSTBUTTON = 0x00000010
POINTER_FLAG_SECONDBUTTON = 0x00000020
POINTER_FLAG_THIRDBUTTON = 0x00000040
POINTER_FLAG_FOURTHBUTTON = 0x00000080
POINTER_FLAG_FIFTHBUTTON = 0x00000100
POINTER_FLAG_PRIMARY = 0x00002000
POINTER_FLAG_CONFIDENCE = 0x00004000
POINTER_FLAG_CANCELED = 0x00008000
POINTER_FLAG_DOWN = 0x00010000
POINTER_FLAG_UPDATE = 0x00020000
POINTER_FLAG_UP = 0x00040000
POINTER_FLAG_WHEEL = 0x00080000
POINTER_FLAG_HWHEEL = 0x00100000
POINTER_FLAG_CAPTURECHANGED = 0x00200000


class POINTER_INFO(ctypes.Structure):
    _fields_ = [("pointerType", ctypes.c_uint32),
                ("pointerId", ctypes.c_uint32),
                ("frameId", ctypes.c_uint32),
                ("pointerFlags", ctypes.c_int),
                ("sourceDevice", ctypes.wintypes.HANDLE),
                ("hwndTarget", ctypes.wintypes.HWND),
                ("ptPixelLocation", ctypes.wintypes.POINT),
                ("ptHimetricLocation", ctypes.wintypes.POINT),
                ("ptPixelLocationRaw", ctypes.wintypes.POINT),
                ("ptHimetricLocationRaw", ctypes.wintypes.POINT),
                ("dwTime", ctypes.c_ulong),
                ("historyCount", ctypes.c_uint32),
                ("inputData", ctypes.c_int32),
                ("dwKeyStates", ctypes.c_ulong),
                ("PerformanceCount", ctypes.c_uint64),
                ("ButtonChangeType", ctypes.c_int)
                ]


class POINTER_TOUCH_INFO(ctypes.Structure):
    _fields_ = [("pointerInfo", POINTER_INFO),
                ("touchFlags", ctypes.c_int),
                ("touchMask", ctypes.c_int),
                ("rcContact", ctypes.wintypes.RECT),
                ("rcContactRaw", ctypes.wintypes.RECT),
                ("orientation", ctypes.c_uint32),
                ("pressure", ctypes.c_uint32)]


# Initialize Pointer and Touch info for two fingers
touchInfoArray = (POINTER_TOUCH_INFO * 2)()

# Use a better lock mechanism
touchInfoLock = threading.RLock()

# Track if each finger is currently in contact
finger_in_contact = [False, False]

# Track hold threads for proper cleanup
hold_threads = [None, None]
hold_thread_exit_flags = [False, False]


def initialize_touch():
    """Initialize touch injection, returns True on success, False on failure"""
    try:
        if (ctypes.windll.user32.InitializeTouchInjection(2, 1) != 0):
            print("Touch injection initialized successfully with 2 touch points")
            # Initialize the touch info structures
            for i in range(2):
                touchInfoArray[i].pointerInfo = POINTER_INFO(
                    pointerType=PT_TOUCH,
                    pointerId=i,
                    ptPixelLocation=ctypes.wintypes.POINT(0, 0)
                )
                touchInfoArray[i].touchFlags = TOUCH_FLAG_NONE
                touchInfoArray[i].touchMask = TOUCH_MASK_ALL
                touchInfoArray[i].rcContact = ctypes.wintypes.RECT(0, 0, 0, 0)
                touchInfoArray[i].orientation = 90
                touchInfoArray[i].pressure = 32000
            return True
        else:
            print("Touch injection initialization failed")
            return False
    except Exception as e:
        print(f"Error initializing touch injection: {e}")
        return False


# Global variable to track initialization state
_g_touchInjenctionInitialized = False


def setTouchCoords(x, y, fingerRadius=5, finger=0):
    """Set coordinates for a specific finger"""
    if finger < 0 or finger > 1:
        raise ValueError(f"Invalid finger number: {finger}, expected 0 or 1")

    with touchInfoLock:
        ti = touchInfoArray[finger]
        ti.pointerInfo.ptPixelLocation.x = x
        ti.pointerInfo.ptPixelLocation.y = y

        ti.rcContact.left = x - fingerRadius
        ti.rcContact.right = x + fingerRadius
        ti.rcContact.top = y - fingerRadius
        ti.rcContact.bottom = y + fingerRadius


def _sendTouch(pointerFlags, finger, errorWhen="doTouch"):
    """
    Send touch event for a specific finger
    """
    if finger < 0 or finger > 1:
        raise ValueError(f"Invalid finger number: {finger}, expected 0 or 1")

    with touchInfoLock:
        # Set the flags for the finger
        touchInfoArray[finger].pointerInfo.pointerFlags = pointerFlags

        try:
            # Send just this finger's touch info
            success = ctypes.windll.user32.InjectTouchInput(1, ctypes.byref(touchInfoArray[finger]))
        except AttributeError:
            raise NotImplementedError("This Windows version does not support touch injection")

        if success == 0:
            err = ctypes.GetLastError()
            print(f"Touch injection failed during {errorWhen}: {err}")
            return False
        return True


def _touchHold(finger):
    """Thread function to keep a touch point active"""
    thread_id = thread.get_ident()
    print(f"Hold thread started for finger {finger}, thread ID: {thread_id}")

    update_interval = 0.25  # seconds

    while not hold_thread_exit_flags[finger]:
        # Check if the finger is still in contact
        with touchInfoLock:
            if not finger_in_contact[finger]:
                break

            # Send update to keep the touch active
            flags = POINTER_FLAG_UPDATE | POINTER_FLAG_INRANGE | POINTER_FLAG_INCONTACT
            success = _sendTouch(flags, finger, "_touchHold")

            if not success:
                break

        # Sleep outside the lock to avoid holding it
        time.sleep(update_interval)

    print(f"Hold thread exiting for finger {finger}, thread ID: {thread_id}")
    hold_threads[finger] = None


def touchDown(x, y, fingerRadius=5, holdEvents=True, finger=0):
    """Send a touch down event"""
    with touchInfoLock:
        # If there's an existing hold thread for this finger, stop it
        if hold_threads[finger] is not None:
            hold_thread_exit_flags[finger] = True
            # Don't join - just let it exit on its own

        # Reset the exit flag for a new thread
        hold_thread_exit_flags[finger] = False

        # Set coordinates and do the touch down
        setTouchCoords(x, y, fingerRadius, finger)
        ok = _sendTouch(POINTER_FLAG_DOWN | POINTER_FLAG_INRANGE | POINTER_FLAG_INCONTACT,
                        finger, "touchDown")

        if not ok:
            return False

        # Mark this finger as in contact
        finger_in_contact[finger] = True

        # Start a hold thread if requested
        if holdEvents:
            hold_threads[finger] = thread.start_new_thread(_touchHold, (finger,))

        return True


def touchMove(x, y, fingerRadius=5, finger=0):
    """Send a touch move event"""
    with touchInfoLock:
        # Check if this finger is in contact
        if not finger_in_contact[finger]:
            return False

        setTouchCoords(x, y, fingerRadius, finger)
        return _sendTouch(POINTER_FLAG_UPDATE | POINTER_FLAG_INRANGE | POINTER_FLAG_INCONTACT,
                          finger, "touchMove")


def touchUp(x, y, fingerRadius=5, finger=0):
    """Send a touch up event"""
    with touchInfoLock:
        # Signal the hold thread to exit if it exists
        if hold_threads[finger] is not None:
            hold_thread_exit_flags[finger] = True
            # Don't join - just let it exit on its own
            hold_threads[finger] = None

        # Even if not in contact, try to send a touchUp
        # This ensures we don't get stuck touches
        setTouchCoords(x, y, fingerRadius, finger)

        # First send update to move to final position
        moveOk = _sendTouch(POINTER_FLAG_UPDATE | POINTER_FLAG_INRANGE | POINTER_FLAG_INCONTACT,
                            finger, "touchUp move to final location")

        # Then send up to release the touch
        upOk = _sendTouch(POINTER_FLAG_UP, finger, "touchUp")

        # Mark this finger as no longer in contact
        finger_in_contact[finger] = False

        return moveOk and upOk


def touchPinch(finger0startXY, finger0endXY, finger1startXY, finger1endXY, count=10, duration=0.75):
    """Perform a pinch gesture with both fingers"""
    # Extract coordinates
    f0x, f0y = finger0startXY
    f1x, f1y = finger1startXY

    # Calculate delta movements
    f0dx = float(finger0endXY[0] - finger0startXY[0]) / count
    f0dy = float(finger0endXY[1] - finger0startXY[1]) / count
    f1dx = float(finger1endXY[0] - finger1startXY[0]) / count
    f1dy = float(finger1endXY[1] - finger1startXY[1]) / count

    # Calculate delay between steps
    delay = float(duration) / count

    # Send touch down events for both fingers (without hold threads)
    touchDown(f0x, f0y, finger=0, holdEvents=False)
    touchDown(f1x, f1y, finger=1, holdEvents=False)

    # Move fingers in steps
    for i in range(count):
        time.sleep(delay)
        f0x += f0dx
        f0y += f0dy
        f1x += f1dx
        f1y += f1dy
        touchMove(int(f0x), int(f0y), finger=0)
        touchMove(int(f1x), int(f1y), finger=1)

    # Final delay and touch up
    time.sleep(delay)
    touchUp(int(finger0endXY[0]), int(finger0endXY[1]), finger=0)
    touchUp(int(finger1endXY[0]), int(finger1endXY[1]), finger=1)

    return True


# Helper functions for backward compatibility
def sendTouchDown(x, y):
    return touchDown(x, y)


def sendTouchUp(x, y):
    return touchUp(x, y)


def sendTouchMove(x, y):
    return touchMove(x, y)


def sendTap(x, y):
    touchDown(x, y)
    time.sleep(0.1)
    touchUp(x, y)
    return True


# Initialize touch injection on module import
_g_touchInjenctionInitialized = initialize_touch()