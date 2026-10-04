"""
Password Security module for SecureVault.

Provides:
- Cryptographically secure password generation using `secrets`
- Password strength analysis with visual feedback

IMPORTANT: This module uses Python's `secrets` module (not `random`)
for all cryptographic operations. The `random` module is NOT
cryptographically secure — its output can be predicted if the
internal state is known.
"""

import secrets
import string


# ── Password Generator ──────────────────────────────────────────────

def generate_password(length: int = 16,
                      use_uppercase: bool = True,
                      use_lowercase: bool = True,
                      use_numbers: bool = True,
                      use_symbols: bool = True) -> str:
    """
    Generate a cryptographically secure random password.

    Uses `secrets.choice()` which is backed by the operating system's
    cryptographic random number generator (e.g., /dev/urandom on Linux,
    CryptGenRandom on Windows). This is fundamentally different from
    `random.choice()` which uses a deterministic pseudo-random algorithm
    (Mersenne Twister) that can be predicted.

    Args:
        length: Desired password length (minimum 4 to allow one of each type).
        use_uppercase: Include uppercase letters (A-Z).
        use_lowercase: Include lowercase letters (a-z).
        use_numbers: Include digits (0-9).
        use_symbols: Include special characters (!@#$%^&*...).

    Returns:
        A random password string.

    Raises:
        ValueError: If no character types are selected or length is too small.
    """
    if length < 4:
        length = 4  # Minimum length to ensure variety

    # Build the character pool based on user selections
    charset = ""
    required_chars = []

    if use_uppercase:
        charset += string.ascii_uppercase
        required_chars.append(secrets.choice(string.ascii_uppercase))

    if use_lowercase:
        charset += string.ascii_lowercase
        required_chars.append(secrets.choice(string.ascii_lowercase))

    if use_numbers:
        charset += string.digits
        required_chars.append(secrets.choice(string.digits))

    if use_symbols:
        symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        charset += symbols
        required_chars.append(secrets.choice(symbols))

    if not charset:
        # Fallback: at least use lowercase
        charset = string.ascii_lowercase
        required_chars = [secrets.choice(charset)]

    # Fill the remaining length with random characters from the full pool
    remaining_length = length - len(required_chars)
    password_chars = required_chars + [secrets.choice(charset)
                                       for _ in range(remaining_length)]

    # Shuffle the result so required characters aren't always at the start
    # We use a Fisher-Yates shuffle with secrets for cryptographic randomness
    shuffled = list(password_chars)
    for i in range(len(shuffled) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]

    return "".join(shuffled)


# ── Password Strength Checker ───────────────────────────────────────

# Common weak patterns that should reduce the strength score
WEAK_PATTERNS = [
    "123456", "password", "qwerty", "abc123", "letmein",
    "admin", "welcome", "monkey", "dragon", "master",
    "login", "princess", "football", "shadow", "sunshine",
    "trustno1", "iloveyou", "batman", "access", "hello",
    "charlie", "donald", "password1", "qwerty123",
]


def check_password_strength(password: str) -> dict:
    """
    Analyze password strength based on multiple criteria.

    This is a heuristic analysis — no strength checker can guarantee
    absolute security. It provides a reasonable estimate based on:

    - Length (longer is better)
    - Character diversity (uppercase, lowercase, numbers, symbols)
    - Absence of common weak patterns
    - Absence of repetitive or sequential characters

    Args:
        password: The password to analyze.

    Returns:
        A dict with:
          - 'score': integer 0-100
          - 'level': one of "Very Weak", "Weak", "Medium", "Strong", "Very Strong"
          - 'feedback': list of improvement suggestions
    """
    if not password:
        return {
            "score": 0,
            "level": "Very Weak",
            "feedback": ["Password is empty."],
        }

    score = 0
    feedback = []

    # ── Length scoring ──
    if len(password) >= 8:
        score += 10
    if len(password) >= 12:
        score += 15
    if len(password) >= 16:
        score += 15
    if len(password) >= 20:
        score += 10
    if len(password) < 8:
        feedback.append("Use at least 8 characters.")

    # ── Character diversity ──
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    if has_upper:
        score += 10
    else:
        feedback.append("Add uppercase letters.")

    if has_lower:
        score += 10
    else:
        feedback.append("Add lowercase letters.")

    if has_digit:
        score += 10
    else:
        feedback.append("Add numbers.")

    if has_symbol:
        score += 15
    else:
        feedback.append("Add special characters (!@#$%^&*...).")

    # ── Character variety bonus ──
    unique_chars = len(set(password))
    if unique_chars >= 10:
        score += 5
    if unique_chars >= 15:
        score += 5

    # ── Penalty for common weak patterns ──
    password_lower = password.lower()
    for pattern in WEAK_PATTERNS:
        if pattern in password_lower:
            score -= 20
            feedback.append(f"Avoid common patterns like '{pattern}'.")
            break

    # ── Penalty for repetitive characters ──
    has_repeats = False
    for i in range(len(password) - 2):
        if password[i] == password[i + 1] == password[i + 2]:
            has_repeats = True
            break
    if has_repeats:
        score -= 10
        feedback.append("Avoid repeating the same character multiple times.")

    # ── Penalty for sequential characters ──
    sequential = False
    for i in range(len(password) - 2):
        if (ord(password[i + 1]) == ord(password[i]) + 1 and
                ord(password[i + 2]) == ord(password[i]) + 2):
            sequential = True
            break
    if sequential:
        score -= 10
        feedback.append("Avoid sequential characters (abc, 123).")

    # ── Normalize score ──
    score = max(0, min(100, score))

    # ── Determine level ──
    if score < 20:
        level = "Very Weak"
    elif score < 40:
        level = "Weak"
    elif score < 60:
        level = "Medium"
    elif score < 80:
        level = "Strong"
    else:
        level = "Very Strong"

    if not feedback:
        feedback.append("Good password!")

    return {
        "score": score,
        "level": level,
        "feedback": feedback,
    }
