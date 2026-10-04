"""
Add/Edit Credential Screen for SecureVault.

Allows users to add a new credential or edit an existing one.
Includes a password generator integration and password strength indicator.
"""

import tkinter as tk
from tkinter import messagebox
from utils.helpers import (
    COLORS, FONTS, center_window,
    createStyledEntry, createStyledButton, createStyledLabel, createStyledFrame,
)
from security.password_security import check_password_strength


class AddEntryScreen:
    """Screen for adding or editing vault credentials."""

    def __init__(self, root, app):
        """
        Initialize the Add Entry screen.

        Args:
            root: The main Tkinter root window.
            app: The main SecureVault application reference.
        """
        self.root = root
        self.app = app
        self.frame = None
        self.website_entry = None
        self.username_entry = None
        self.password_entry = None
        self.notes_entry = None
        self.strength_label = None
        self.error_label = None
        self._strength_bar = None
        self._editing_id = None  # If set, we're editing an existing entry
        self._build()

    def _build(self):
        """Build the add/edit credential screen UI."""
        self.frame = createStyledFrame(self.root)
        self.frame.pack(fill="both", expand=True)

        # ── Header with back button ──
        header_frame = createStyledFrame(self.frame, bg=COLORS["bg_medium"])
        header_frame.pack(fill="x", pady=(0, 20))

        back_btn = createStyledButton(
            header_frame,
            text="← Back",
            command=self._on_back,
            style="secondary",
        )
        back_btn.pack(side="left", padx=15, pady=12)

        self.title_label = createStyledLabel(
            header_frame,
            text="➕ Add Credential",
            font_key="heading",
            fg_key="text_primary",
            bg=COLORS["bg_medium"],
        )
        self.title_label.pack(side="left", padx=10, pady=12)

        # ── Form area ──
        form_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        form_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # Website/Application
        website_label = createStyledLabel(
            form_frame,
            text="Website / Application",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        website_label.pack(fill="x", padx=20, pady=(15, 3))

        self.website_entry = createStyledEntry(form_frame, width=50)
        self.website_entry.pack(padx=20, pady=(0, 10), ipady=8, fill="x")

        # Username/Email
        username_label = createStyledLabel(
            form_frame,
            text="Username / Email",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        username_label.pack(fill="x", padx=20, pady=(5, 3))

        self.username_entry = createStyledEntry(form_frame, width=50)
        self.username_entry.pack(padx=20, pady=(0, 10), ipady=8, fill="x")

        # Password
        password_label = createStyledLabel(
            form_frame,
            text="Password",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        password_label.pack(fill="x", padx=20, pady=(5, 3))

        pw_frame = createStyledFrame(form_frame, bg=COLORS["bg_dark"])
        pw_frame.pack(fill="x", padx=20, pady=(0, 3))

        self.password_entry = createStyledEntry(pw_frame, show="•", width=35)
        self.password_entry.pack(side="left", ipady=8, fill="x", expand=True, padx=(0, 10))

        # Show/Hide password toggle
        self._show_password = False
        self.toggle_btn = createStyledButton(
            pw_frame,
            text="👁 Show",
            command=self._toggle_password_visibility,
            style="secondary",
        )
        self.toggle_btn.pack(side="left")

        # Bind key release to update strength indicator
        self.password_entry.bind("<KeyRelease>", self._on_password_change)

        # Password strength bar
        strength_frame = createStyledFrame(form_frame, bg=COLORS["bg_dark"])
        strength_frame.pack(fill="x", padx=20, pady=(0, 5))

        self._strength_bar = tk.Canvas(
            strength_frame,
            height=5,
            bg=COLORS["border"],
            highlightthickness=0,
        )
        self._strength_bar.pack(fill="x", pady=(0, 2))

        self.strength_label = createStyledLabel(
            strength_frame,
            text="",
            font_key="small",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
        )
        self.strength_label.pack(anchor="w")

        # Generate Password button
        gen_btn_frame = createStyledFrame(form_frame, bg=COLORS["bg_dark"])
        gen_btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        gen_btn = createStyledButton(
            gen_btn_frame,
            text="🔑 Generate Password",
            command=self._on_generate_password,
            style="primary",
        )
        gen_btn.pack(side="left")

        # Notes
        notes_label = createStyledLabel(
            form_frame,
            text="Notes (optional)",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        notes_label.pack(fill="x", padx=20, pady=(5, 3))

        self.notes_entry = tk.Text(
            form_frame,
            height=3,
            bg=COLORS["input_bg"],
            fg=COLORS["input_fg"],
            insertbackground=COLORS["input_insert"],
            font=FONTS["body"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )
        self.notes_entry.pack(padx=20, pady=(0, 10), fill="x")

        # ── Error label ──
        self.error_label = createStyledLabel(
            form_frame,
            text="",
            font_key="small",
            fg_key="danger",
            bg=COLORS["bg_dark"],
        )
        self.error_label.pack(pady=(0, 5))

        # ── Buttons ──
        btn_frame = createStyledFrame(form_frame, bg=COLORS["bg_dark"])
        btn_frame.pack(pady=(5, 15))

        self.save_btn = createStyledButton(
            btn_frame,
            text="💾 Save Credential",
            command=self._on_save,
            style="success",
            width=20,
        )
        self.save_btn.pack(side="left", padx=10)

        clear_btn = createStyledButton(
            btn_frame,
            text="🗑 Clear",
            command=self._clear_fields,
            style="secondary",
            width=20,
        )
        clear_btn.pack(side="left", padx=10)

    def show(self, entry_id=None):
        """
        Show this screen.

        Args:
            entry_id: If provided, we're editing an existing entry.
        """
        self._clear_fields()
        self._editing_id = entry_id

        if entry_id:
            self.title_label.config(text="✏️ Edit Credential")
            self.save_btn.config(text="💾 Update Credential")
            self._load_entry(entry_id)
        else:
            self.title_label.config(text="➕ Add Credential")
            self.save_btn.config(text="💾 Save Credential")

        if self.frame:
            self.frame.pack(fill="both", expand=True)
        self.website_entry.focus_set()

    def hide(self):
        """Hide this screen."""
        if self.frame:
            self.frame.pack_forget()

    def _clear_fields(self):
        """Clear all input fields."""
        self.website_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.notes_entry.delete("1.0", tk.END)
        self.error_label.config(text="")
        self.strength_label.config(text="")
        self._strength_bar.delete("all")
        self._editing_id = None

    def _load_entry(self, entry_id):
        """Load an existing entry for editing."""
        key = self.app.auth_manager.get_derived_key()
        user_id = self.app.auth_manager.current_user_id
        entry, error = self.app.vault_manager.get_entry(entry_id, user_id, key)

        if entry:
            self.website_entry.delete(0, tk.END)
            self.website_entry.insert(0, entry["website"])

            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, entry["username"])

            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, entry["password"])

            self.notes_entry.delete("1.0", tk.END)
            self.notes_entry.insert("1.0", entry["notes"])

            self._on_password_change()
        else:
            messagebox.showerror("Error", error or "Failed to load credential.")

    def _on_password_change(self, event=None):
        """Update the password strength indicator."""
        password = self.password_entry.get()
        if not password:
            self.strength_label.config(text="")
            self._strength_bar.delete("all")
            return

        result = check_password_strength(password)
        score = result["score"]
        level = result["level"]

        color_map = {
            "Very Weak": COLORS["strength_very_weak"],
            "Weak": COLORS["strength_weak"],
            "Medium": COLORS["strength_medium"],
            "Strong": COLORS["strength_strong"],
            "Very Strong": COLORS["strength_very_strong"],
        }
        color = color_map.get(level, COLORS["strength_weak"])

        self._strength_bar.delete("all")
        bar_width = (score / 100) * 400  # approximate width
        if bar_width > 0:
            self._strength_bar.create_rectangle(
                0, 0, max(bar_width, 5), 5,
                fill=color, outline=""
            )

        self.strength_label.config(text=f"Strength: {level}", fg=color)

    def _toggle_password_visibility(self):
        """Toggle password visibility."""
        self._show_password = not self._show_password
        if self._show_password:
            self.password_entry.config(show="")
            self.toggle_btn.config(text="🙈 Hide")
        else:
            self.password_entry.config(show="•")
            self.toggle_btn.config(text="👁 Show")

    def _on_generate_password(self):
        """Open the password generator and use the result."""
        self.hide()
        self.app.show_password_generator(return_to_entry=True)

    def use_generated_password(self, password):
        """
        Called by the password generator when a password is selected.

        Args:
            password: The generated password to insert.
        """
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        self._on_password_change()
        if self.frame:
            self.frame.pack(fill="both", expand=True)

    def _show_error(self, message):
        """Display an error message."""
        self.error_label.config(text=message)

    def _on_save(self):
        """Save the credential (add or update)."""
        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        notes = self.notes_entry.get("1.0", tk.END).strip()

        # Validation
        if not website:
            self._show_error("Website/Application name is required.")
            return
        if not username:
            self._show_error("Username/Email is required.")
            return
        if not password:
            self._show_error("Password is required.")
            return

        key = self.app.auth_manager.get_derived_key()
        user_id = self.app.auth_manager.current_user_id

        if self._editing_id:
            # Update existing entry
            success, message = self.app.vault_manager.update_entry(
                self._editing_id, user_id, key,
                website, username, password, notes
            )
        else:
            # Add new entry
            success, message = self.app.vault_manager.add_entry(
                user_id, key,
                website, username, password, notes
            )

        if success:
            messagebox.showinfo("Success", message)
            self.hide()
            self.app.show_credential_list()
        else:
            self._show_error(message)

    def _on_back(self):
        """Navigate back to the credential list or dashboard."""
        self.hide()
        if self._editing_id:
            self.app.show_credential_list()
        else:
            self.app.show_dashboard()
