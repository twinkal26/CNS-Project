"""
Registration Screen for SecureVault.

Allows new users to create an account with a username and master password.
Displays real-time password strength feedback.
"""

import tkinter as tk
from tkinter import messagebox
from utils.helpers import (
    COLORS, FONTS, center_window,
    createStyledEntry, createStyledButton, createStyledLabel, createStyledFrame,
)
from security.password_security import check_password_strength


class RegisterScreen:
    """Registration / account creation screen."""

    def __init__(self, root, app):
        """
        Initialize the Registration screen.

        Args:
            root: The main Tkinter root window.
            app: The main SecureVault application reference.
        """
        self.root = root
        self.app = app
        self.frame = None
        self.username_entry = None
        self.password_entry = None
        self.confirm_entry = None
        self.strength_label = None
        self.feedback_label = None
        self._strength_bar = None
        self._build()

    def _build(self):
        """Build the registration screen UI."""
        self.frame = createStyledFrame(self.root)
        self.frame.pack(fill="both", expand=True)

        # ── Center container ──
        center_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ── Title ──
        title = createStyledLabel(
            center_frame,
            text="📝 Create Account",
            font_key="heading",
            fg_key="text_primary",
            bg=COLORS["bg_dark"],
        )
        title.pack(pady=(0, 25))

        # ── Username field ──
        username_label = createStyledLabel(
            center_frame,
            text="Username",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        username_label.pack(fill="x", padx=60)

        self.username_entry = createStyledEntry(center_frame, width=35)
        self.username_entry.pack(pady=(5, 15), padx=60, ipady=8)

        # ── Password field ──
        password_label = createStyledLabel(
            center_frame,
            text="Master Password",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        password_label.pack(fill="x", padx=60)

        self.password_entry = createStyledEntry(center_frame, show="•", width=35)
        self.password_entry.pack(pady=(5, 5), padx=60, ipady=8)

        # Bind key release to update strength indicator
        self.password_entry.bind("<KeyRelease>", self._on_password_change)

        # ── Password strength indicator ──
        strength_frame = createStyledFrame(center_frame, bg=COLORS["bg_dark"])
        strength_frame.pack(fill="x", padx=60, pady=(0, 5))

        # Strength bar canvas
        self._strength_bar = tk.Canvas(
            strength_frame,
            height=6,
            bg=COLORS["border"],
            highlightthickness=0,
        )
        self._strength_bar.pack(fill="x", pady=(0, 3))

        self.strength_label = createStyledLabel(
            strength_frame,
            text="",
            font_key="small",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
        )
        self.strength_label.pack(anchor="w")

        self.feedback_label = createStyledLabel(
            strength_frame,
            text="",
            font_key="small",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
        )
        self.feedback_label.pack(anchor="w")

        # ── Confirm password field ──
        confirm_label = createStyledLabel(
            center_frame,
            text="Confirm Master Password",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        confirm_label.pack(fill="x", padx=60)

        self.confirm_entry = createStyledEntry(center_frame, show="•", width=35)
        self.confirm_entry.pack(pady=(5, 20), padx=60, ipady=8)

        # ── Error message label ──
        self.error_label = createStyledLabel(
            center_frame,
            text="",
            font_key="small",
            fg_key="danger",
            bg=COLORS["bg_dark"],
        )
        self.error_label.pack(pady=(0, 10))

        # ── Buttons ──
        btn_frame = createStyledFrame(center_frame, bg=COLORS["bg_dark"])
        btn_frame.pack()

        create_btn = createStyledButton(
            btn_frame,
            text="Create Account",
            command=self._on_create,
            style="success",
            width=18,
        )
        create_btn.pack(side="left", padx=10)

        back_btn = createStyledButton(
            btn_frame,
            text="Back",
            command=self._on_back,
            style="secondary",
            width=18,
        )
        back_btn.pack(side="left", padx=10)

    def show(self):
        """Show this screen and clear previous inputs."""
        self.clear_fields()
        if self.frame:
            self.frame.pack(fill="both", expand=True)
        self.username_entry.focus_set()

    def hide(self):
        """Hide this screen."""
        if self.frame:
            self.frame.pack_forget()

    def clear_fields(self):
        """Clear all input fields and messages."""
        if self.username_entry:
            self.username_entry.delete(0, tk.END)
        if self.password_entry:
            self.password_entry.delete(0, tk.END)
        if self.confirm_entry:
            self.confirm_entry.delete(0, tk.END)
        self.error_label.config(text="")
        self.strength_label.config(text="")
        self.feedback_label.config(text="")
        if self._strength_bar:
            self._strength_bar.delete("all")

    def _on_password_change(self, event=None):
        """Update the password strength indicator in real-time."""
        password = self.password_entry.get()
        if not password:
            self.strength_label.config(text="")
            self.feedback_label.config(text="")
            self._strength_bar.delete("all")
            return

        result = check_password_strength(password)
        score = result["score"]
        level = result["level"]
        feedback = result["feedback"]

        # Choose color based on level
        color_map = {
            "Very Weak": COLORS["strength_very_weak"],
            "Weak": COLORS["strength_weak"],
            "Medium": COLORS["strength_medium"],
            "Strong": COLORS["strength_strong"],
            "Very Strong": COLORS["strength_very_strong"],
        }
        color = color_map.get(level, COLORS["strength_weak"])

        # Update strength bar
        self._strength_bar.delete("all")
        bar_width = (score / 100) * self._strength_bar.winfo_reqwidth()
        if bar_width > 0:
            self._strength_bar.create_rectangle(
                0, 0, max(bar_width, 5), 6,
                fill=color, outline=""
            )

        # Update labels
        self.strength_label.config(text=f"Strength: {level} ({score}/100)", fg=color)
        feedback_text = " | ".join(feedback)
        self.feedback_label.config(text=feedback_text)

    def _show_error(self, message):
        """Display an error message."""
        self.error_label.config(text=message)

    def _on_create(self):
        """Handle account creation button click."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        # ── Validation ──
        if not username:
            self._show_error("Please enter a username.")
            return

        if not password:
            self._show_error("Please enter a master password.")
            return

        if len(password) < 8:
            self._show_error("Master password must be at least 8 characters.")
            return

        if password != confirm:
            self._show_error("Passwords do not match.")
            return

        # Check strength
        strength = check_password_strength(password)
        if strength["score"] < 40:
            self._show_error("Password is too weak. Please choose a stronger password.")
            return

        # ── Register ──
        success, message = self.app.auth_manager.register(username, password)

        if success:
            messagebox.showinfo("Success", message)
            self.hide()
            self.app.show_login()
        else:
            self._show_error(message)

    def _on_back(self):
        """Navigate back to the welcome screen."""
        self.hide()
        self.app.show_welcome()
