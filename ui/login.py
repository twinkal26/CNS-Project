"""
Login Screen for SecureVault.

Allows existing users to authenticate with their username and master password.
Displays error messages for invalid credentials and lockout notifications.
"""

import tkinter as tk
from tkinter import messagebox
from utils.helpers import (
    COLORS, FONTS, center_window,
    createStyledEntry, createStyledButton, createStyledLabel, createStyledFrame,
)


class LoginScreen:
    """Login screen for existing users."""

    def __init__(self, root, app):
        """
        Initialize the Login screen.

        Args:
            root: The main Tkinter root window.
            app: The main SecureVault application reference.
        """
        self.root = root
        self.app = app
        self.frame = None
        self.username_entry = None
        self.password_entry = None
        self._build()

    def _build(self):
        """Build the login screen UI."""
        self.frame = createStyledFrame(self.root)
        self.frame.pack(fill="both", expand=True)

        # ── Center container ──
        center_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ── Title ──
        title = createStyledLabel(
            center_frame,
            text="🔑 Login",
            font_key="heading",
            fg_key="text_primary",
            bg=COLORS["bg_dark"],
        )
        title.pack(pady=(0, 30))

        # ── Username field ──
        username_label = createStyledLabel(
            center_frame,
            text="Username",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        username_label.pack(fill="x", padx=50)

        self.username_entry = createStyledEntry(center_frame, width=35)
        self.username_entry.pack(pady=(5, 15), padx=50, ipady=8)

        # ── Password field ──
        password_label = createStyledLabel(
            center_frame,
            text="Master Password",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        password_label.pack(fill="x", padx=50)

        self.password_entry = createStyledEntry(center_frame, show="•", width=35)
        self.password_entry.pack(pady=(5, 25), padx=50, ipady=8)

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

        login_btn = createStyledButton(
            btn_frame,
            text="Login",
            command=self._on_login,
            style="primary",
            width=20,
        )
        login_btn.pack(side="left", padx=10)

        back_btn = createStyledButton(
            btn_frame,
            text="Back",
            command=self._on_back,
            style="secondary",
            width=20,
        )
        back_btn.pack(side="left", padx=10)

        # Bind Enter key to login
        self.root.bind("<Return>", lambda event: self._on_login())

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
        """Clear all input fields and error messages."""
        if self.username_entry:
            self.username_entry.delete(0, tk.END)
        if self.password_entry:
            self.password_entry.delete(0, tk.END)
        self.error_label.config(text="")

    def _show_error(self, message):
        """Display an error message."""
        self.error_label.config(text=message)

    def _on_login(self):
        """Handle login button click."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username:
            self._show_error("Please enter your username.")
            return

        if not password:
            self._show_error("Please enter your master password.")
            return

        # Attempt login through the authentication manager
        success, message = self.app.auth_manager.login(username, password)

        if success:
            self.hide()
            self.app.show_dashboard()
        else:
            self._show_error(message)
            self.password_entry.delete(0, tk.END)

    def _on_back(self):
        """Navigate back to the welcome screen."""
        self.hide()
        self.app.show_welcome()
