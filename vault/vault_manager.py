"""
Vault Manager module for SecureVault.

Handles CRUD operations on encrypted credentials:
- Add new credentials (encrypt before storing)
- View credentials (decrypt on read)
- Edit credentials (re-encrypt updated data)
- Delete credentials
- Search credentials (by website or username — searching decrypts all entries
  to match, but passwords are never displayed during search)
"""

import json
from database.database import DatabaseManager
from crypto.crypto_manager import encrypt_json, decrypt_json


class VaultManager:
    """
    Manages encrypted vault entries for the currently authenticated user.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the vault manager.

        Args:
            db_manager: An instance of DatabaseManager.
        """
        self.db = db_manager

    def add_entry(self, user_id: int, encryption_key: bytes,
                  website: str, username: str, password: str,
                  notes: str = "") -> tuple:
        """
        Add a new encrypted credential entry to the vault.

        The website, username, password, and notes are bundled into a
        dictionary, encrypted with AES-256-GCM, and stored as a single
        blob in the database. No plaintext ever touches the database.

        Args:
            user_id: The authenticated user's ID.
            encryption_key: The AES-256 key (derived from PBKDF2).
            website: The website or application name.
            username: The username/email for the credential.
            password: The password for the credential.
            notes: Optional notes.

        Returns:
            Tuple of (success: bool, message: str).
        """
        # ── Input validation ──
        if not website or not website.strip():
            return False, "Website/Application name is required."

        if not username or not username.strip():
            return False, "Username/Email is required."

        if not password:
            return False, "Password is required."

        # ── Build credential dict ──
        credential_data = {
            "website": website.strip(),
            "username": username.strip(),
            "password": password,
            "notes": notes.strip() if notes else "",
        }

        # ── Encrypt and store ──
        try:
            encrypted_data = encrypt_json(encryption_key, credential_data)
            entry_id = self.db.add_vault_entry(user_id, encrypted_data)
            if entry_id:
                return True, "Credential saved successfully!"
            return False, "Failed to save credential."
        except Exception as e:
            return False, f"Encryption error: {str(e)}"

    def get_all_entries(self, user_id: int, encryption_key: bytes) -> list:
        """
        Retrieve and decrypt all vault entries for the user.

        Returns:
            A list of dicts with 'id', 'website', 'username', 'created_at',
            'updated_at', and decrypted data. Passwords are included internally
            but the UI should not display them in the list view.
        """
        raw_entries = self.db.get_vault_entries(user_id)
        decrypted_entries = []

        for entry in raw_entries:
            try:
                data = decrypt_json(encryption_key, entry["encrypted_data"])
                decrypted_entries.append({
                    "id": entry["id"],
                    "website": data.get("website", ""),
                    "username": data.get("username", ""),
                    "password": data.get("password", ""),
                    "notes": data.get("notes", ""),
                    "created_at": entry["created_at"],
                    "updated_at": entry["updated_at"],
                })
            except Exception:
                # Skip entries that cannot be decrypted (corrupted data)
                continue

        return decrypted_entries

    def get_entry(self, entry_id: int, user_id: int,
                  encryption_key: bytes) -> tuple:
        """
        Retrieve and decrypt a single vault entry.

        Args:
            entry_id: The vault entry ID.
            user_id: The authenticated user's ID.
            encryption_key: The AES-256 key.

        Returns:
            Tuple of (entry_dict or None, error_message or None).
        """
        entry = self.db.get_vault_entry(entry_id, user_id)
        if not entry:
            return None, "Credential not found."

        try:
            data = decrypt_json(encryption_key, entry["encrypted_data"])
            return {
                "id": entry["id"],
                "website": data.get("website", ""),
                "username": data.get("username", ""),
                "password": data.get("password", ""),
                "notes": data.get("notes", ""),
                "created_at": entry["created_at"],
                "updated_at": entry["updated_at"],
            }, None
        except Exception as e:
            return None, f"Failed to decrypt credential: {str(e)}"

    def update_entry(self, entry_id: int, user_id: int,
                     encryption_key: bytes, website: str,
                     username: str, password: str,
                     notes: str = "") -> tuple:
        """
        Update an existing vault entry with new (or unchanged) data.

        The data is re-encrypted before being stored, because AES-GCM
        requires a fresh nonce for each encryption — you cannot simply
        edit the encrypted blob.

        Args:
            entry_id: The vault entry ID to update.
            user_id: The authenticated user's ID.
            encryption_key: The AES-256 key.
            website: Updated website name.
            username: Updated username/email.
            password: Updated password.
            notes: Updated notes.

        Returns:
            Tuple of (success: bool, message: str).
        """
        # ── Input validation ──
        if not website or not website.strip():
            return False, "Website/Application name is required."

        if not username or not username.strip():
            return False, "Username/Email is required."

        if not password:
            return False, "Password is required."

        credential_data = {
            "website": website.strip(),
            "username": username.strip(),
            "password": password,
            "notes": notes.strip() if notes else "",
        }

        try:
            encrypted_data = encrypt_json(encryption_key, credential_data)
            success = self.db.update_vault_entry(entry_id, user_id, encrypted_data)
            if success:
                return True, "Credential updated successfully!"
            return False, "Credential not found."
        except Exception as e:
            return False, f"Encryption error: {str(e)}"

    def delete_entry(self, entry_id: int, user_id: int) -> tuple:
        """
        Delete a vault entry.

        Args:
            entry_id: The vault entry ID to delete.
            user_id: The authenticated user's ID.

        Returns:
            Tuple of (success: bool, message: str).
        """
        success = self.db.delete_vault_entry(entry_id, user_id)
        if success:
            return True, "Credential deleted successfully!"
        return False, "Credential not found."

    def search_entries(self, user_id: int, encryption_key: bytes,
                       query: str) -> list:
        """
        Search vault entries by website name or username.

        Because all data is encrypted, we must decrypt every entry to
        search through it. This is a known trade-off of client-side
        encryption — searching requires decrypting all entries first.

        Passwords are returned in the results but the UI must NOT
        display them in the search results list.

        Args:
            user_id: The authenticated user's ID.
            encryption_key: The AES-256 key.
            query: The search term.

        Returns:
            A list of matching decrypted entries.
        """
        if not query or not query.strip():
            return []

        query_lower = query.strip().lower()
        all_entries = self.get_all_entries(user_id, encryption_key)

        results = []
        for entry in all_entries:
            if (query_lower in entry["website"].lower() or
                    query_lower in entry["username"].lower()):
                results.append(entry)

        return results

    def get_entry_count(self, user_id: int) -> int:
        """Get the total number of vault entries for the user."""
        return self.db.get_vault_entry_count(user_id)
