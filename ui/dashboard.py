"""
Dashboard Screen for SecureVault.

The main screen after successful login. Shows a welcome message,
credential count, and navigation buttons to all major features.
"""

import tkinter as tk
from tkinter import messagebox
from utils.helpers import (
    COLORS, FONTS, center_window,
    createStyledButton, createStyledLabel, createStyledFrame,
)


class DashboardScreen:
    """Main dashboard displayed after successful login."""

    def __init__(self, root, app):
        """
        Initialize the Dashboard screen.

        Args:
            root: The main Tkinter root window.
            app: The main SecureVault application reference.
        """
        self.root = root
        self.app = app
        self.frame = None
        self.welcome_label = None
        self.count_label = None
        self._build()

    def _build(self):
        """Build the dashboard screen UI."""
        self.frame = createStyledFrame(self.root)
        self.frame.pack(fill="both", expand=True)

        # ── Header ──
        header_frame = createStyledFrame(self.frame, bg=COLORS["bg_medium"])
        header_frame.pack(fill="x", pady=(0, 20))

        title = createStyledLabel(
            header_frame,
            text="🔐 SecureVault",
            font_key="heading",
            fg_key="text_primary",
            bg=COLORS["bg_medium"],
        )
        title.pack(side="left", padx=20, pady=15)

        # ── Welcome area ──
        welcome_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        welcome_frame.pack(fill="x", padx=40, pady=(0, 10))

        self.welcome_label = createStyledLabel(
            welcome_frame,
            text="Welcome!",
            font_key="subheading",
            fg_key="text_primary",
            bg=COLORS["bg_dark"],
        )
        self.welcome_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.count_label = createStyledLabel(
            welcome_frame,
            text="Saved credentials: 0",
            font_key="body",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
        )
        self.count_label.pack(anchor="w", padx=20, pady=(0, 15))

        # ── Action buttons grid ──
        grid_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        grid_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # Configure grid weights for equal spacing
        for i in range(3):
            grid_frame.columnconfigure(i, weight=1)
        for i in range(3):
            grid_frame.rowconfigure(i, weight=1)

        # Button definitions: (text, command, style, row, col)
        buttons = [
            ("➕ Add Credential", self._on_add_entry, "primary", 0, 0),
            ("📋 View Credentials", self._on_view_credentials, "secondary", 0, 1),
            ("🔍 Search", self._on_search, "secondary", 0, 2),
            ("🔑 Password Generator", self._on_password_generator, "secondary", 1, 0),
            ("🔒 Logout", self._on_logout, "danger", 1, 1),
            ("🚪 Exit", self._on_exit, "danger", 1, 2),
        ]

        for text, command, style, row, col in buttons:
            btn_frame = createStyledFrame(grid_frame, bg=COLORS["bg_dark"])
            btn_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            btn = createStyledButton(
                btn_frame,
                text=text,
                command=command,
                style=style,
                width=22,
                height=3,
            )
            btn.pack(expand=True, fill="both", padx=5, pady=5)

        # ── Status bar ──
        self.status_label = createStyledLabel(
            self.frame,
            text="Session active",
            font_key="small",
            fg_key="text_secondary",
            bg=COLORS["bg_medium"],
        )
        self.status_label.pack(side="bottom", fill="x", padx=0, pady=0, ipady=3)

    def show(self):
        """Show this screen and refresh the data."""
        self._refresh_data()
        if self.frame:
            self.frame.pack(fill="both", expand=True)

    def hide(self):
        """Hide this screen."""
        if self.frame:
            self.frame.pack_forget()

    def _refresh_data(self):
        """Refresh the welcome message and credential count."""
        username = self.app.auth_manager.current_username
        count = self.app.vault_manager.get_entry_count(
            self.app.auth_manager.current_user_id
        )

        self.welcome_label.config(text=f"Welcome, {username}!")
        self.count_label.config(text=f"Saved credentials: {count}")

    def _on_add_entry(self):
        """Navigate to the add credential screen."""
        self.hide()
        self.app.show_add_entry()

    def _on_view_credentials(self):
        """Navigate to the credential list screen."""
        self.hide()
        self.app.show_credential_list()

    def _on_search(self):
        """Navigate to the credential list with search mode."""
        self.hide()
        self.app.show_credential_list(search_mode=True)

    def _on_password_generator(self):
        """Navigate to the password generator screen."""
        self.hide()
        self.app.show_password_generator()

    def _on_logout(self):
        """Log out and return to welcome screen."""
        result = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if result:
            self.app.auth_manager.logout()
            self.hide()
            self.app.show_welcome()

    def _on_exit(self):
        """Exit the application."""
        result = messagebox.askyesno("Exit", "Are you sure you want to exit?")
        if result:
            self.app.auth_manager.logout()
            self.root.quit()
            self.root.destroy()
