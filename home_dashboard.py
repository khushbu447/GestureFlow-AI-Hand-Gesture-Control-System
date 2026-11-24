
import customtkinter as ctk
from tkinter import messagebox


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

BG = "#111827"
PANEL = "#1B2636"
PANEL_LIGHT = "#243447"
EMERALD = "#35BFA0"
AQUA = "#8BE9D4"
WHITE = "#F4F7FA"
MUTED = "#9AA9BA"


class HomeDashboard(ctk.CTk):
    def __init__(self, user_name="User"):
        super().__init__()

        self.user_name = user_name
        self.title("GestureFlow | Home Dashboard")
        self.geometry("1200x780")
        self.minsize(1000, 680)
        self.configure(fg_color=BG)

        self.build_ui()

    def build_ui(self):
        # Main layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(
            self, width=225, corner_radius=0, fg_color=PANEL
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="✋ GestureFlow",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=AQUA
        ).pack(pady=(32, 5), padx=18)

        ctk.CTkLabel(
            sidebar, text="AI HAND CONTROL",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=MUTED
        ).pack(pady=(0, 35))

        self.nav_button(sidebar, "⌂   Home", self.show_home, active=True)
        self.nav_button(sidebar, "✋   My Gestures", self.show_gestures)
        self.nav_button(sidebar, "⚙   Settings", self.show_settings)
        self.nav_button(sidebar, "ⓘ   About", self.show_about)

        ctk.CTkLabel(
            sidebar, text="GESTUREFLOW v1.0",
            text_color=MUTED,
            font=ctk.CTkFont(size=10)
        ).pack(side="bottom", pady=20)

        # Main content area
        self.content = ctk.CTkFrame(
            self, fg_color=BG, corner_radius=0
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=30, pady=25)
        self.content.grid_columnconfigure((0, 1), weight=1)

        self.show_home()

    def nav_button(self, parent, text, command, active=False):
        ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=43,
            anchor="w",
            corner_radius=10,
            fg_color=EMERALD if active else "transparent",
            hover_color=PANEL_LIGHT,
            text_color="#10231F" if active else WHITE,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", padx=15, pady=5)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text="Welcome to GestureFlow 👋",
            font=ctk.CTkFont(size=31, weight="bold"),
            text_color=WHITE
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(15, 5))

        ctk.CTkLabel(
            self.content,
            text=f"Hello, {self.user_name}! Control your computer using hand gestures.",
            text_color=MUTED,
            font=ctk.CTkFont(size=14)
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 25))

        # Hero panel
        hero = ctk.CTkFrame(
            self.content, fg_color=PANEL, corner_radius=20
        )
        hero.grid(
            row=2, column=0, columnspan=2,
            sticky="ew", pady=(0, 20)
        )

        ctk.CTkLabel(
            hero, text="✋",
            font=ctk.CTkFont(size=55),
            text_color=AQUA
        ).pack(pady=(22, 5))

        ctk.CTkLabel(
            hero, text="Touchless Control. Smarter Interaction.",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=WHITE
        ).pack(pady=5)

        ctk.CTkLabel(
            hero,
            text="Use your webcam to recognize hand gestures and control your system.",
            font=ctk.CTkFont(size=13),
            text_color=MUTED,
            wraplength=650
        ).pack(pady=(0, 15))

        ctk.CTkButton(
            hero,
            text="OPEN GESTURE CONTROL  →",
            height=48,
            width=280,
            corner_radius=12,
            fg_color=EMERALD,
            hover_color="#269B82",
            text_color="#10231F",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.open_gesture_control
        ).pack(pady=(0, 25))

        # Information cards
        self.info_card(
            3, 0, "✋  Gesture Recognition",
            "Recognize predefined hand gestures using your webcam."
        )
        self.info_card(
            3, 1, "💻  System Control",
            "Use supported gestures for actions such as media control."
        )
        self.info_card(
            4, 0, "📷  Camera Access",
            "Camera starts only after you open Gesture Control."
        )
        self.info_card(
            4, 1, "🔒  Account",
            f"Signed in as:\n{self.user_name}"
        )

    def info_card(self, row, column, title, description):
        card = ctk.CTkFrame(
            self.content, fg_color=PANEL, corner_radius=15
        )
        card.grid(
            row=row, column=column,
            sticky="nsew", padx=7, pady=7
        )

        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=AQUA
        ).pack(anchor="w", padx=18, pady=(17, 8))

        ctk.CTkLabel(
            card, text=description,
            font=ctk.CTkFont(size=12),
            text_color=MUTED,
            wraplength=330,
            justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 18))

    def show_gestures(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content, text="My Gestures",
            font=ctk.CTkFont(size=29, weight="bold"),
            text_color=WHITE
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=15)

        gestures = [
            ("✊", "Fist", "Previous"),
            ("👍", "Thumbs Up", "Next"),
            ("☝", "One Finger", "Volume Up"),
            ("✌", "Two Fingers", "Play / Pause"),
            ("3", "Three Fingers", "Volume Down"),
            ("🤘", "Rock Sign", "Mute / Unmute"),
            ("👌", "OK Sign", "Enter"),
            ("🖖", "Four Fingers", "Sleep Mode"),
        ]

        ctk.CTkLabel(
            self.content,
            text="These are the gestures listed in the current dashboard template. "
                 "Make sure they match your gesture_logic.py.",
            text_color=MUTED, wraplength=750, justify="left"
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))

        for index, (symbol, name, action) in enumerate(gestures):
            row = 2 + index // 2
            col = index % 2
            card = ctk.CTkFrame(
                self.content, fg_color=PANEL, corner_radius=12
            )
            card.grid(row=row, column=col, sticky="ew", padx=6, pady=6)

            ctk.CTkLabel(
                card, text=f"{symbol}   {name}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=AQUA
            ).pack(anchor="w", padx=15, pady=(13, 4))

            ctk.CTkLabel(
                card, text=f"Action: {action}",
                text_color=MUTED
            ).pack(anchor="w", padx=15, pady=(0, 13))

    def show_settings(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content, text="Settings",
            font=ctk.CTkFont(size=29, weight="bold"),
            text_color=WHITE
        ).grid(row=0, column=0, sticky="w", pady=15)

        settings = [
            ("Appearance", "Dark theme"),
            ("Camera", "Camera is opened from Gesture Control"),
            ("Authentication", "Firebase Email/Password and Google sign-in"),
            ("Gesture model", "MediaPipe Tasks API"),
        ]

        for row, (name, value) in enumerate(settings, start=1):
            card = ctk.CTkFrame(
                self.content, fg_color=PANEL, corner_radius=12
            )
            card.grid(row=row, column=0, columnspan=2,
                      sticky="ew", pady=7)

            ctk.CTkLabel(
                card, text=name,
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=AQUA
            ).pack(anchor="w", padx=18, pady=(12, 3))

            ctk.CTkLabel(
                card, text=value, text_color=MUTED
            ).pack(anchor="w", padx=18, pady=(0, 12))

    def show_about(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content, text="About GestureFlow",
            font=ctk.CTkFont(size=29, weight="bold"),
            text_color=WHITE
        ).grid(row=0, column=0, sticky="w", pady=15)

        ctk.CTkLabel(
            self.content,
            text=(
                "GestureFlow is an AI-based hand gesture control system.\n\n"
                "It uses computer vision to detect hand landmarks through a webcam "
                "and recognizes supported gestures to trigger computer actions.\n\n"
                "Technologies: Python, CustomTkinter, OpenCV, MediaPipe Tasks API "
                "and Firebase Authentication."
            ),
            text_color=MUTED,
            font=ctk.CTkFont(size=15),
            justify="left",
            wraplength=720
        ).grid(row=1, column=0, sticky="nw", pady=10)

    def open_gesture_control(self):
        try:
            # Import only when the user clicks the button.
            from main import GestureFlowApp

            self.destroy()
            app = GestureFlowApp()
            app.mainloop()
        except Exception as exc:
            messagebox.showerror(
                "Gesture Control",
                "Gesture Control open nahi ho paya.\n\n"
                f"Error: {exc}\n\n"
                "Check karo ki main.py aur gesture_logic.py project folder mein hain."
            )


if __name__ == "__main__":
    HomeDashboard().mainloop()
