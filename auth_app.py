
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from auth_service import (
    AuthError,
    login_email,
    signup_email,
    login_google
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AuthApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("GestureFlow | Account")
        self.state("zoomed")
        self.resizable(True, True)
        self.configure(fg_color="#111827")

        self.page = "login"

        self.title_label = ctk.CTkLabel(
            self,
            text="GestureFlow",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#8BE9D4"
        )
        self.title_label.pack(pady=(35, 5))

        ctk.CTkLabel(
            self,
            text="AI-Based Hand Gesture Control System",
            text_color="#B7C3D0",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 22))

        self.card = ctk.CTkFrame(
            self,
            corner_radius=18,
            fg_color="#1B2636"
        )
        self.card.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=(0, 28)
        )

        self.form_title = ctk.CTkLabel(
            self.card,
            text="Welcome back",
            font=ctk.CTkFont(size=23, weight="bold")
        )
        self.form_title.pack(pady=(24, 18))

        self.email_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Email address",
            height=42,
            width=330
        )
        self.email_entry.pack(pady=7)

        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Password",
            show="•",
            height=42,
            width=330
        )
        self.password_entry.pack(pady=7)

        self.primary_button = ctk.CTkButton(
            self.card,
            text="Login",
            height=42,
            width=330,
            fg_color="#35BFA0",
            hover_color="#269B82",
            text_color="#10231F",
            command=self.submit_email
        )
        self.primary_button.pack(pady=(18, 10))

        self.switch_button = ctk.CTkButton(
            self.card,
            text="New here? Create an account",
            height=32,
            fg_color="transparent",
            hover_color="#26364A",
            command=self.toggle_page
        )
        self.switch_button.pack(pady=(0, 10))

        ctk.CTkLabel(
            self.card,
            text="────────  OR  ────────",
            text_color="#9AA9BA"
        ).pack(pady=8)

        self.google_button = ctk.CTkButton(
            self.card,
            text="Continue with Google",
            height=42,
            width=330,
            fg_color="#F4F6F8",
            hover_color="#DDE3E8",
            text_color="#1D2733",
            command=self.submit_google
        )
        self.google_button.pack(pady=(8, 12))

        self.status = ctk.CTkLabel(
            self.card,
            text="Your account is secured by Firebase Authentication.",
            text_color="#9AA9BA",
            wraplength=320,
            font=ctk.CTkFont(size=11)
        )
        self.status.pack(pady=(0, 18))

    def toggle_page(self):

        if self.page == "login":
            self.page = "signup"
            self.form_title.configure(
                text="Create your account"
            )
            self.primary_button.configure(text="Sign Up")
            self.switch_button.configure(
                text="Already have an account? Login"
            )

        else:
            self.page = "login"
            self.form_title.configure(text="Welcome back")
            self.primary_button.configure(text="Login")
            self.switch_button.configure(
                text="New here? Create an account"
            )

        self.status.configure(text="")

    def submit_email(self):

        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        self.primary_button.configure(state="disabled")
        self.status.configure(text="Please wait...")
        self.update_idletasks()

        try:

            if self.page == "signup":

                user = signup_email(email, password)

                messagebox.showinfo(
                    "Account created",
                    "Signup successful! You are now logged in."
                )

            else:
                user = login_email(email, password)

            self.open_home(user)

        except AuthError as exc:

            try:
                self.status.configure(text=str(exc))
                self.primary_button.configure(state="normal")
            except tk.TclError:
                pass

            messagebox.showerror(
                "Authentication",
                str(exc)
            )

        except Exception as exc:

            messagebox.showerror("Error", str(exc))

            try:
                self.primary_button.configure(state="normal")
            except tk.TclError:
                pass

    def submit_google(self):

        self.google_button.configure(state="disabled")
        self.status.configure(
            text="Google sign-in is opening in your browser..."
        )
        self.update_idletasks()

        try:

            user = login_google()
            self.open_home(user)

        except AuthError as exc:

            try:
                self.status.configure(text=str(exc))
                self.google_button.configure(state="normal")
            except tk.TclError:
                pass

            messagebox.showerror(
                "Google sign-in",
                str(exc)
            )

        except Exception as exc:

            messagebox.showerror("Error", str(exc))

            try:
                self.google_button.configure(state="normal")
            except tk.TclError:
                pass

    def open_home(self, user):

        email = user.get("email", "")

        self.destroy()

        from home_dashboard import HomeDashboard

        app = HomeDashboard(
            user_name=email or "User"
        )

        app.lift()
        app.focus_force()
        app.attributes("-topmost", True)

        app.after(
            1000,
            lambda: app.attributes("-topmost", False)
        )

        app.mainloop()


if __name__ == "__main__":

    app = AuthApp()
    app.mainloop()
