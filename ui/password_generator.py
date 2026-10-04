"""
Password Generator Screen for SecureVault.

Provides a UI for generating cryptographically secure passwords
with configurable options (length, character types).
Includes copy-to-clipboard and "Use in Credential" functionality.
"""

import tkinter as tk
from tkinter import messagebox
from utils.helpers import (
    COLORS, FONTS,
    createStyledEntry, createStyledButton, createStyledLabel, createStyledFrame,
)
from security.password_security import generate_password, check_password_strength


class PasswordGeneratorScreen:
    """Screen for generating secure random passwords."""

    def __init__(self, root, app):
        """
        Initialize the Password Generator screen.

        Args:
            root: The main Tkinter root window.
            app: The main SecureVault application reference.
        """
        self.root = root
        self.app = app
        self.frame = None
        self.length_var = None
        self.length_slider = None
        self.uppercase_var = None
        self.lowercase_var = None
        self.numbers_var = None
        self.symbols_var = None
        self.generated_label = None
        self.strength_label = None
        self._strength_bar = None
        self._return_to_entry = False
        self._last_generated = ""
        self._build()

    def _build(self):
        """Build the password generator screen UI."""
        self.frame = createStyledFrame(self.root)
        self.frame.pack(fill="both", expand=True)

        # ── Header ──
        header_frame = createStyledFrame(self.frame, bg=COLORS["bg_medium"])
        header_frame.pack(fill="x", pady=(0, 20))

        back_btn = createStyledButton(
            header_frame,
            text="← Back",
            command=self._on_back,
            style="secondary",
        )
        back_btn.pack(side="left", padx=15, pady=12)

        title = createStyledLabel(
            header_frame,
            text="🔑 Password Generator",
            font_key="heading",
            fg_key="text_primary",
            bg=COLORS["bg_medium"],
        )
        title.pack(side="left", padx=10, pady=12)

        # ── Main content ──
        content_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        content_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # ── Length selector ──
        length_label = createStyledLabel(
            content_frame,
            text="Password Length",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        length_label.pack(fill="x", padx=20, pady=(20, 5))

        slider_frame = createStyledFrame(content_frame, bg=COLORS["bg_dark"])
        slider_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.length_var = tk.IntVar(value=16)

        self.length_slider = tk.Scale(
            slider_frame,
            from_=8,
            to=64,
            orient="horizontal",
            variable=self.length_var,
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
            highlightthickness=0,
            troughcolor=COLORS["border"],
            activebackground=COLORS["accent"],
            font=FONTS["body"],
            length=400,
        )
        self.length_slider.pack(side="left", fill="x", expand=True)

        self.length_display = createStyledLabel(
            slider_frame,
            text="16",
            font_key="heading",
            fg_key="text_accent",
            bg=COLORS["bg_dark"],
        )
        self.length_display.pack(side="right", padx=20)

        # Update display when slider changes
        self.length_var.trace_add("write", self._on_length_change)

        # ── Character type toggles ──
        options_label = createStyledLabel(
            content_frame,
            text="Character Types",
            font_key="body_bold",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
            anchor="w",
        )
        options_label.pack(fill="x", padx=20, pady=(15, 10))

        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.numbers_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)

        options_frame = createStyledFrame(content_frame, bg=COLORS["bg_dark"])
        options_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Create checkboxes with custom styling
        for text, var, col in [
            ("Uppercase (A-Z)", self.uppercase_var, 0),
            ("Lowercase (a-z)", self.lowercase_var, 1),
            ("Numbers (0-9)", self.numbers_var, 2),
            ("Symbols (!@#$...)", self.symbols_var, 3),
        ]:
            cb = tk.Checkbutton(
                options_frame,
                text=text,
                variable=var,
                bg=COLORS["bg_dark"],
                fg=COLORS["text_primary"],
                selectcolor=COLORS["bg_card"],
                activebackground=COLORS["bg_dark"],
                activeforeground=COLORS["text_primary"],
                font=FONTS["body"],
            )
            cb.grid(row=0, column=col, padx=15, pady=5, sticky="w")

        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(2, weight=1)
        options_frame.columnconfigure(3, weight=1)

        # ── Generate button ──
        gen_btn_frame = createStyledFrame(content_frame, bg=COLORS["bg_dark"])
        gen_btn_frame.pack(pady=(10, 20))

        generate_btn = createStyledButton(
            gen_btn_frame,
            text="🎲 Generate Password",
            command=self._on_generate,
            style="primary",
            width=25,
            height=2,
        )
        generate_btn.pack()

        # ── Generated password display ──
        result_frame = createStyledFrame(content_frame, bg=COLORS["bg_card"])
        result_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.generated_label = createStyledLabel(
            result_frame,
            text="Click 'Generate Password' to create a password",
            font_key="mono",
            fg_key="text_secondary",
            bg=COLORS["bg_card"],
            wraplength=600,
        )
        self.generated_label.pack(padx=20, pady=15)

        # ── Strength indicator ──
        strength_frame = createStyledFrame(content_frame, bg=COLORS["bg_dark"])
        strength_frame.pack(fill="x", padx=20, pady=(0, 10))

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

        # ── Action buttons ──
        action_frame = createStyledFrame(content_frame, bg=COLORS["bg_dark"])
        action_frame.pack(pady=(15, 20))

        copy_btn = createStyledButton(
            action_frame,
            text="📋 Copy Password",
            command=self._on_copy,
            style="secondary",
            width=20,
        )
        copy_btn.pack(side="left", padx=10)

        self.use_btn = createStyledButton(
            action_frame,
            text="✅ Use in Credential",
            command=self._on_use,
            style="success",
            width=20,
        )
        self.use_btn.pack(side="left", padx=10)

    def show(self, return_to_entry=False):
        """
        Show this screen.

        Args:
            return_to_entry: If True, the 'Use in Credential' button
                           will send the password back to the add entry screen.
        """
        self._return_to_entry = return_to_entry
        self.use_btn.pack(side="left", padx=10) if return_to_entry else self.use_btn.pack_forget()

        if self.frame:
            self.frame.pack(fill="both", expand=True)

    def hide(self):
        """Hide this screen."""
        if self.frame:
            self.frame.pack_forget()

    def _on_length_change(self, *args):
        """Update the length display."""
        self.length_display.config(text=str(self.length_var.get()))

    def _on_generate(self):
        """Generate a new password with the selected options."""
        length = self.length_var.get()
        use_upper = self.uppercase_var.get()
        use_lower = self.lowercase_var.get()
        use_nums = self.numbers_var.get()
        use_syms = self.symbols_var.get()

        # Ensure at least one option is selected
        if not (use_upper or use_lower or use_nums or use_syms):
            messagebox.showwarning(
                "No Options Selected",
                "Please select at least one character type."
            )
            return

        try:
            password = generate_password(
                length=length,
                use_uppercase=use_upper,
                use_lowercase=use_lower,
                use_numbers=use_nums,
                use_symbols=use_syms,
            )
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self._last_generated = password

        # Display the generated password
        self.generated_label.config(text=password, fg=COLORS["text_primary"])

        # Update strength indicator
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
        bar_width = (score / 100) * 500
        if bar_width > 0:
            self._strength_bar.create_rectangle(
                0, 0, max(bar_width, 5), 6,
                fill=color, outline=""
            )

        self.strength_label.config(
            text=f"Strength: {level} ({score}/100)",
            fg=color,
        )

    def _on_copy(self):
        """Copy the generated password to the clipboard."""
        if not self._last_generated:
            messagebox.showwarning(
                "No Password",
                "Generate a password first."
            )
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(self._last_generated)
        self.root.update()
        messagebox.showinfo("Copied", "Password copied to clipboard!")

    def _on_use(self):
        """Send the generated password back to the add entry screen."""
        if not self._last_generated:
            messagebox.showwarning(
                "No Password",
                "Generate a password first."
            )
            return

        self.hide()
        self.app.show_add_entry_with_password(self._last_generated)

    def _on_back(self):
        """Navigate back to the previous screen."""
        self.hide()
        if self._return_to_entry:
            self.app.show_add_entry()
        else:
            self.app.show_dashboard()
