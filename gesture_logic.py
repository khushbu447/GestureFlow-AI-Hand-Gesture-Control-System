
import ctypes
import math
import pyautogui
from tkinter import messagebox


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def detect_gesture(landmarks):
    lm = landmarks

    thumb_tip = lm[4]
    thumb_ip = lm[3]
    thumb_mcp = lm[2]

    index_open = lm[8].y < lm[6].y
    middle_open = lm[12].y < lm[10].y
    ring_open = lm[16].y < lm[14].y
    pinky_open = lm[20].y < lm[18].y

    count = sum([
        index_open, middle_open, ring_open, pinky_open
    ])

    thumb_extended = (
        distance(thumb_tip, lm[5])
        > distance(thumb_mcp, lm[5]) + 0.04
    )

    thumb_up = (
        thumb_tip.y < thumb_ip.y
        and thumb_tip.y < thumb_mcp.y
    )

    pinch = distance(thumb_tip, lm[8]) < 0.055

    # OK SIGN
    if pinch and middle_open and ring_open and pinky_open:
        return "OK SIGN"

    # FOUR FINGERS - Sleep Mode
    if count == 4 and not thumb_extended:
        return "FOUR FINGERS"

    # THUMBS UP
    if count == 0 and thumb_up and thumb_extended:
        return "THUMBS UP"

    # FIST
    if count == 0 and not thumb_extended:
        return "FIST"

    # ROCK SIGN
    if index_open and not middle_open and not ring_open and pinky_open:
        return "ROCK SIGN"

    # ONE FINGER
    if index_open and not middle_open and not ring_open and not pinky_open:
        return "ONE FINGER"

    # TWO FINGERS
    if index_open and middle_open and not ring_open and not pinky_open:
        return "TWO FINGERS"

    # THREE FINGERS
    if index_open and middle_open and ring_open and not pinky_open:
        return "THREE FINGERS"

    return "NO GESTURE"


def sleep_action():
    answer = messagebox.askyesno(
        "GestureFlow - Sleep Mode",
        "FOUR FINGERS detected!\n\n"
        "Do you want to put your computer to sleep?"
    )

    if not answer:
        return "Sleep Cancelled"

    try:
        result = ctypes.windll.powrprof.SetSuspendState(
            False, False, False
        )

        if result:
            return "Sleep Mode"

        messagebox.showwarning(
            "Sleep Mode",
            "Windows could not start Sleep Mode. "
            "Please check your power settings."
        )
        return "Sleep Failed"

    except Exception as error:
        messagebox.showerror("Sleep Error", str(error))
        return "Sleep Failed"


def perform_action(gesture):

    actions = {
        "FIST": (
            "Previous",
            lambda: pyautogui.press("left")
        ),

        "THUMBS UP": (
            "Next",
            lambda: pyautogui.press("right")
        ),

        "ONE FINGER": (
            "Volume Up",
            lambda: pyautogui.press("volumeup")
        ),

        "TWO FINGERS": (
            "Play / Pause",
            lambda: pyautogui.press("space")
        ),

        "THREE FINGERS": (
            "Volume Down",
            lambda: pyautogui.press("volumedown")
        ),

        "ROCK SIGN": (
            "Mute / Unmute",
            lambda: pyautogui.press("volumemute")
        ),

        "OK SIGN": (
            "Enter",
            lambda: pyautogui.press("enter")
        ),
    }

    if gesture == "FOUR FINGERS":
        return sleep_action()

    if gesture not in actions:
        return "No action"

    action_name, action_function = actions[gesture]

    action_function()

    return action_name
