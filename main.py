"""
SecureVault — Secure Password Manager
Main Application Entry Point

This module initializes the Tkinter root window, sets up the database,
cryptography, authentication, and vault managers, and manages navigation
between all application screens.

Architecture:
    User → Tkinter GUI → Authentication Layer → Cryptography Layer
    → Vault Manager → SQLite Database

Run:
    python main.py
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add project root to path so imports work from any location
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import DatabaseManager
from auth.authentication import AuthenticationManager
from vault.vault_manager import VaultManager
from ui.welcome import WelcomeScreen
from ui.login import LoginScreen
from ui.register import RegisterScreen
from ui.dashboard import DashboardScreen
from ui.add_entry import AddEntryScreen
from ui.credential_list import CredentialListScreen
from ui.view_entry import ViewEntryScreen
from ui.password_generator import PasswordGeneratorScreen
from utils.helpers import (
    COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    MIN_WIDTH, MIN_HEIGHT, center_window,
)


class SecureVaultApp:
    """
    Main application class for SecureVault.

    Manages the lifecycle of all screens and shared state
    (database, auth manager, vault manager).
    """

    def __init__(self):
        """Initialize the application."""
        # ── Create the main Tkinter window ──
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        center_window(self.root)

        # Prevent closing without confirmation
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── Initialize backend managers ──
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthenticationManager(self.db_manager)
        self.vault_manager = VaultManager(self.db_manager)

        # ── Initialize all screens ──
        self.screens = {}
        self.screens["welcome"] = WelcomeScreen(self.root, self)
        self.screens["login"] = LoginScreen(self.root, self)
        self.screens["register"] = RegisterScreen(self.root, self)
        self.screens["dashboard"] = DashboardScreen(self.root, self)
        self.screens["add_entry"] = AddEntryScreen(self.root, self)
        self.screens["credential_list"] = CredentialListScreen(self.root, self)
        self.screens["view_entry"] = ViewEntryScreen(self.root, self)
        self.screens["password_generator"] = PasswordGeneratorScreen(self.root, self)

        # Show the welcome screen on startup
        self.show_welcome()

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()

    # ── Screen Navigation ────────────────────────────────────────────

    def _hide_all(self):
        """Hide all screens."""
        for screen in self.screens.values():
            screen.hide()

    def show_welcome(self):
        """Navigate to the welcome screen."""
        self._hide_all()
        self.screens["welcome"].show()

    def show_login(self):
        """Navigate to the login screen."""
        self._hide_all()
        self.screens["login"].show()

    def show_register(self):
        """Navigate to the registration screen."""
        self._hide_all()
        self.screens["register"].show()

    def show_dashboard(self):
        """Navigate to the dashboard screen."""
        if not self.auth_manager.is_authenticated():
            messagebox.showwarning("Session Expired", "Please log in again.")
            self.show_login()
            return
        self._hide_all()
        self.screens["dashboard"].show()

    def show_add_entry(self, entry_id=None):
        """Navigate to the add/edit entry screen."""
        if not self.auth_manager.is_authenticated():
            messagebox.showwarning("Session Expired", "Please log in again.")
            self.show_login()
            return
        self._hide_all()
        self.screens["add_entry"].show(entry_id=entry_id)

    def show_add_entry_with_password(self, password):
        """
        Navigate to the add entry screen with a pre-filled password
        (used when returning from the password generator).

        Args:
            password: The generated password to insert.
        """
        self._hide_all()
        self.screens["add_entry"].show()
        self.screens["add_entry"].use_generated_password(password)

    def show_credential_list(self, search_mode=False):
        """Navigate to the credential list screen."""
        if not self.auth_manager.is_authenticated():
            messagebox.showwarning("Session Expired", "Please log in again.")
            self.show_login()
            return
        self._hide_all()
        self.screens["credential_list"].show(search_mode=search_mode)

    def show_view_entry(self, entry):
        """
        Navigate to the view entry screen.

        Args:
            entry: The credential entry dict to display.
        """
        if not self.auth_manager.is_authenticated():
            messagebox.showwarning("Session Expired", "Please log in again.")
            self.show_login()
            return
        self._hide_all()
        self.screens["view_entry"].show(entry)

    def show_password_generator(self, return_to_entry=False):
        """Navigate to the password generator screen."""
        self._hide_all()
        self.screens["password_generator"].show(return_to_entry=return_to_entry)

    # ── Application Lifecycle ────────────────────────────────────────

    def _on_close(self):
        """Handle window close — clear sensitive data and exit."""
        result = messagebox.askyesno(
            "Exit SecureVault",
            "Are you sure you want to exit?\nAll session data will be cleared."
        )
        if result:
            # Clear sensitive data from memory
            self.auth_manager.logout()
            self.root.quit()
            self.root.destroy()


# ── Entry Point ──────────────────────────────────────────────────────

def main():
    """Launch the SecureVault application."""
    app = SecureVaultApp()
    app.run()


if __name__ == "__main__":
    main()
