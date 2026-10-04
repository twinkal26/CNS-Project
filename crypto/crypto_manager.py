"""
Cryptography module for SecureVault.

Implements:
- PBKDF2-HMAC-SHA256 for master password hashing / key derivation
- AES-256-GCM for encrypting and decrypting vault data

Security principles enforced here:
- The master password is NEVER stored. Only the derived hash and random salt are kept.
- Every AES-GCM operation uses a fresh random 12-byte nonce.
- The derived key lives only in memory and is never written to disk.
"""

import os
import base64
import hashlib
import secrets
import json

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# ── Constants ────────────────────────────────────────────────────────

# PBKDF2 iteration count — higher is slower but more resistant to brute-force.
# 600,000 is the current OWASP recommendation for PBKDF2-HMAC-SHA256.
PBKDF2_ITERATIONS = 600_000

# Key length for AES-256
KEY_LENGTH = 32  # 256 bits

# Salt length — 16 bytes gives 128 bits of entropy, more than enough.
SALT_LENGTH = 16

# AES-GCM nonce length — 12 bytes (96 bits) is the standard recommended size.
NONCE_LENGTH = 12


# ── Salt Generation ─────────────────────────────────────────────────

def generate_salt() -> bytes:
    """
    Generate a cryptographically secure random salt.

    WHY A SALT?
    ───────────
    A salt is a random value mixed into the password before hashing. It ensures
    that even if two users choose the same master password, their stored hashes
    are completely different. Without a salt, an attacker could use a precomputed
    "rainbow table" to reverse common passwords instantly. A random salt forces
    the attacker to re-compute every guess for every single user, making
    dictionary and brute-force attacks orders of magnitude harder.
    """
    return os.urandom(SALT_LENGTH)


# ── Key Derivation ──────────────────────────────────────────────────

def derive_key(master_password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit AES key from the master password using PBKDF2-HMAC-SHA256.

    PBKDF2 (Password-Based Key Derivation Function 2) repeatedly hashes the
    password+salt combination many times (PBKDF2_ITERATIONS). This deliberate
    slowness makes brute-force attacks impractical — each guess an attacker
    tries costs the same computational effort as a legitimate login.

    Args:
        master_password: The user's master password (plaintext, in memory only).
        salt: The random salt (bytes) stored alongside the user record.

    Returns:
        A 32-byte (256-bit) derived key suitable for AES-256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(master_password.encode("utf-8"))


def hash_master_password(master_password: str, salt: bytes) -> str:
    """
    Derive a key and return it as a hex string for storage/verification.

    We store this hash in the database so we can verify the master password
    at login time without ever storing the password itself. The stored hash
    is NOT an AES key — it is the PBKDF2 output used purely for verification.

    Args:
        master_password: The user's master password.
        salt: The random salt.

    Returns:
        Hex-encoded derived key string.
    """
    key = derive_key(master_password, salt)
    return key.hex()


# ── AES-256-GCM Encryption / Decryption ─────────────────────────────

def encrypt_data(key: bytes, plaintext: str) -> str:
    """
    Encrypt a plaintext string using AES-256-GCM.

    AES-GCM (Galois/Counter Mode) provides:
      - Confidentiality: the data cannot be read without the key.
      - Integrity: any tampering with the ciphertext is detected.
      - Authentication: the receiver can verify the ciphertext was created
        by someone who holds the key.

    Each call generates a fresh random 12-byte nonce. The nonce is NOT secret —
    it is stored alongside the ciphertext. What makes AES-GCM secure is that
    the same nonce must NEVER be reused with the same key. Because we generate
    a random nonce every time, the probability of collision is negligible.

    The output format is: base64( nonce || ciphertext || tag )
    The 16-byte authentication tag is appended automatically by AESGCM.

    Args:
        key: The 256-bit AES key (from PBKDF2 derivation).
        plaintext: The string to encrypt.

    Returns:
        A base64-encoded string containing nonce + ciphertext + auth tag.
    """
    nonce = os.urandom(NONCE_LENGTH)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    # Pack nonce + ciphertext (which includes the auth tag) together
    packed = nonce + ciphertext
    return base64.b64encode(packed).decode("utf-8")


def decrypt_data(key: bytes, encrypted_b64: str) -> str:
    """
    Decrypt a base64-encoded AES-256-GCM ciphertext.

    If the data has been tampered with or the wrong key is used, the
    authentication tag verification will fail and raise an exception.

    Args:
        key: The 256-bit AES key.
        encrypted_b64: The base64-encoded packed (nonce + ciphertext + tag).

    Returns:
        The decrypted plaintext string.

    Raises:
        Exception: If decryption fails (wrong key, corrupted data, etc.).
    """
    packed = base64.b64decode(encrypted_b64.encode("utf-8"))
    nonce = packed[:NONCE_LENGTH]
    ciphertext = packed[NONCE_LENGTH:]

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")


def encrypt_json(key: bytes, data: dict) -> str:
    """
    Encrypt a Python dictionary by first serializing it to JSON.

    Args:
        key: The 256-bit AES key.
        data: The dictionary to encrypt.

    Returns:
        A base64-encoded encrypted string.
    """
    json_str = json.dumps(data, ensure_ascii=False)
    return encrypt_data(key, json_str)


def decrypt_json(key: bytes, encrypted_b64: str) -> dict:
    """
    Decrypt and deserialize a JSON dictionary.

    Args:
        key: The 256-bit AES key.
        encrypted_b64: The encrypted JSON string.

    Returns:
        The decrypted dictionary.

    Raises:
        Exception: If decryption or JSON parsing fails.
    """
    json_str = decrypt_data(key, encrypted_b64)
    return json.loads(json_str)
