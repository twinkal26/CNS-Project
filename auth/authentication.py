"""
Authentication module for SecureVault.

Handles user registration, login, and session management.
The master password is verified using PBKDF2-HMAC-SHA256.
Failed login attempts are tracked, and accounts are temporarily
locked after 5 consecutive failures.
"""

from database.database import DatabaseManager
from crypto.crypto_manager import (
    generate_salt,
    derive_key,
    hash_master_password,
)


class AuthenticationManager:
    """
    Manages user authentication including registration, login,
    account locking, and session state.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the authentication manager.

        Args:
            db_manager: An instance of DatabaseManager.
        """
        self.db = db_manager
        self.current_user_id = None
        self.current_username = None
        self.derived_key = None  # AES key, lives only in memory

    def register(self, username: str, master_password: str) -> tuple:
        """
        Register a new user account.

        Steps:
        1. Validate inputs.
        2. Check if username already exists.
        3. Generate a random salt.
        4. Derive the key using PBKDF2-HMAC-SHA256.
        5. Store the username, derived hash, and salt — never the password.

        Args:
            username: The desired username.
            master_password: The master password (processed in memory only).

        Returns:
            Tuple of (success: bool, message: str).
        """
        # ── Input validation ──
        if not username or not username.strip():
            return False, "Username cannot be empty."

        if len(username.strip()) < 3:
            return False, "Username must be at least 3 characters."

        if len(username.strip()) > 50:
            return False, "Username must be at most 50 characters."

        if not master_password:
            return False, "Master password cannot be empty."

        if len(master_password) < 8:
            return False, "Master password must be at least 8 characters."

        username = username.strip()

        # ── Check for duplicate username ──
        existing_user = self.db.get_user(username)
        if existing_user:
            return False, "Username already exists. Please choose another."

        # ── Generate salt and derive key ──
        salt = generate_salt()
        password_hash = hash_master_password(master_password, salt)

        # Convert salt to hex for storage
        salt_hex = salt.hex()

        # ── Store user in database ──
        user_id = self.db.create_user(username, password_hash, salt_hex)
        if user_id is None:
            return False, "Failed to create account. Please try again."

        return True, "Account created successfully! You can now log in."

    def login(self, username: str, master_password: str) -> tuple:
        """
        Authenticate an existing user.

        Steps:
        1. Retrieve the user record by username.
        2. Check if the account is locked.
        3. Derive the key from the entered password using the stored salt.
        4. Compare the derived hash with the stored hash.
        5. On success: store the derived key in memory, reset failed attempts.
        6. On failure: increment failed attempts, potentially lock account.

        Args:
            username: The username.
            master_password: The master password attempt.

        Returns:
            Tuple of (success: bool, message: str).
        """
        if not username or not master_password:
            return False, "Username and password are required."

        # ── Look up user ──
        user = self.db.get_user(username.strip())
        if not user:
            return False, "Invalid username or password."

        user_id = user["id"]

        # ── Check account lockout ──
        if self.db.is_account_locked(user_id):
            return False, (
                "Account is temporarily locked due to too many failed attempts. "
                "Please try again in 15 minutes."
            )

        # ── Verify password ──
        salt = bytes.fromhex(user["salt"])
        entered_hash = hash_master_password(master_password, salt)

        if entered_hash != user["password_hash"]:
            self.db.increment_failed_attempts(user_id)
            # Check remaining attempts
            updated_user = self.db.get_user(username.strip())
            attempts_left = max(0, 5 - updated_user["failed_attempts"])
            if attempts_left > 0:
                return False, f"Invalid username or password. {attempts_left} attempt(s) remaining."
            else:
                return False, "Account locked due to too many failed attempts. Try again in 15 minutes."

        # ── Login successful ──
        self.db.reset_failed_attempts(user_id)
        self.current_user_id = user_id
        self.current_username = username.strip()

        # Derive the AES encryption key and keep it in memory only.
        # This key is used to encrypt/decrypt vault entries while the
        # user is logged in. It is NEVER written to disk.
        self.derived_key = derive_key(master_password, salt)

        return True, f"Welcome back, {username.strip()}!"

    def logout(self):
        """
        Clear all sensitive session data from memory.

        This is important for security — after logout, the derived AES key
        should not be accessible in memory.
        """
        self.current_user_id = None
        self.current_username = None
        # Overwrite the derived key reference. Note: Python's garbage collector
        # will handle the actual memory, but clearing the reference prevents
        # accidental reuse.
        if self.derived_key:
            # Write zeros over the key bytes before discarding
            self.derived_key = b'\x00' * len(self.derived_key)
        self.derived_key = None

    def is_authenticated(self) -> bool:
        """Check if a user is currently logged in."""
        return self.current_user_id is not None and self.derived_key is not None

    def get_derived_key(self) -> bytes:
        """
        Get the current derived AES key.

        Returns:
            The 256-bit AES key, or None if not authenticated.
        """
        return self.derived_key
