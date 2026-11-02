"""CLI utility to generate and verify Argon2id password hashes for MediDeck."""
import sys
import getpass
import argon2

ph = argon2.PasswordHasher(type=argon2.Type.ID)


def generate_hash(password: str) -> str:
    return ph.hash(password)


def verify(password_hash: str, password: str) -> bool:
    try:
        return ph.verify(password_hash, password)
    except Exception:
        return False


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        if len(sys.argv) < 4:
            print("Usage: python hash_password.py verify '<hash>' '<password>'")
            sys.exit(1)
        h = sys.argv[2]
        p = sys.argv[3]
        valid = verify(h, p)
        print(f"Match: {valid}")
        sys.exit(0 if valid else 1)

    if len(sys.argv) > 1 and sys.argv[1] != "verify":
        password = sys.argv[1]
    else:
        password = getpass.getpass("Enter password to hash: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Error: Passwords do not match.")
            sys.exit(1)

    hashed = generate_hash(password)
    print("\n--- Argon2id Hash Generated ---")
    print(hashed)
    print("-------------------------------\n")
    print("Copy this value into your environment variable (e.g., ADMIN_PASSWORD_HASH).")


if __name__ == "__main__":
    main()

