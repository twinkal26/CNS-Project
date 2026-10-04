# 🔐 SecureVault — Secure Password Manager

A professional, cryptographically secure password manager built with Python, demonstrating real **Cryptography and Network Security** concepts for a B.Tech CNS Mini Project.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Objectives](#objectives)
4. [Features](#features)
5. [Technologies Used](#technologies-used)
6. [Cryptography Concepts](#cryptography-concepts)
7. [System Architecture](#system-architecture)
8. [Database Design](#database-design)
9. [Project Structure](#project-structure)
10. [Installation](#installation)
11. [How to Run](#how-to-run)
12. [Usage](#usage)
13. [Screenshots](#screenshots)
14. [Testing](#testing)
15. [Limitations](#limitations)
16. [Future Scope](#future-scope)
17. [Conclusion](#conclusion)

---

## 📖 Project Overview

SecureVault is a locally-run password manager that encrypts all stored credentials using industry-standard cryptographic algorithms. It demonstrates core CNS concepts including symmetric encryption, key derivation, secure hashing, and authentication — all within a user-friendly Tkinter GUI.

**Key principle:** The master password is never stored. Only a PBKDF2-derived hash is kept for verification, and the actual AES encryption key exists only in memory while the user is logged in.

---

## ❗ Problem Statement

Storing passwords in plaintext — whether in text files, sticky notes, or browsers without encryption — exposes users to severe security risks:

- **Data breaches** can expose all stored credentials instantly
- **Malware** can read plaintext password files
- **Unauthorized access** becomes trivial if a device is compromised

A secure password manager encrypts all credentials using a master password-derived key, so even if the database file is stolen, the attacker cannot read the passwords without the master password.

---

## 🎯 Objectives

1. Create a secure account system with master password authentication
2. Encrypt all stored credentials using AES-256-GCM
3. Derive encryption keys using PBKDF2-HMAC-SHA256
4. Never store master passwords or vault passwords in plaintext
5. Generate cryptographically secure random passwords
6. Implement account lockout after failed login attempts
7. Provide a clean, professional GUI for ease of use
8. Demonstrate real CNS concepts suitable for a college project

---

## ✨ Features

- **User Authentication** — Account creation with PBKDF2 key derivation
- **AES-256-GCM Encryption** — Confidentiality, integrity, and authentication for all vault data
- **Secure Password Generation** — Using Python's `secrets` module (not `random`)
- **Password Strength Analysis** — Real-time strength feedback during password creation
- **CRUD Operations** — Add, view, edit, and delete credentials
- **Search** — Search credentials by website or username
- **Show/Hide Password** — Toggle password visibility
- **Copy to Clipboard** — Quick copy for passwords
- **Account Lockout** — Temporary lockout after 5 failed login attempts
- **Session Security** — Encryption key cleared from memory on logout
- **Input Validation** — All inputs validated before processing
- **Dark Themed UI** — Modern cybersecurity-themed interface

---

## 🛠 Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.11+ | Core language |
| Tkinter | GUI framework |
| SQLite | Local database |
| `cryptography` library | AES-256-GCM, PBKDF2-HMAC-SHA256 |
| `hashlib` | Hashing utilities |
| `secrets` | Cryptographically secure random generation |
| `os` | System-level operations |
| `base64` | Encoding encrypted data |

---

## 🔐 Cryptography Concepts

### Master Password Flow
```
Master Password → PBKDF2-HMAC-SHA256 (with random salt, 600K iterations)
                     ↓
              256-bit Derived Key
                     ↓
         Stored Hash (for verification only)
```

### Vault Encryption Flow
```
Credential Data → JSON Serialization → AES-256-GCM Encryption
                                          ↓
                                    Nonce (12 bytes, random)
                                    Ciphertext
                                    Authentication Tag
                                          ↓
                                    Base64-encoded string
                                          ↓
                                    SQLite Database
```

### Key Concepts Implemented

- **PBKDF2** — Password-Based Key Derivation Function 2. Slowly hashes the password with a salt thousands of times to resist brute-force attacks.
- **Salt** — A random value mixed into the password before hashing. Prevents rainbow table attacks by ensuring identical passwords produce different hashes.
- **AES-256-GCM** — Advanced Encryption Standard with Galois/Counter Mode. Provides both encryption (confidentiality) and authentication (integrity verification).
- **Nonce** — A unique random value used once per encryption. Ensures identical plaintexts produce different ciphertexts.
- **Authentication Tag** — A cryptographic checksum appended to the ciphertext. Detects any tampering with the encrypted data.

---

## 🏗 System Architecture

```
User
  ↓
Tkinter GUI (ui/)
  ↓
Authentication Layer (auth/authentication.py)
  ↓
Cryptography Layer (crypto/crypto_manager.py)
  ↓
Vault Manager (vault/vault_manager.py)
  ↓
SQLite Database (database/database.py)
```

Each layer has a single responsibility:
- **GUI Layer** — Handles user interaction and display
- **Auth Layer** — Manages registration, login, and session state
- **Crypto Layer** — Performs all encryption/decryption operations
- **Vault Layer** — Manages CRUD operations on encrypted data
- **Database Layer** — Handles SQLite queries and data persistence

---

## 🗄 Database Design

### `users` Table
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-incrementing user ID |
| username | TEXT (UNIQUE) | User-chosen username |
| password_hash | TEXT | PBKDF2-derived hash for verification |
| salt | TEXT (hex) | Random 16-byte salt |
| created_at | TIMESTAMP | Account creation time |
| failed_attempts | INTEGER | Counter for failed logins |
| locked_until | TIMESTAMP | Account lock expiry time |

### `vault_entries` Table
| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-incrementing entry ID |
| user_id | INTEGER (FK) | References users.id |
| encrypted_data | TEXT | AES-256-GCM encrypted JSON blob |
| created_at | TIMESTAMP | Entry creation time |
| updated_at | TIMESTAMP | Last modification time |

---

## 📁 Project Structure

```
SecureVault/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── .gitignore                 # Git ignore rules
│
├── database/
│   ├── __init__.py
│   └── database.py            # SQLite database operations
│
├── crypto/
│   ├── __init__.py
│   └── crypto_manager.py      # AES-256-GCM and PBKDF2
│
├── auth/
│   ├── __init__.py
│   └── authentication.py      # User authentication
│
├── vault/
│   ├── __init__.py
│   └── vault_manager.py       # Encrypted credential CRUD
│
├── security/
│   ├── __init__.py
│   └── password_security.py   # Password generation & strength
│
├── ui/
│   ├── __init__.py
│   ├── welcome.py             # Welcome/landing screen
│   ├── login.py               # Login screen
│   ├── register.py            # Registration screen
│   ├── dashboard.py           # Main dashboard
│   ├── add_entry.py           # Add/edit credential form
│   ├── credential_list.py     # Credential table view
│   ├── view_entry.py          # View credential details
│   └── password_generator.py  # Password generator tool
│
├── utils/
│   ├── __init__.py
│   └── helpers.py             # Colors, fonts, and utilities
│
├── data/
│   └── .gitkeep               # Database stored here (gitignored)
│
└── screenshots/
    └── .gitkeep               # Project screenshots
```

---

## 💻 Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/SecureVault.git
   cd SecureVault
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶ How to Run

```bash
python main.py
```

The application window will open with the Welcome screen.

---

## 📱 Usage

### 1. Create an Account
- Click "Create Account" on the Welcome screen
- Enter a username and a strong master password
- The password strength indicator will help you choose a secure password
- Click "Create Account"

### 2. Log In
- Enter your username and master password
- Click "Login"
- After 5 failed attempts, the account is locked for 15 minutes

### 3. Add a Credential
- Click "Add Credential" on the Dashboard
- Fill in the website, username, password, and optional notes
- Use the "Generate Password" button for a strong random password
- Click "Save Credential"

### 4. View Credentials
- Click "View Credentials" on the Dashboard
- See all saved entries in a table (passwords hidden)
- Click "View" to see full details

### 5. Search
- Click "Search" on the Dashboard
- Type a website name or username
- Results appear dynamically

### 6. Edit / Delete
- Select an entry and click "Edit" or "Delete"
- Edits are re-encrypted before saving
- Deletions require confirmation

### 7. Password Generator
- Click "Password Generator" on the Dashboard
- Adjust length and character options
- Click "Generate" and copy or use the result

### 8. Logout
- Click "Logout" on the Dashboard
- All session data (including the AES key) is cleared from memory

---

## 📸 Screenshots

> *(Add screenshots of each screen here during your demonstration)*

---

## 🧪 Testing

| Test Case | Expected Result | Status |
|---|---|---|
| Valid registration | Account created successfully | ✅ |
| Duplicate registration | "Username already exists" error | ✅ |
| Weak master password | Rejected with feedback | ✅ |
| Password mismatch | "Passwords do not match" error | ✅ |
| Valid login | Dashboard displayed | ✅ |
| Invalid login | Error message with attempt count | ✅ |
| Account lockout (5 failures) | Locked for 15 minutes | ✅ |
| Add credential | Saved and encrypted | ✅ |
| Edit credential | Updated and re-encrypted | ✅ |
| Delete credential | Removed after confirmation | ✅ |
| Search credential | Results filtered correctly | ✅ |
| Password generation | Secure random password created | ✅ |
| Invalid input handling | Friendly error messages | ✅ |
| Logout | Session cleared, key destroyed | ✅ |
| Data persistence | Data survives app restart | ✅ |
| Database contains no plaintext | Passwords are encrypted blobs | ✅ |

---

## ⚠ Limitations

1. **Single-user per database** — Only one user account can exist per database file
2. **No cloud sync** — Data is stored locally only
3. **No import/export** — Cannot import from other password managers
4. **Search requires full decrypt** — All entries must be decrypted to search (trade-off of client-side encryption)
5. **Memory-based key** — The AES key exists only in RAM; if the process is killed, the key is lost (which is actually a security feature)
6. **No two-factor authentication** — Only single-factor (master password) authentication

---

## 🔮 Future Scope

1. **Multi-user support** — Multiple user accounts with separate vaults
2. **Cloud synchronization** — Encrypted vault sync across devices
3. **Import/Export** — CSV/JSON import from other password managers
4. **Two-factor authentication** — TOTP or hardware key support
5. **Browser extension** — Auto-fill passwords in web browsers
6. **Clipboard auto-clear** — Automatically clear clipboard after copying
7. **Password breach checking** — Integration with Have I Been Pwned API
8. **Biometric authentication** — Fingerprint/face recognition support
9. **Encrypted file attachments** — Store encrypted notes and files
10. **Audit logging** — Detailed security event logging

---

## 🎓 Conclusion

SecureVault demonstrates practical application of cryptography and network security concepts in a real-world project. By implementing PBKDF2 for key derivation, AES-256-GCM for encryption, and proper session management, the project shows how modern security principles protect user data at rest and in transit (within the application).

The project is suitable for a B.Tech CNS mini-project as it covers:
- Symmetric encryption (AES)
- Key derivation (PBKDF2)
- Hashing and salting
- Authentication and authorization
- Secure random number generation
- Data integrity verification (GCM authentication tag)

---

## 📚 References

1. [NIST SP 800-132](https://csrc.nist.gov/publications/detail/sp/800-132/final) — PBKDF2
2. [NIST FIPS 197](https://csrc.nist.gov/publications/detail/fips/197/final) — AES
3. [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
4. [Python `secrets` module](https://docs.python.org/3/library/secrets.html)
5. [Python `cryptography` library](https://cryptography.io/en/latest/)

---

## 📄 License

This project is for educational purposes as part of a B.Tech CNS Mini Project.
