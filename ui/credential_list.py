"""
Credential List Screen for SecureVault.

Displays saved credentials in a clean table view.
Supports searching by website or username.
Provides View, Edit, and Delete actions for each entry.
Passwords are NOT displayed in the list — only website and username.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.helpers import (
    COLORS, FONTS, center_window,
    createStyledEntry, createStyledButton, createStyledLabel, createStyledFrame,
)


class CredentialListScreen:
    """Screen displaying the list of saved credentials."""

    def __init__(self, root, app):
        """
        Initialize the Credential List screen.

        Args:
            root: The main Tkinter root window.
            app: The main SecureVault application reference.
        """
        self.root = root
        self.app = app
        self.frame = None
        self.search_entry = None
        self.tree = None
        self._entries = []
        self._search_mode = False
        self._build()

    def _build(self):
        """Build the credential list screen UI."""
        self.frame = createStyledFrame(self.root)
        self.frame.pack(fill="both", expand=True)

        # ── Header ──
        header_frame = createStyledFrame(self.frame, bg=COLORS["bg_medium"])
        header_frame.pack(fill="x", pady=(0, 10))

        back_btn = createStyledButton(
            header_frame,
            text="← Back",
            command=self._on_back,
            style="secondary",
        )
        back_btn.pack(side="left", padx=15, pady=12)

        self.title_label = createStyledLabel(
            header_frame,
            text="📋 My Credentials",
            font_key="heading",
            fg_key="text_primary",
            bg=COLORS["bg_medium"],
        )
        self.title_label.pack(side="left", padx=10, pady=12)

        # ── Search bar ──
        search_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        search_frame.pack(fill="x", padx=20, pady=(5, 10))

        search_label = createStyledLabel(
            search_frame,
            text="🔍",
            font_key="body",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
        )
        search_label.pack(side="left", padx=(10, 5))

        self.search_entry = createStyledEntry(search_frame, width=40)
        self.search_entry.pack(side="left", ipady=6, fill="x", expand=True, padx=(0, 10))

        search_btn = createStyledButton(
            search_frame,
            text="Search",
            command=self._on_search,
            style="primary",
        )
        search_btn.pack(side="left", padx=(0, 5))

        clear_search_btn = createStyledButton(
            search_frame,
            text="Clear",
            command=self._on_clear_search,
            style="secondary",
        )
        clear_search_btn.pack(side="left", padx=(0, 10))

        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda event: self._on_search())

        # ── Table / Treeview ──
        table_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Configure treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"],
                         fieldbackground=COLORS["bg_card"],
                         rowheight=35,
                         font=FONTS["body"])
        style.configure("Custom.Treeview.Heading",
                         background=COLORS["bg_medium"],
                         foreground=COLORS["text_primary"],
                         font=FONTS["body_bold"])
        style.map("Custom.Treeview",
                   background=[("selected", COLORS["accent"])],
                   foreground=[("selected", COLORS["text_primary"])])

        # Create treeview with scrollbars
        tree_container = createStyledFrame(table_frame, bg=COLORS["bg_dark"])
        tree_container.pack(fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(tree_container, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_container,
            columns=("id", "website", "username"),
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=scrollbar_y.set,
            selectmode="browse",
        )
        scrollbar_y.config(command=self.tree.yview)

        # Define columns
        self.tree.heading("id", text="#")
        self.tree.heading("website", text="Website / Application")
        self.tree.heading("username", text="Username / Email")

        self.tree.column("id", width=40, minwidth=40, stretch=False)
        self.tree.column("website", width=300, minwidth=200)
        self.tree.column("username", width=300, minwidth=200)

        self.tree.pack(fill="both", expand=True)

        # ── Action buttons ──
        action_frame = createStyledFrame(self.frame, bg=COLORS["bg_dark"])
        action_frame.pack(fill="x", padx=20, pady=(0, 15))

        view_btn = createStyledButton(
            action_frame,
            text="👁 View",
            command=self._on_view,
            style="secondary",
            width=15,
        )
        view_btn.pack(side="left", padx=8)

        edit_btn = createStyledButton(
            action_frame,
            text="✏️ Edit",
            command=self._on_edit,
            style="primary",
            width=15,
        )
        edit_btn.pack(side="left", padx=8)

        delete_btn = createStyledButton(
            action_frame,
            text="🗑 Delete",
            command=self._on_delete,
            style="danger",
            width=15,
        )
        delete_btn.pack(side="left", padx=8)

        # ── Status label ──
        self.status_label = createStyledLabel(
            self.frame,
            text="",
            font_key="small",
            fg_key="text_secondary",
            bg=COLORS["bg_dark"],
        )
        self.status_label.pack(pady=(0, 5))

    def show(self, search_mode=False):
        """
        Show this screen.

        Args:
            search_mode: If True, focus the search field.
        """
        self._search_mode = search_mode
        if self.frame:
            self.frame.pack(fill="both", expand=True)
        self._load_entries()
        if search_mode:
            self.search_entry.focus_set()
        else:
            self.search_entry.delete(0, tk.END)

    def hide(self):
        """Hide this screen."""
        if self.frame:
            self.frame.pack_forget()

    def _load_entries(self, entries=None):
        """
        Load entries into the treeview.

        Args:
            entries: Optional list of entries to display. If None, loads all.
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        if entries is None:
            key = self.app.auth_manager.get_derived_key()
            user_id = self.app.auth_manager.current_user_id
            entries = self.app.vault_manager.get_all_entries(user_id, key)

        self._entries = entries

        # Populate treeview
        for i, entry in enumerate(entries, 1):
            self.tree.insert("", "end", values=(
                i,
                entry["website"],
                entry["username"],
            ))

        count = len(entries)
        self.status_label.config(text=f"Showing {count} credential(s)")

    def _get_selected_entry(self):
        """Get the currently selected entry from the treeview."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a credential first.")
            return None

        item = self.tree.item(selection[0])
        index = int(item["values"][0]) - 1  # Convert to 0-based index

        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None

    def _on_search(self):
        """Search credentials by website or username."""
        query = self.search_entry.get().strip()
        if not query:
            self._load_entries()
            return

        key = self.app.auth_manager.get_derived_key()
        user_id = self.app.auth_manager.current_user_id
        results = self.app.vault_manager.search_entries(user_id, key, query)
        self._load_entries(results)
        self.title_label.config(text=f"🔍 Search Results for '{query}'")

    def _on_clear_search(self):
        """Clear the search and show all entries."""
        self.search_entry.delete(0, tk.END)
        self.title_label.config(text="📋 My Credentials")
        self._load_entries()

    def _on_view(self):
        """View the selected credential details."""
        entry = self._get_selected_entry()
        if entry:
            self.hide()
            self.app.show_view_entry(entry)

    def _on_edit(self):
        """Edit the selected credential."""
        entry = self._get_selected_entry()
        if entry:
            self.hide()
            self.app.show_add_entry(entry_id=entry["id"])

    def _on_delete(self):
        """Delete the selected credential with confirmation."""
        entry = self._get_selected_entry()
        if not entry:
            return

        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the credential for\n"
            f"'{entry['website']}' ({entry['username']})?\n\n"
            f"This action cannot be undone."
        )

        if result:
            user_id = self.app.auth_manager.current_user_id
            success, message = self.app.vault_manager.delete_entry(entry["id"], user_id)
            if success:
                messagebox.showinfo("Deleted", message)
                self._load_entries()
            else:
                messagebox.showerror("Error", message)

    def _on_back(self):
        """Navigate back to the dashboard."""
        self.hide()
        self.app.show_dashboard()
