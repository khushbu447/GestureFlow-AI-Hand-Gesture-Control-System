
import os
import time
import tkinter as tk
from tkinter import messagebox

import cv2
import customtkinter as ctk
import mediapipe as mp
from PIL import Image

from gesture_logic import detect_gesture, perform_action


# =========================================================
# GESTUREFLOW - AI BASED HAND GESTURE CONTROL SYSTEM
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATHS = [
    os.path.join(BASE_DIR, "model", "hand_landmarker.task"),
    os.path.join(BASE_DIR, "models", "hand_landmarker.task"),
    os.path.join(BASE_DIR, "hand_landmarker.task"),
]

MODEL_PATH = next(
    (path for path in MODEL_PATHS if os.path.isfile(path)),
    MODEL_PATHS[0]
)

# Midnight Charcoal + Emerald + Aqua theme
BG = "#06111B"
SIDEBAR = "#071923"
PANEL = "#091F2B"
CARD = "#0B2935"
CARD_ACTIVE = "#10443F"
BORDER = "#087D88"
AQUA = "#27E6E0"
MINT = "#55F5B0"
GREEN = "#45E99B"
PURPLE = "#B77BFF"
PINK = "#EF65D7"
YELLOW = "#FFD15C"
WHITE = "#EAFBFF"
MUTED = "#9BBAC9"

GESTURES = [
    ("FIST", "✊", "Previous", PINK),
    ("THUMBS UP", "👍", "Next", AQUA),
    ("ONE FINGER", "☝", "Volume Up", MINT),
    ("TWO FINGERS", "✌", "Play / Pause", PURPLE),
    ("THREE FINGERS", "3", "Volume Down", YELLOW),
    ("ROCK SIGN", "🤘", "Mute / Unmute", PINK),
    ("OK SIGN", "👌", "Enter", YELLOW),
    ("FOUR FINGERS", "🖖", "Sleep Mode", PURPLE),
]


def detect_four_fingers(landmarks):
    """Detect four raised fingers while the thumb remains folded."""
    index_open = landmarks[8].y < landmarks[6].y
    middle_open = landmarks[12].y < landmarks[10].y
    ring_open = landmarks[16].y < landmarks[14].y
    pinky_open = landmarks[20].y < landmarks[18].y

    # Thumb folded: thumb tip stays relatively close to the palm side.
    thumb_folded = abs(landmarks[4].x - landmarks[5].x) < abs(landmarks[3].x - landmarks[5].x) + 0.025

    return (
        index_open and middle_open and ring_open and pinky_open
        and thumb_folded
    )


def create_landmarker():
    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(
            "hand_landmarker.task model file nahi mili.\n\n"
            "Model ko model ya models folder mein rakho:\n"
            + MODEL_PATH
        )

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=MODEL_PATH
        ),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    return mp.tasks.vision.HandLandmarker.create_from_options(
        options
    )


class GestureFlowApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("GestureFlow | AI Hand Gesture Control")
        self.geometry("1500x920")
        self.minsize(1100, 720)
        self.configure(fg_color=BG)

        self.cap = None
        self.landmarker = None
        self.camera_running = False
        self.after_id = None
        self.camera_image = None

        self.last_gesture = "NO GESTURE"
        self.last_action_time = 0
        self.action_cooldown = 1.0

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.bind("<Escape>", lambda event: self.stop_camera())

    # -----------------------------------------------------
    # REUSABLE COMPONENTS
    # -----------------------------------------------------

    def panel(self, parent, title=None, color=PANEL):
        frame = ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=12,
            border_width=1,
            border_color=BORDER
        )

        if title:
            ctk.CTkLabel(
                frame,
                text=title,
                font=("Segoe UI", 14, "bold"),
                text_color=AQUA
            ).pack(
                anchor="w",
                padx=12,
                pady=(10, 7)
            )

        return frame

    def label(self, parent, text, size=11, color=WHITE,
              bold=False, **kwargs):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=(
                "Segoe UI",
                size,
                "bold" if bold else "normal"
            ),
            text_color=color,
            **kwargs
        )

    def button(self, parent, text, command, color=CARD):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=38,
            corner_radius=9,
            fg_color=color,
            hover_color="#087D88",
            text_color=WHITE,
            font=("Segoe UI", 11, "bold")
        )

    # -----------------------------------------------------
    # MAIN DASHBOARD
    # -----------------------------------------------------

    def build_ui(self):

        header = ctk.CTkFrame(
            self,
            fg_color=SIDEBAR,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            height=66
        )
        header.pack(fill="x", padx=12, pady=(10, 6))
        header.pack_propagate(False)

        self.label(
            header,
            "✋  GestureFlow",
            25,
            AQUA,
            True
        ).pack(side="left", padx=18)

        self.label(
            header,
            "Make your device smarter with your hands",
            12,
            MUTED
        ).pack(side="left", padx=8)

        self.top_status = self.label(
            header,
            "● CAMERA DISCONNECTED",
            11,
            MINT,
            True
        )
        self.top_status.pack(side="right", padx=18)

        # Main dashboard grid
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=12, pady=4)

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=3)
        main.grid_columnconfigure(2, weight=2)
        main.grid_columnconfigure(3, weight=1)
        main.grid_rowconfigure(0, weight=1)

        self.build_sidebar(main)
        self.build_camera_panel(main)
        self.build_gesture_panel(main)
        self.build_right_panel(main)
        self.build_bottom()

    # -----------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------

    def build_sidebar(self, parent):

        side = self.panel(parent, color=SIDEBAR)
        side.grid(
            row=0, column=0,
            sticky="nsew",
            padx=(0, 5),
            pady=3
        )

        self.label(
            side, "✋", 44, AQUA, True
        ).pack(pady=(18, 0))

        self.label(
            side, "GestureFlow", 19, MINT, True
        ).pack(pady=(2, 0))

        self.label(
            side,
            "AI Hand Gesture Control",
            10,
            MUTED,
            wraplength=155
        ).pack(pady=(0, 22))

        options = [
            ("⌂   Home", self.home_action),
            ("✋   Gestures", self.show_gestures),
            ("⚙   Settings", self.show_settings),
            ("ⓘ   About", self.show_about),
        ]

        for text, command in options:
            self.button(
                side,
                text,
                command,
                "#07554E" if "Home" in text else CARD
            ).pack(fill="x", padx=9, pady=5)

        spacer = ctk.CTkFrame(side, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        self.label(
            side,
            "Control your device\nwith simple\nhand gestures.",
            12,
            AQUA,
            justify="left"
        ).pack(anchor="w", padx=12, pady=12)

        self.label(
            side,
            "♡  Small movements.\n    Big control!",
            11,
            MINT
        ).pack(anchor="w", padx=12, pady=(8, 18))

    def home_action(self):
        pass

    def show_gestures(self):
        text = "\n".join(
            f"{i}. {name} — {action}"
            for i, (name, symbol, action, color)
            in enumerate(GESTURES, 1)
        )
        messagebox.showinfo("Supported Gestures", text)

    def show_settings(self):
        messagebox.showinfo(
            "Settings",
            "Camera: Press START CAMERA\n"
            "Stop: Press STOP CAMERA or Escape\n"
            "Gesture actions: gesture_logic.py"
        )

    def show_about(self):
        messagebox.showinfo(
            "About GestureFlow",
            "GestureFlow is an AI hand gesture control system "
            "using Python, OpenCV and MediaPipe Tasks."
        )

    # -----------------------------------------------------
    # CAMERA PANEL
    # -----------------------------------------------------

    def build_camera_panel(self, parent):

        panel = self.panel(parent, "📷  Live Camera Feed")
        panel.grid(
            row=0, column=1,
            sticky="nsew",
            padx=3, pady=3
        )

        # IMPORTANT: separate content frame avoids pack/grid conflict
        content = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )
        content.pack(
            fill="both",
            expand=True,
            padx=9,
            pady=(0, 9)
        )

        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.camera_label = ctk.CTkLabel(
            content,
            text="📷\n\nYour camera preview will appear here\n\n"
                 "Click START CAMERA below",
            font=("Segoe UI", 16),
            text_color=MUTED,
            fg_color="#061722",
            corner_radius=10
        )
        self.camera_label.grid(
            row=0, column=0,
            sticky="nsew",
            padx=1, pady=5
        )

        self.camera_status = self.label(
            content,
            "✋  Hand landmarks will appear here",
            10, AQUA
        )
        self.camera_status.grid(
            row=1, column=0,
            sticky="w",
            padx=4, pady=4
        )

        buttons = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        buttons.grid(
            row=2, column=0,
            sticky="ew",
            pady=(5, 2)
        )

        buttons.grid_columnconfigure(0, weight=1)
        buttons.grid_columnconfigure(1, weight=1)

        self.button(
            buttons,
            "▶  START CAMERA",
            self.start_camera,
            "#00BFA5"
        ).grid(
            row=0, column=0,
            sticky="ew", padx=(0, 4)
        )

        self.button(
            buttons,
            "■  STOP CAMERA",
            self.stop_camera,
            "#103047"
        ).grid(
            row=0, column=1,
            sticky="ew", padx=(4, 0)
        )

    # -----------------------------------------------------
    # GESTURE RECOGNITION PANEL
    # -----------------------------------------------------

    def build_gesture_panel(self, parent):

        middle = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        middle.grid(
            row=0, column=2,
            sticky="nsew",
            padx=3, pady=3
        )

        middle.grid_columnconfigure(0, weight=1)
        middle.grid_rowconfigure(1, weight=1)

        detected = self.panel(
            middle,
            "✋  Detected Gesture"
        )
        detected.grid(
            row=0, column=0,
            sticky="ew",
            pady=(0, 6)
        )

        self.detected_icon = self.label(
            detected, "✋", 34, AQUA
        )
        self.detected_icon.pack(pady=(5, 0))

        self.detected_name = self.label(
            detected, "NO GESTURE", 20, MINT, True
        )
        self.detected_name.pack(pady=(2, 0))

        self.detected_subtitle = self.label(
            detected,
            "(Hand not detected)",
            11, MUTED
        )
        self.detected_subtitle.pack(pady=(0, 5))

        ctk.CTkFrame(
            detected,
            height=1,
            fg_color=BORDER
        ).pack(fill="x", padx=12, pady=5)

        self.action_name = self.label(
            detected,
            "Action Performed\nWaiting...",
            12, WHITE
        )
        self.action_name.pack(pady=(2, 12))

        supported = self.panel(
            middle,
            f"✥  Supported Gestures ({len(GESTURES)})"
        )
        supported.grid(
            row=1, column=0,
            sticky="nsew"
        )

        grid = ctk.CTkFrame(
            supported,
            fg_color="transparent"
        )
        grid.pack(
            fill="both",
            expand=True,
            padx=6, pady=(0, 7)
        )

        for col in range(5):
            grid.grid_columnconfigure(
                col, weight=1, uniform="gestures"
            )

        for row in range(2):
            grid.grid_rowconfigure(
                row, weight=1, uniform="gestures"
            )

        self.gesture_tiles = {}

        for i, (name, symbol, action, color) in enumerate(GESTURES):

            tile = ctk.CTkFrame(
                grid,
                fg_color=CARD,
                corner_radius=9,
                border_width=1,
                border_color=BORDER
            )
            tile.grid(
                row=i // 5,
                column=i % 5,
                sticky="nsew",
                padx=2, pady=3
            )

            self.label(
                tile, symbol, 24, color, True
            ).pack(pady=(5, 0))

            self.label(
                tile, name.title(), 9, WHITE, True,
                wraplength=78
            ).pack(pady=(2, 0))

            self.label(
                tile, action, 8, MUTED,
                wraplength=78
            ).pack(pady=(1, 5))

            self.gesture_tiles[name] = tile

    # -----------------------------------------------------
    # QUICK CONTROLS AND STATUS
    # -----------------------------------------------------

    def build_right_panel(self, parent):

        right = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        right.grid(
            row=0, column=3,
            sticky="nsew",
            padx=(3, 0), pady=3
        )
        right.grid_columnconfigure(0, weight=1)

        quick = self.panel(right, "⚡  Quick Controls")
        quick.grid(
            row=0, column=0,
            sticky="ew",
            pady=(0, 6)
        )

        self.quick_gesture = self.label(
            quick, "Gesture: —", 11, AQUA
        )
        self.quick_gesture.pack(
            anchor="w", padx=10, pady=(4, 2)
        )

        self.quick_action = self.label(
            quick, "Action: Waiting", 11, WHITE
        )
        self.quick_action.pack(
            anchor="w", padx=10, pady=(2, 10)
        )

        status = self.panel(right, "⚙  System Status")
        status.grid(
            row=1, column=0,
            sticky="ew",
            pady=(0, 6)
        )

        self.system_ready = self.label(
            status, "● System Ready", 12, MINT, True
        )
        self.system_ready.pack(
            anchor="w", padx=10, pady=(3, 7)
        )

        ctk.CTkFrame(
            status,
            height=1,
            fg_color=BORDER
        ).pack(fill="x", padx=9)

        self.status_camera = self.label(
            status, "Camera: Disconnected", 10, MUTED
        )
        self.status_camera.pack(
            anchor="w", padx=10, pady=5
        )

        self.status_model = self.label(
            status, "Model: Not loaded", 10, MUTED
        )
        self.status_model.pack(
            anchor="w", padx=10, pady=5
        )

        self.status_hands = self.label(
            status, "Hands: 0 detected", 10, MUTED
        )
        self.status_hands.pack(
            anchor="w", padx=10, pady=(5, 10)
        )

        quote = self.panel(
            right, color="#071A27"
        )
        quote.grid(
            row=2, column=0,
            sticky="nsew"
        )

        self.label(
            quote,
            "“Small movements.\nBig control.”",
            15, AQUA
        ).pack(expand=True, padx=8, pady=20)

    # -----------------------------------------------------
    # BOTTOM INFORMATION CARDS
    # -----------------------------------------------------

    def build_bottom(self):

        bottom = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        bottom.pack(
            fill="x",
            padx=12,
            pady=(4, 10)
        )
        for col, weight in enumerate([1, 2, 1, 2]):
            bottom.grid_columnconfigure(
                col, weight=weight, uniform="bottom"
                )

        cards = [
            (
                "📁  Project Structure",
                "AI_Hand_Gesture_Control/\n"
                "  model/\n"
                "    hand_landmarker.task\n"
                "  main.py\n"
                "  gesture_logic.py\n"
                "  requirements.txt"
            ),
            (
                "ⓘ  About GestureFlow",
                "AI-powered hand gesture control.\n\n"
                "Python • MediaPipe Tasks\n"
                "OpenCV • CustomTkinter\n\n"
                "Control your computer using\n"
                "camera-based hand gestures."
            ),
            (
                "✦  Key Features",
                "✓ Live camera preview\n"
                "✓ Hand landmark tracking\n"
                f"✓ {len(GESTURES)} gesture tiles\n"
                "✓ Start / Stop camera\n"
                "✓ Gesture action mapping"
            ),
            (
                "▶  How to Run",
                "1. Open project in VS Code\n"
                "2. Activate your venv\n"
                "3. Check the model file\n"
                "4. Run: python main.py\n"
                "5. Click START CAMERA\n"
                "6. Allow camera permission"
            ),
        ]

        for col, (title, body) in enumerate(cards):
            card = self.panel(bottom, title)
            card.grid(
                row=0, column=col,
                sticky="nsew",
                padx=3, pady=2
            )

            self.label(
                card,
                body,
                10,
                "#C2DCE8",
                justify="left",
                anchor="nw"
            ).pack(
                fill="both",
                expand=True,
                padx=10, pady=(0, 12)
            )

    # -----------------------------------------------------
    # CAMERA START
    # -----------------------------------------------------

    def start_camera(self):

        if self.camera_running:
            return

        try:
            if self.landmarker is None:
                self.landmarker = create_landmarker()

            self.status_model.configure(
                text="Model: Loaded",
                text_color=GREEN
            )

            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

            if not self.cap.isOpened():
                self.cap.release()
                self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                raise RuntimeError(
                    "Camera open nahi hua.\n\n"
                    "Check karo ki camera kisi aur app mein "
                    "use nahi ho raha aur Windows camera "
                    "permission enabled hai."
                )

            self.camera_running = True

            self.top_status.configure(
                text="● CAMERA CONNECTED",
                text_color=MINT
            )
            self.camera_status.configure(
                text="● Camera active — hand tracking running",
                text_color=MINT
            )
            self.status_camera.configure(
                text="Camera: Connected",
                text_color=MINT
            )
            self.system_ready.configure(
                text="● System Running",
                text_color=MINT
            )

            self.update_camera()

        except Exception as error:
            self.stop_camera()
            messagebox.showerror(
                "GestureFlow Error",
                str(error)
            )

    # -----------------------------------------------------
    # CAMERA LOOP + MEDIAPIPE TASKS API
    # -----------------------------------------------------

    def update_camera(self):

        if not self.camera_running or self.cap is None:
            return

        success, frame = self.cap.read()

        if not success:
            self.after_id = self.after(
                60, self.update_camera
            )
            return

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(
            frame, cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = self.landmarker.detect(mp_image)

        gesture = "NO GESTURE"
        hand_count = 0

        if result.hand_landmarks:

            hand_count = len(result.hand_landmarks)
            landmarks = result.hand_landmarks[0]

            height, width = frame.shape[:2]

            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),
                (0, 5), (5, 6), (6, 7), (7, 8),
                (5, 9), (9, 10), (10, 11), (11, 12),
                (9, 13), (13, 14), (14, 15), (15, 16),
                (13, 17), (17, 18), (18, 19),
                (19, 20), (0, 17)
            ]

            for start, end in connections:
                p1 = (
                    int(landmarks[start].x * width),
                    int(landmarks[start].y * height)
                )
                p2 = (
                    int(landmarks[end].x * width),
                    int(landmarks[end].y * height)
                )

                cv2.line(
                    frame, p1, p2,
                    (50, 240, 190), 2
                )

            for point in landmarks:
                x = int(point.x * width)
                y = int(point.y * height)

                cv2.circle(
                    frame,
                    (x, y),
                    4,
                    (40, 255, 220),
                    -1
                )

            try:
                # Give the dedicated four-finger pose priority over generic gestures.
                if detect_four_fingers(landmarks):
                    gesture = "FOUR FINGERS"
                else:
                    gesture = detect_gesture(landmarks)
                if not gesture:
                    gesture = "NO GESTURE"
            except Exception as error:
                self.action_name.configure(
                    text=f"Detection error\n{error}"
                )
                gesture = "NO GESTURE"

        self.status_hands.configure(
            text=f"Hands: {hand_count} detected"
        )

        # Perform action only when the recognized gesture changes
        now = time.time()

        if (
            gesture != "NO GESTURE"
            and gesture != self.last_gesture
            and now - self.last_action_time
            >= self.action_cooldown
        ):
            try:
                action = perform_action(gesture)

                if not action:
                    action = next(
                        (
                            item[2] for item in GESTURES
                            if item[0] == gesture
                        ),
                        "Action triggered"
                    )

                self.action_name.configure(
                    text=f"Action Performed\n{action}"
                )
                self.quick_gesture.configure(
                    text=f"Gesture: {gesture.title()}"
                )
                self.quick_action.configure(
                    text=f"Action: {action}"
                )

                self.last_action_time = now

            except Exception as error:
                self.action_name.configure(
                    text=f"Action error\n{error}"
                )

        self.last_gesture = gesture

        self.detected_name.configure(
            text=gesture,
            text_color=(
                MINT if gesture != "NO GESTURE"
                else MUTED
            )
        )

        self.detected_subtitle.configure(
            text=(
                "Hand recognized"
                if gesture != "NO GESTURE"
                else "(Hand not detected)"
            )
        )

        # Highlight active gesture tile
        for name, tile in self.gesture_tiles.items():

            active = name == gesture

            tile.configure(
                border_color=GREEN if active else BORDER,
                fg_color=CARD_ACTIVE if active else CARD
            )

        # Display live camera image
        rgb_frame = cv2.cvtColor(
            frame, cv2.COLOR_BGR2RGB
        )

        pil_image = Image.fromarray(rgb_frame)

        box_width = max(
            self.camera_label.winfo_width(), 320
        )
        box_height = max(
            self.camera_label.winfo_height(), 240
        )

        pil_image.thumbnail(
            (box_width, box_height)
        )

        self.camera_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=pil_image.size
        )

        self.camera_label.configure(
            image=self.camera_image,
            text=""
        )

        self.after_id = self.after(
            30, self.update_camera
        )

    # -----------------------------------------------------
    # STOP CAMERA + CLEANUP
    # -----------------------------------------------------

    def stop_camera(self):

        self.camera_running = False

        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass

            self.after_id = None

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        if hasattr(self, "camera_label"):
            self.camera_label.configure(
                image=None,
                text="📷\n\nYour camera preview will appear here\n\n"
                     "Click START CAMERA below"
            )

        self.camera_image = None
        self.last_gesture = "NO GESTURE"

        if hasattr(self, "top_status"):
            self.top_status.configure(
                text="● CAMERA DISCONNECTED",
                text_color=MINT
            )

            self.camera_status.configure(
                text="✋ Camera stopped",
                text_color=MUTED
            )

            self.status_camera.configure(
                text="Camera: Disconnected",
                text_color=MUTED
            )

            self.status_hands.configure(
                text="Hands: 0 detected"
            )

            self.system_ready.configure(
                text="● System Ready",
                text_color=MINT
            )

            self.detected_name.configure(
                text="NO GESTURE",
                text_color=MUTED
            )

            self.detected_subtitle.configure(
                text="(Hand not detected)"
            )

            self.action_name.configure(
                text="Action Performed\nWaiting..."
            )

            self.quick_gesture.configure(
                text="Gesture: —"
            )

            self.quick_action.configure(
                text="Action: Waiting"
            )

            for tile in self.gesture_tiles.values():
                tile.configure(
                    border_color=BORDER,
                    fg_color=CARD
                )

    def close_app(self):

        self.stop_camera()

        if self.landmarker is not None:
            try:
                self.landmarker.close()
            except Exception:
                pass

            self.landmarker = None

        self.destroy()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app = GestureFlowApp()
    app.mainloop()
import customtkinter as ctk
from tkinter import messagebox

BG = "#06111B"
SIDEBAR = "#071923"
PANEL = "#091F2B"
CARD = "#0B2935"
BORDER = "#087D88"
AQUA = "#27E6E0"
MINT = "#55F5B0"
WHITE = "#EAFBFF"
MUTED = "#9BBAC9"
PURPLE = "#B77BFF"


class HomeDashboard(ctk.CTk):
    def __init__(self, user_name="User"):
        super().__init__()
        self.user_name = user_name
        self.title("GestureFlow | Home")
        self.geometry("1200x760")
        self.minsize(950, 650)
        self.configure(fg_color=BG)
        self.build_home()

    def label(self, parent, text, size=14, color=WHITE, bold=False, **kwargs):
        return ctk.CTkLabel(
            parent, text=text,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            text_color=color, **kwargs
        )

    def card(self, parent, title, description, symbol, button_text, command, accent):
        frame = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=18,
                             border_width=1, border_color=BORDER)
        self.label(frame, symbol, 36, accent, True).pack(anchor="w", padx=20, pady=(20, 8))
        self.label(frame, title, 21, WHITE, True).pack(anchor="w", padx=20)
        self.label(frame, description, 13, MUTED, wraplength=280,
                   justify="left").pack(anchor="w", padx=20, pady=(8, 18))
        ctk.CTkButton(
            frame, text=button_text, command=command, height=42,
            corner_radius=10, fg_color=accent, hover_color="#087D88",
            text_color=BG, font=("Segoe UI", 12, "bold")
        ).pack(fill="x", padx=20, pady=(0, 20))
        return frame

    def build_home(self):
        header = ctk.CTkFrame(self, fg_color=SIDEBAR, corner_radius=16,
                              border_width=1, border_color=BORDER)
        header.pack(fill="x", padx=22, pady=(22, 16))
        self.label(header, "✋  GestureFlow", 26, AQUA, True).pack(
            side="left", padx=22, pady=18)
        self.label(header, "AI Hand Gesture Control System", 13, MUTED).pack(
            side="left", padx=8)
        ctk.CTkButton(header, text="About", command=self.show_about,
                      fg_color=CARD, hover_color="#087D88",
                      text_color=WHITE, width=100).pack(side="right", padx=18, pady=15)

        hero = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=20,
                            border_width=1, border_color=BORDER)
        hero.pack(fill="x", padx=22, pady=(0, 18))
        self.label(hero, f"Welcome to GestureFlow, {self.user_name} 👋",
                   28, WHITE, True).pack(anchor="w", padx=28, pady=(25, 6))
        self.label(hero, "Control your computer naturally using simple hand gestures.",
                   15, MUTED).pack(anchor="w", padx=28, pady=(0, 20))

        stats = ctk.CTkFrame(hero, fg_color="transparent")
        stats.pack(fill="x", padx=24, pady=(0, 24))
        for title, value, color in [
            ("SUPPORTED GESTURES", str(len(GESTURES)), AQUA),
            ("CONTROL MODE", "Camera-based", MINT),
            ("AI ENGINE", "MediaPipe Tasks", PURPLE),
        ]:
            box = ctk.CTkFrame(stats, fg_color=CARD, corner_radius=12)
            box.pack(side="left", fill="x", expand=True, padx=5)
            self.label(box, value, 20, color, True).pack(anchor="w", padx=15, pady=(13, 2))
            self.label(box, title, 10, MUTED, True).pack(anchor="w", padx=15, pady=(0, 13))

        self.label(self, "Explore GestureFlow", 22, WHITE, True).pack(
            anchor="w", padx=24, pady=(4, 12))
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="both", expand=True, padx=17, pady=(0, 15))
        for col in range(3):
            cards.grid_columnconfigure(col, weight=1, uniform="cards")
        cards.grid_rowconfigure(0, weight=1)

        self.card(cards, "Gesture Control",
                  "Open the live camera, recognize hand gestures and trigger computer actions.",
                  "✋", "OPEN GESTURE CONTROL", self.open_gesture_control, AQUA
                  ).grid(row=0, column=0, sticky="nsew", padx=6, pady=5)
        self.card(cards, "My Gestures",
                  "View the gestures and actions supported by the application.",
                  "✦", "VIEW GESTURES", self.show_gestures, MINT
                  ).grid(row=0, column=1, sticky="nsew", padx=6, pady=5)
        self.card(cards, "Settings",
                  "Find instructions for camera access and application controls.",
                  "⚙", "OPEN SETTINGS", self.show_settings, PURPLE
                  ).grid(row=0, column=2, sticky="nsew", padx=6, pady=5)

        self.label(self, "GESTUREFLOW  •  Python  •  OpenCV  •  MediaPipe Tasks",
                   11, MUTED).pack(pady=(0, 14))

    def open_gesture_control(self):
        try:
            from main import GestureFlowApp
            self.destroy()
            app = GestureFlowApp()
            app.mainloop()
        except Exception as exc:
            messagebox.showerror(
                "Unable to open Gesture Control",
                f"Gesture Control could not be opened.\n\n{exc}\n\n"
                "Check that main.py and gesture_logic.py are in the same folder."
            )

    
        messagebox.showinfo(
            "My Gestures",
            "Current gestures in the main.py you shared:\n\n"
            "1. Fist — Previous\n2. Thumbs Up — Next\n"
            "3. One Finger — Volume Up\n4. Two Fingers — Play / Pause\n"
            "5. Three Fingers — Volume Down\n6. Rock Sign — Mute / Unmute\n"
            "7. OK Sign — Enter\n\n"
            "8. Four Fingers - Sleep Mode"
        )

    def show_settings(self):
        messagebox.showinfo(
            "Settings",
            "1. Click Gesture Control to open the camera screen.\n"
            "2. Press START CAMERA to begin detection.\n"
            "3. Press STOP CAMERA or Escape to stop detection.\n"
            "4. Keep hand_landmarker.task in the model/models folder or project root."
        )

    def show_about(self):
        messagebox.showinfo(
            "About GestureFlow",
            "GestureFlow is an AI-based hand gesture control project built with "
            "Python, OpenCV, MediaPipe Tasks and CustomTkinter."
        )


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    HomeDashboard().mainloop()
