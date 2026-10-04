"""
Database module for SecureVault.
Handles all SQLite database operations including creating tables,
inserting, updating, and querying data.
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database connections and operations for SecureVault."""

    def __init__(self, db_path=None):
        """
        Initialize the database manager.

        Args:
            db_path: Path to the SQLite database file. Defaults to data/securevault.db
        """
        if db_path is None:
            # Place the database in the data/ directory
            base_dir = Path(__file__).resolve().parent.parent
            db_path = base_dir / "data" / "securevault.db"
        
        self.db_path = str(db_path)
        self.connection = None
        self._create_tables()

    def _connect(self):
        """Create a new database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection

    def _close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def _create_tables(self):
        """Create the users and vault_entries tables if they don't exist."""
        conn = self._connect()
        try:
            cursor = conn.cursor()

            # Users table: stores user accounts with hashed master passwords
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP DEFAULT NULL
                )
            ''')

            # Vault entries table: stores encrypted credential data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vault_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    encrypted_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

            conn.commit()
        finally:
            self._close()

    # ── User Operations ──────────────────────────────────────────────

    def create_user(self, username, password_hash, salt):
        """
        Register a new user.

        Args:
            username: The desired username.
            password_hash: The PBKDF2-derived hash of the master password.
            salt: The random salt used during key derivation.

        Returns:
            The new user's ID, or None if the username already exists.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Username already exists
            return None
        finally:
            self._close()

    def get_user(self, username):
        """
        Retrieve a user by username.

        Returns:
            A sqlite3.Row object or None if not found.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            return cursor.fetchone()
        finally:
            self._close()

    def get_user_by_id(self, user_id):
        """
        Retrieve a user by ID.

        Returns:
            A sqlite3.Row object or None if not found.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()
        finally:
            self._close()

    def increment_failed_attempts(self, user_id):
        """
        Increment the failed login attempt counter for a user.

        After 5 consecutive failed attempts, lock the account for 15 minutes.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET failed_attempts = failed_attempts + 1 WHERE id = ?",
                (user_id,)
            )
            conn.commit()

            # Check if we should lock the account (5 failed attempts)
            cursor.execute(
                "SELECT failed_attempts FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row and row["failed_attempts"] >= 5:
                lock_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Lock for 15 minutes from now
                from datetime import timedelta
                unlock_time = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "UPDATE users SET locked_until = ? WHERE id = ?",
                    (unlock_time, user_id)
                )
                conn.commit()
        finally:
            self._close()

    def reset_failed_attempts(self, user_id):
        """Reset the failed login attempt counter after a successful login."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?",
                (user_id,)
            )
            conn.commit()
        finally:
            self._close()

    def is_account_locked(self, user_id):
        """
        Check if an account is currently locked due to failed attempts.

        Returns:
            True if locked, False otherwise. Automatically unlocks if lock period expired.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT locked_until FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if not row or row["locked_until"] is None:
                return False

            locked_until = datetime.strptime(row["locked_until"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() >= locked_until:
                # Lock period expired, unlock the account
                cursor.execute(
                    "UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?",
                    (user_id,)
                )
                conn.commit()
                return False
            return True
        finally:
            self._close()

    # ── Vault Operations ─────────────────────────────────────────────

    def add_vault_entry(self, user_id, encrypted_data):
        """
        Add an encrypted vault entry for a user.

        Args:
            user_id: The user's ID.
            encrypted_data: The AES-GCM encrypted JSON string.

        Returns:
            The new entry's ID.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO vault_entries (user_id, encrypted_data) VALUES (?, ?)",
                (user_id, encrypted_data)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            self._close()

    def get_vault_entries(self, user_id):
        """
        Retrieve all vault entries for a user.

        Returns:
            A list of sqlite3.Row objects.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM vault_entries WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,)
            )
            return cursor.fetchall()
        finally:
            self._close()

    def get_vault_entry(self, entry_id, user_id):
        """
        Retrieve a single vault entry by ID, ensuring it belongs to the user.

        Returns:
            A sqlite3.Row object or None.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM vault_entries WHERE id = ? AND user_id = ?",
                (entry_id, user_id)
            )
            return cursor.fetchone()
        finally:
            self._close()

    def update_vault_entry(self, entry_id, user_id, encrypted_data):
        """
        Update an existing vault entry with new encrypted data.

        Returns:
            True if the update succeeded, False if the entry wasn't found.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE vault_entries SET encrypted_data = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = ? AND user_id = ?",
                (encrypted_data, entry_id, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            self._close()

    def delete_vault_entry(self, entry_id, user_id):
        """
        Delete a vault entry.

        Returns:
            True if the delete succeeded, False if the entry wasn't found.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM vault_entries WHERE id = ? AND user_id = ?",
                (entry_id, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            self._close()

    def get_vault_entry_count(self, user_id):
        """
        Count the number of vault entries for a user.

        Returns:
            The count as an integer.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM vault_entries WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return row["count"] if row else 0
        finally:
            self._close()
