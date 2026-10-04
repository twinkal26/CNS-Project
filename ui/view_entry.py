"""
View Credential Screen for SecureVault.

Displays the details of a single credential entry.
The password is hidden by default with a show/hide toggle.
Includes a copy-to-clipboard button for convenience.
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import platform
from utils.helpers import (
    COLORS, FONTS,
    createStyledButton, createStyledLabel, createStyledFrame,
)


class ViewEntryScreen:
    """Screen for viewing a single credential's details."""

    def __init__(self, root, app):
        """
        Initialize the View Entry screen.

        Args:
            root: The main Tkinter root window.
            app: The main SecureVault application reference.
        """
        self.root = root
        self.app = app
        self.frame = None
        self._entry = None
        self._password_visible = False
        self._build()

    def _build(self):
        """Build the view entry screen UI."""
        self.frame = createStyledFrame(self.root)
        self.frame.pack(fill="both", expand=True)

        # ── Header ──
        header_frame = createStyledFrame(self.frame, bg=COLORS["bg_medium"])
        header_frame.pack(fill="x", pady=(0, 20))

        close_btn = createStyledButton(
            header_frame,
            text="← Close",
            command=self._on_close,
            style="secondary",
        )
        close_btn.pack(side="left", padx=15, pady=12)

        title = createStyledLabel(
            header_frame,
            text="👁 View Credential",
            font_key="heading",
            fg_key="text_primary",
            bg=COLORS["bg_medium"],
        )
        title.pack(side="left", padx=10, pady=12)

        # ── Card container ──
        card_frame = createStyledFrame(self.frame, bg=COLORS["bg_card"])
        card_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # Website
        self._add_field(card_frame, "Website / Application", 0)
        self.website_value = createStyledLabel(
            card_frame, text="", font_key="body",
            fg_key="text_primary", bg=COLORS["bg_card"],
        )
        self.website_value.grid(row=1, column=0, columnspan=3, sticky="w", padx=30, pady=(0, 15))

        # Username
        self._add_field(card_frame, "Username / Email", 2)
        self.username_value = createStyledLabel(
            card_frame, text="", font_key="body",
            fg_key="text_primary", bg=COLORS["bg_card"],
        )
        self.username_value.grid(row=3, column=0, columnspan=3, sticky="w", padx=30, pady=(0, 15))

        # Password
        self._add_field(card_frame, "Password", 4)
        pw_frame = createStyledFrame(card_frame, bg=COLORS["bg_card"])
        pw_frame.grid(row=5, column=0, columnspan=3, sticky="ew", padx=30, pady=(0, 15))

        self.password_value = createStyledLabel(
            pw_frame, text="••••••••", font_key="mono",
            fg_key="text_primary", bg=COLORS["bg_card"],
        )
        self.password_value.pack(side="left", fill="x", expand=True)

        toggle_btn = createStyledButton(
            pw_frame,
            text="👁 Show",
            command=self._toggle_password,
            style="secondary",
        )
        toggle_btn.pack(side="left", padx=(10, 5))

        copy_btn = createStyledButton(
            pw_frame,
            text="📋 Copy",
            command=self._copy_password,
            style="primary",
        )
        copy_btn.pack(side="left")

        # Notes
        self._add_field(card_frame, "Notes", 6)
        self.notes_value = createStyledLabel(
            card_frame, text="", font_key="body",
            fg_key="text_secondary", bg=COLORS["bg_card"],
            wraplength=600, justify="left",
        )
        self.notes_value.grid(row=7, column=0, columnspan=3, sticky="w", padx=30, pady=(0, 15))

        # Configure grid
        card_frame.columnconfigure(0, weight=1)

        # ── Close button at bottom ──
        bottom_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        bottom_frame.pack(fill="x", padx=40, pady=(0, 20))

        close_bottom_btn = createStyledButton(
            bottom_frame,
            text="Close",
            command=self._on_close,
            style="secondary",
            width=20,
        )
        close_bottom_btn.pack(pady=10)

    def _add_field(self, parent, label_text, row):
        """Add a field label to the card."""
        label = createStyledLabel(
            parent,
            text=label_text,
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_card"],
            anchor="w",
        )
        label.grid(row=row, column=0, sticky="w", padx=30, pady=(10, 3))

    def show(self, entry):
        """
        Show this screen with the given entry data.

        Args:
            entry: Dict containing credential data.
        """
        self._entry = entry
        self._password_visible = False

        # Populate fields
        self.website_value.config(text=entry.get("website", ""))
        self.username_value.config(text=entry.get("username", ""))
        self.password_value.config(text="••••••••")
        self.notes_value.config(text=entry.get("notes", "") or "(no notes)")

        if self.frame:
            self.frame.pack(fill="both", expand=True)

    def hide(self):
        """Hide this screen."""
        if self.frame:
            self.frame.pack_forget()

    def _toggle_password(self):
        """Toggle password visibility."""
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.password_value.config(text=self._entry.get("password", ""))
        else:
            self.password_value.config(text="••••••••")

    def _copy_password(self):
        """Copy the password to the clipboard."""
        password = self._entry.get("password", "")
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()
            messagebox.showinfo("Copied", "Password copied to clipboard!")
        else:
            messagebox.showwarning("No Password", "No password to copy.")

    def _on_close(self):
        """Close this screen and return to the credential list."""
        self.hide()
        self.app.show_credential_list()
