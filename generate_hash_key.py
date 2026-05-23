#!/usr/bin/env python
"""
Generate a random secret key for Django settings.
Usage: python generate_hash_key.py
"""

import secrets
import string


def generate_secret_key(length: int = 50) -> str:
    """
    Generate a cryptographically strong random secret key.

    Args:
        length: Length of the secret key (default: 50)

    Returns:
        A random secret key string
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    secret_key = ''.join(secrets.choice(characters) for _ in range(length))
    return secret_key


def generate_api_key(length: int = 32) -> str:
    """
    Generate a random API key (alphanumeric only).

    Args:
        length: Length of the API key (default: 32)

    Returns:
        A random API key string
    """
    characters = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(characters) for _ in range(length))
    return api_key


def generate_token(length: int = 64) -> str:
    """
    Generate a random token (hex format).

    Args:
        length: Length of the token (default: 64)

    Returns:
        A random token string in hex format
    """
    return secrets.token_hex(length // 2)


if __name__ == '__main__':
    import sys

    print("=" * 70)
    print("Secret Key Generator")
    print("=" * 70)
    print()

    # Django Secret Key
    secret_key = generate_secret_key()
    print("Django SECRET_KEY:")
    print(f"SECRET_KEY = '{secret_key}'")
    print()

    # API Key
    api_key = generate_api_key()
    print("API Key (alphanumeric):")
    print(f"API_KEY = '{api_key}'")
    print()

    # Random Token
    token = generate_token()
    print("Random Token (hex):")
    print(f"TOKEN = '{token}'")
    print()

    print("=" * 70)
    print("Copy and paste any of these into your .env file")
    print("=" * 70)
