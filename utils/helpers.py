"""
Helper utilities for SecureVault.

Provides common UI colors, styles, and utility functions
used across multiple UI modules.
"""

# ── Color Theme ──────────────────────────────────────────────────────

# Cybersecurity-themed dark color palette
COLORS = {
    "bg_dark": "#1a1a2e",        # Dark navy background
    "bg_medium": "#16213e",      # Slightly lighter navy
    "bg_card": "#0f3460",        # Card/panel background
    "accent": "#e94560",         # Red accent (primary action)
    "accent_hover": "#ff6b81",   # Lighter red for hover
    "text_primary": "#ffffff",   # White text
    "text_secondary": "#a0a0b0", # Grey text
    "text_accent": "#e94560",    # Red text
    "success": "#2ecc71",        # Green for success
    "warning": "#f39c12",        # Orange for warnings
    "danger": "#e74c3c",         # Red for danger/errors
    "input_bg": "#1a1a3e",       # Input field background
    "input_fg": "#ffffff",       # Input field text
    "input_insert": "#ffffff",   # Input cursor color
    "border": "#2a2a5e",         # Border color
    "strength_very_weak": "#e74c3c",
    "strength_weak": "#e67e22",
    "strength_medium": "#f1c40f",
    "strength_strong": "#27ae60",
    "strength_very_strong": "#2ecc71",
}

# ── Fonts ────────────────────────────────────────────────────────────

FONTS = {
    "title": ("Segoe UI", 24, "bold"),
    "heading": ("Segoe UI", 16, "bold"),
    "subheading": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 11),
    "body_bold": ("Segoe UI", 11, "bold"),
    "small": ("Segoe UI", 9),
    "mono": ("Consolas", 11),
    "button": ("Segoe UI", 11, "bold"),
    "entry": ("Consolas", 12),
}

# ── Window Settings ─────────────────────────────────────────────────

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "SecureVault — Secure Password Manager"
MIN_WIDTH = 700
MIN_HEIGHT = 500


# ── Helper Functions ─────────────────────────────────────────────────

def center_window(window, width=None, height=None):
    """
    Center a Tkinter window on the screen.

    Args:
        window: The Tkinter window/Toplevel to center.
        width: Window width (defaults to WINDOW_WIDTH).
        height: Window height (defaults to WINDOW_HEIGHT).
    """
    if width is None:
        width = WINDOW_WIDTH
    if height is None:
        height = WINDOW_HEIGHT

    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


def createStyledEntry(parent, show=None, font_key="entry", width=None):
    """
    Create a styled Entry widget matching the dark theme.

    Args:
        parent: The parent widget.
        show: Character to show instead of text (for passwords).
        font_key: Key into FONTS dict for font style.
        width: Width of the entry widget.

    Returns:
        A tkinter Entry widget.
    """
    import tkinter as tk
    entry = tk.Entry(
        parent,
        bg=COLORS["input_bg"],
        fg=COLORS["input_fg"],
        insertbackground=COLORS["input_insert"],
        font=FONTS[font_key],
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"],
        show=show,
        width=width,
    )
    return entry


def createStyledButton(parent, text, command=None, style="primary", **kwargs):
    """
    Create a styled Button widget matching the dark theme.

    Args:
        parent: The parent widget.
        text: Button label text.
        command: Callback function.
        style: One of 'primary', 'secondary', 'danger', 'success'.
        **kwargs: Additional tkinter Button options.

    Returns:
        A tkinter Button widget.
    """
    import tkinter as tk

    style_map = {
        "primary": (COLORS["accent"], COLORS["text_primary"]),
        "secondary": (COLORS["bg_card"], COLORS["text_primary"]),
        "danger": (COLORS["danger"], COLORS["text_primary"]),
        "success": (COLORS["success"], COLORS["text_primary"]),
    }

    bg, fg = style_map.get(style, style_map["primary"])

    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=COLORS["accent_hover"],
        activeforeground=COLORS["text_primary"],
        font=FONTS["button"],
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=15,
        pady=6,
        **kwargs,
    )
    return button


def createStyledLabel(parent, text, font_key="body", fg_key="text_primary", **kwargs):
    """
    Create a styled Label widget matching the dark theme.

    Args:
        parent: The parent widget.
        text: Label text.
        font_key: Key into FONTS dict.
        fg_key: Key into COLORS dict for foreground color.
        **kwargs: Additional tkinter Label options.

    Returns:
        A tkinter Label widget.
    """
    import tkinter as tk
    label = tk.Label(
        parent,
        text=text,
        bg=kwargs.pop("bg", COLORS["bg_dark"]),
        fg=COLORS.get(fg_key, COLORS["text_primary"]),
        font=FONTS.get(font_key, FONTS["body"]),
        **kwargs,
    )
    return label


def createStyledFrame(parent, **kwargs):
    """
    Create a styled Frame widget matching the dark theme.

    Returns:
        A tkinter Frame widget.
    """
    import tkinter as tk
    frame = tk.Frame(
        parent,
        bg=kwargs.pop("bg", COLORS["bg_dark"]),
        **kwargs,
    )
    return frame
