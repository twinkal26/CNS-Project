# 🔐 SecureVault — Project Documentation

## CNS Mini Project: Cryptography & Network Security

---

## 1. Introduction

Password management is one of the most critical aspects of digital security. Studies consistently show that users reuse passwords across multiple services, store them in plaintext, or use weak, easily guessable combinations. This creates a single point of failure — if one service is compromised, all accounts using the same password become vulnerable.

SecureVault addresses this problem by providing a local, encrypted password manager that:
- Never stores passwords in plaintext
- Uses industry-standard encryption (AES-256-GCM)
- Derives encryption keys from the master password using PBKDF2
- Provides a clean, user-friendly interface

---

## 2. Problem Statement

**The Problem:** Users store passwords in unsafe locations (text files, sticky notes, browsers without encryption). When a device is compromised or a file is accessed by an unauthorized person, all stored credentials are exposed in plaintext.

**The Risk:**
- Identity theft
- Financial loss
- Privacy invasion
- Account compromise across multiple services (due to password reuse)

**Our Solution:** A password manager that encrypts all credentials using AES-256-GCM, with the encryption key derived from the master password using PBKDF2-HMAC-SHA256. Even if the database file is stolen, the attacker cannot read any passwords without knowing the master password.

---

## 3. Objectives

1. Build a secure password manager with a professional GUI
2. Implement AES-256-GCM encryption for vault data
3. Implement PBKDF2-HMAC-SHA256 for master password hashing
4. Never store plaintext passwords (master or vault)
5. Generate cryptographically secure random passwords
6. Implement account lockout after failed login attempts
7. Demonstrate real CNS concepts in a practical application

---

## 4. Methodology

### Overall Flow

```
User enters master password
         ↓
    PBKDF2-HMAC-SHA256
    (with random salt, 600,000 iterations)
         ↓
    256-bit Derived Key
         ↓
  ┌──────┴──────┐
  ↓              ↓
Verification   AES-256-GCM
(hash compare)  Encryption/Decryption
  ↓              ↓
Login         Vault Data
Success       (stored in SQLite)
```

### Registration Flow
1. User chooses a username and master password
2. A random 16-byte salt is generated
3. PBKDF2 derives a 256-bit key from the password + salt
4. The derived hash and salt are stored in the database
5. The master password is immediately discarded from memory

### Login Flow
1. User enters username and master password
2. The system retrieves the stored salt for that username
3. PBKDF2 re-derives the key from the entered password + stored salt
4. The derived hash is compared with the stored hash
5. On match: the AES key is kept in memory for the session
6. On mismatch: failed attempt counter is incremented

### Encryption Flow
1. User enters credential data (website, username, password, notes)
2. Data is serialized to JSON
3. A fresh random 12-byte nonce is generated
4. AES-256-GCM encrypts the JSON with the derived key and nonce
5. The result (nonce + ciphertext + auth tag) is base64-encoded
6. The encoded string is stored in SQLite

---

## 5. Cryptography Explanation

### 5.1 Hashing

**What is hashing?**
Hashing is the process of converting data (like a password) into a fixed-size string of characters using a mathematical function. The output (hash) is deterministic — the same input always produces the same hash — but it is practically impossible to reverse the process to recover the original input.

**Example:**
```
Input:  "mypassword"
SHA-256: 8b3e7c4d... (64 hex characters)
```

**Properties:**
- One-way function (cannot be reversed)
- Deterministic (same input → same output)
- Fixed output size regardless of input size
- Avalanche effect (small input change → completely different output)

### 5.2 Salting

**What is a salt?**
A salt is a random value that is added to the password before hashing. Each user gets a unique salt, which is stored alongside the hash.

**Why is a salt required?**
Without a salt, two users with the same password would have the same hash. An attacker could precompute hashes for common passwords (rainbow table attack). A random salt forces the attacker to recompute every guess for every individual user, making precomputed attacks useless.

**In SecureVault:**
- Salt is 16 bytes (128 bits) of cryptographic randomness
- Generated using `os.urandom()`
- Stored in the database alongside the hash
- Never reused across users

### 5.3 PBKDF2

**What is PBKDF2?**
PBKDF2 (Password-Based Key Derivation Function 2) is a key derivation function that applies a pseudorandom function (like HMAC-SHA256) to the input password along with a salt, and repeats the process many times (iterations).

**Why PBKDF2?**
- It's slow by design — each guess takes the same time as a legitimate login
- This makes brute-force attacks computationally expensive
- OWASP recommends 600,000 iterations for PBKDF2-HMAC-SHA256

**In SecureVault:**
- Algorithm: PBKDF2-HMAC-SHA256
- Iterations: 600,000
- Output length: 256 bits (32 bytes)
- Salt: 16 random bytes

### 5.4 AES (Advanced Encryption Standard)

**What is AES?**
AES is a symmetric block cipher adopted by the U.S. government to protect classified information. It operates on fixed-size blocks of data (128 bits) using keys of 128, 192, or 256 bits.

**Why AES?**
- It is the most widely used encryption algorithm worldwide
- It has been extensively analyzed by cryptographers for over 20 years
- No practical attacks exist against AES-256
- It is fast and efficient in both hardware and software

**In SecureVault:**
- We use AES-256 (256-bit key)
- Mode: GCM (Galois/Counter Mode)

### 5.5 GCM (Galois/Counter Mode)

**What is GCM?**
GCM is a mode of operation for block ciphers that provides both encryption (confidentiality) and authentication (integrity). It combines Counter Mode (CTR) encryption with GHASH authentication.

**Why GCM?**
- Provides **confidentiality** (data is unreadable without the key)
- Provides **integrity** (any tampering is detected)
- Provides **authentication** (the receiver knows the data came from someone with the key)
- It is a single-pass authenticated encryption mode (efficient)

### 5.6 Nonce

**What is a nonce?**
A nonce (Number used ONCE) is a random value that is used only once in an encryption operation. It ensures that encrypting the same plaintext twice with the same key produces different ciphertexts.

**In SecureVault:**
- Nonce is 12 bytes (96 bits) — the recommended size for AES-GCM
- Generated using `os.urandom()` (cryptographically secure)
- A fresh nonce is generated for every encryption operation
- The nonce is stored alongside the ciphertext (it is not secret)

**Critical rule:** Never reuse a nonce with the same key. SecureVault guarantees this by generating a new random nonce for each encryption.

### 5.7 Authentication Tag

**What is an authentication tag?**
An authentication tag (or MAC) is a cryptographic checksum appended to the ciphertext. It allows the receiver to verify that:
1. The data was created by someone who holds the encryption key
2. The data has not been modified since it was encrypted

**In SecureVault:**
- AES-GCM automatically generates a 16-byte (128-bit) authentication tag
- The tag is included in the encrypted output
- During decryption, the tag is verified first — if it doesn't match, decryption fails and an error is raised
- This prevents tampering with encrypted vault entries

### 5.8 Confidentiality vs Integrity

| Property | Meaning | Mechanism |
|---|---|---|
| Confidentiality | Data cannot be read without the key | AES encryption |
| Integrity | Data has not been modified | GCM authentication tag |
| Authentication | Data was created by a key holder | GCM authentication tag |

SecureVault provides all three through AES-256-GCM.

---

## 6. System Architecture

```
┌─────────────────────────────────────┐
│            User                     │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│     Tkinter GUI (ui/)               │
│  Welcome, Login, Register,          │
│  Dashboard, Add Entry,              │
│  Credential List, View,             │
│  Password Generator                 │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Authentication Layer              │
│   (auth/authentication.py)          │
│   - Registration                    │
│   - Login verification              │
│   - Session management              │
│   - Account lockout                 │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Cryptography Layer                │
│   (crypto/crypto_manager.py)        │
│   - PBKDF2 key derivation           │
│   - AES-256-GCM encrypt/decrypt     │
│   - Salt generation                 │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Vault Manager                     │
│   (vault/vault_manager.py)          │
│   - Add/Edit/Delete credentials     │
│   - Search                          │
│   - Decrypt on read                 │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   SQLite Database                   │
│   (database/database.py)            │
│   - users table                     │
│   - vault_entries table             │
│   - securevault.db                  │
└─────────────────────────────────────┘
```

### Role of Each Layer

1. **GUI Layer** — Presents the user interface, collects input, and displays results. Does not perform any cryptographic operations directly.

2. **Authentication Layer** — Manages user accounts, verifies credentials using PBKDF2, and maintains session state (current user, derived key). Handles account lockout after failed attempts.

3. **Cryptography Layer** — Performs all encryption/decryption using AES-256-GCM and key derivation using PBKDF2-HMAC-SHA256. This is the core security module.

4. **Vault Manager** — Acts as the bridge between the UI and the crypto/database layers. It encrypts data before saving and decrypts when reading.

5. **Database Layer** — Handles all SQLite operations. Stores encrypted blobs and user metadata. Never sees plaintext passwords.

---

## 7. Security Mechanisms

| Mechanism | Implementation | Purpose |
|---|---|---|
| Master password hashing | PBKDF2-HMAC-SHA256 (600K iterations) | Prevent brute-force attacks |
| Salt | 16-byte random salt per user | Prevent rainbow table attacks |
| Vault encryption | AES-256-GCM | Confidentiality + Integrity |
| Fresh nonce | 12-byte random per encryption | Prevent nonce reuse attacks |
| Session key in memory only | Never written to disk | Protect key if file is stolen |
| Account lockout | 5 failures → 15 min lock | Prevent brute-force login |
| Input validation | All fields validated | Prevent injection/errors |
| Secure random | `secrets` module | Cryptographically secure randomness |
| Session logout | Key zeroed and discarded | Clear sensitive data |

---

## 8. CNS Viva Questions and Answers

### Q1: Why did you use AES?
**A:** AES (Advanced Encryption Standard) is the most widely adopted symmetric encryption algorithm globally. It has been analyzed by cryptographers for over 20 years with no practical attacks found. It is fast, efficient, and standardized by NIST.

### Q2: Why AES-256-GCM?
**A:** AES-256 provides a 256-bit key space, making brute-force attacks computationally infeasible (2^256 possible keys). GCM (Galois/Counter Mode) provides authenticated encryption — it not only encrypts the data (confidentiality) but also generates an authentication tag that detects any tampering (integrity + authentication).

### Q3: Why PBKDF2?
**A:** PBKDF2 (Password-Based Key Derivation Function 2) is designed to be deliberately slow. By iterating the hash function 600,000 times, each password guess by an attacker takes the same time as a legitimate login. This makes brute-force attacks extremely slow and impractical.

### Q4: What is a salt?
**A:** A salt is a random value mixed into the password before hashing. It ensures that two users with the same password get different hashes. Without a salt, an attacker could precompute a table of hashes for common passwords (rainbow table). A unique salt per user defeats this attack.

### Q5: Why is the master password not stored?
**A:** If the master password were stored, anyone who gains access to the database could read it directly. Instead, we store only the PBKDF2-derived hash. At login, we re-derive the hash from the entered password and compare it. The actual password is never stored anywhere.

### Q6: What is hashing?
**A:** Hashing is a one-way mathematical function that converts input data into a fixed-size output string. It is deterministic (same input → same output) but practically irreversible. Common algorithms include SHA-256, SHA-3, and bcrypt.

### Q7: What is encryption?
**A:** Encryption is a two-way transformation of data using a key. Unlike hashing, encrypted data can be decrypted back to the original using the correct key. SecureVault uses AES-256-GCM for encryption.

### Q8: Difference between hashing and encryption?
**A:**
| Property | Hashing | Encryption |
|---|---|---|
| Direction | One-way (irreversible) | Two-way (reversible with key) |
| Purpose | Verification/storage | Confidentiality |
| Key needed | No | Yes |
| Example use | Password verification | Storing vault data |

### Q9: What is a nonce?
**A:** A nonce (Number used ONCE) is a random value used once per encryption operation. It ensures that encrypting the same plaintext twice produces different ciphertexts, preventing patterns that could leak information.

### Q10: What is an authentication tag?
**A:** An authentication tag is a cryptographic checksum generated during AES-GCM encryption. It allows the receiver to verify that the ciphertext has not been modified and was created by someone holding the encryption key.

### Q11: How does your application protect stored passwords?
**A:** All credential data (website, username, password, notes) is bundled into a JSON object and encrypted using AES-256-GCM before being stored in the database. The encryption key is derived from the master password using PBKDF2 and exists only in memory during the active session. The database only contains encrypted blobs.

### Q12: What happens if the database is stolen?
**A:** The attacker would only see encrypted data (base64-encoded blobs). Without the master password, they cannot derive the AES key to decrypt the data. PBKDF2 with 600,000 iterations makes brute-forcing the master password extremely slow.

### Q13: Why use SQLite?
**A:** SQLite is a lightweight, serverless, file-based database that is included in Python's standard library. It is ideal for local applications because it requires no separate server, is easy to use, and stores everything in a single file.

### Q14: Why use `secrets` instead of `random`?
**A:** Python's `random` module uses a pseudo-random number generator (Mersenne Twister) that is deterministic — if you know the seed, you can predict all outputs. The `secrets` module uses the operating system's cryptographic random number generator, which is unpredictable and suitable for security purposes.

### Q15: What happens after multiple failed login attempts?
**A:** After 5 consecutive failed login attempts, the account is temporarily locked for 15 minutes. The lock timestamp is stored in the database. During the lock period, login attempts are rejected. After 15 minutes, the lock expires and the user can try again.

### Q16: What CNS concepts are demonstrated?
**A:**
1. Symmetric encryption (AES-256)
2. Authenticated encryption (GCM mode)
3. Key derivation (PBKDF2-HMAC-SHA256)
4. Password hashing with salt
5. Cryptographically secure random generation
6. Nonce/IV management
7. Authentication and authorization
8. Account security (lockout mechanism)
9. Session management
10. Data integrity verification

---

## 9. Test Cases

| # | Test Case | Input | Expected Result |
|---|---|---|---|
| 1 | Valid registration | Username: "alice", Password: "Str0ng!Pass#2024" | Account created successfully |
| 2 | Duplicate registration | Same username as existing | "Username already exists" |
| 3 | Weak master password | Password: "123" | "Must be at least 8 characters" |
| 4 | Password mismatch | Different confirm password | "Passwords do not match" |
| 5 | Valid login | Correct credentials | Dashboard displayed |
| 6 | Invalid login (wrong password) | Wrong password | "Invalid username or password" |
| 7 | Account lockout | 5 wrong password attempts | Account locked for 15 minutes |
| 8 | Add credential | Valid website, user, pass | Credential saved |
| 9 | Add credential (missing fields) | Empty website | "Website is required" |
| 10 | Edit credential | Modify existing entry | Entry updated and re-encrypted |
| 11 | Delete credential | Confirm deletion | Entry removed from database |
| 12 | Search credential | Search by website name | Matching entries displayed |
| 13 | Password generation | Click Generate | Secure random password shown |
| 14 | Empty input handling | Submit empty form | Validation error shown |
| 15 | Logout | Click Logout | Session cleared, back to Welcome |
| 16 | Plaintext verification | Check database file | No plaintext passwords stored |
| 17 | Data persistence | Restart application | All data still accessible |
| 18 | Session security | Check memory after logout | No keys in memory |

---

## 10. Demonstration Flow (College Demo)

1. **Launch** — Run `python main.py`, show the Welcome screen
2. **Create Account** — Register with username "demo_user" and a strong password
3. **Login** — Log in with the created credentials
4. **Dashboard** — Show the dashboard with 0 saved credentials
5. **Add Credential** — Add a Gmail credential:
   - Website: gmail.com
   - Username: demo@gmail.com
   - Password: Click "Generate Password" to create a strong one
   - Notes: "Personal email"
6. **Save** — Show the credential is saved
7. **Database Inspection** — Open `securevault.db` and show that the vault_entries table contains only encrypted blobs, NOT plaintext passwords
8. **View Credential** — Open the saved credential, show the password is hidden, click "Show" to reveal it
9. **Search** — Search for "gmail" and show the result
10. **Edit** — Modify the notes field and save
11. **Delete** — Delete the credential and confirm
12. **Logout** — Log out and return to the Welcome screen
13. **Failed Login** — Enter wrong password 5 times and show the lockout message

**Important:** Never use real passwords during the demonstration!

---

*Documentation prepared for B.Tech CNS Mini Project — SecureVault*
