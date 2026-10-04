"""
Welcome Screen for SecureVault.

The first screen the user sees when launching the application.
Provides options to Login, Create Account, or Exit.
"""

import tkinter as tk
from tkinter import messagebox
from utils.helpers import (
    COLORS, FONTS, center_window,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    createStyledButton, createStyledLabel, createStyledFrame,
)


class WelcomeScreen:
    """Welcome / landing screen displayed at application start."""

    def __init__(self, root, app):
        """
        Initialize the Welcome screen.

        Args:
            root: The main Tkinter root window.
            app: The main SecureVault application reference.
        """
        self.root = root
        self.app = app
        self.frame = None
        self._build()

    def _build(self):
        """Build the welcome screen UI."""
        self.frame = createStyledFrame(self.root)
        self.frame.pack(fill="both", expand=True)

        # ── Center container ──
        center_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ── Title / Logo area ──
        title_label = createStyledLabel(
            center_frame,
            text="🔐 SecureVault",
            font_key="title",
            fg_key="text_primary",
            bg=COLORS["bg_dark"],
        )
        title_label.pack(pady=(0, 5))

        subtitle_label = createStyledLabel(
            center_frame,
            text="Secure Password Manager",
            font_key="subheading",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
        )
        subtitle_label.pack(pady=(0, 40))

        # ── Buttons ──
        btn_frame = createStyledFrame(center_frame, bg=COLORS["bg_dark"])
        btn_frame.pack()

        login_btn = createStyledButton(
            btn_frame,
            text="🔑  Login",
            command=self._on_login,
            style="primary",
            width=25,
            height=2,
        )
        login_btn.pack(pady=8)

        register_btn = createStyledButton(
            btn_frame,
            text="📝  Create Account",
            command=self._on_register,
            style="secondary",
            width=25,
            height=2,
        )
        register_btn.pack(pady=8)

        exit_btn = createStyledButton(
            btn_frame,
            text="🚪  Exit",
            command=self._on_exit,
            style="danger",
            width=25,
            height=2,
        )
        exit_btn.pack(pady=8)

        # ── Footer ──
        footer_label = createStyledLabel(
            self.frame,
            text="CNS Mini Project — Cryptography & Network Security",
            font_key="small",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
        )
        footer_label.pack(side="bottom", pady=10)

    def show(self):
        """Show this screen."""
        if self.frame:
            self.frame.pack(fill="both", expand=True)

    def hide(self):
        """Hide this screen."""
        if self.frame:
            self.frame.pack_forget()

    def _on_login(self):
        """Navigate to login screen."""
        self.hide()
        self.app.show_login()

    def _on_register(self):
        """Navigate to registration screen."""
        self.hide()
        self.app.show_register()

    def _on_exit(self):
        """Exit the application."""
        self.root.quit()
        self.root.destroy()
