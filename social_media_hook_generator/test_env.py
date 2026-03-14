#!/usr/bin/env python3
"""
Test script to verify environment variables are set correctly.
Run this after setting up your .env file.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def test_env_vars():
    """Test all required environment variables."""
    print("Checking environment variables...\n")

    required_vars = {
        "GOOGLE_API_KEY": "Google Gemini API Key",
        "SECRET_KEY": "Flask Secret Key",
    }
    optional_vars = {
        "TWITTER_BEARER_TOKEN": "Twitter Bearer Token (optional)",
        "DATABASE_URL": "Database URL (optional, defaults to SQLite)",
    }

    all_good = True
    placeholders = {
        "GOOGLE_API_KEY": {"your_google_gemini_api_key_here"},
        "SECRET_KEY": {"your_32_character_random_secret_key_here", "your-secret-key-here"},
    }

    for var, description in required_vars.items():
        value = (os.getenv(var) or "").strip()
        if value and value not in placeholders.get(var, set()):
            print(f"[OK] {description}: Set")
        else:
            print(f"[MISSING] {description}: NOT SET or using placeholder")
            all_good = False

    print()

    for var, description in optional_vars.items():
        value = (os.getenv(var) or "").strip()
        if value:
            print(f"[OK] {description}: Set")
        else:
            print(f"[INFO] {description}: Not set")

    print()
    if os.getenv("DATABASE_URL"):
        print("[OK] Database: PostgreSQL configured")
    else:
        print("[OK] Database: SQLite (default)")

    print()
    if all_good:
        print("All required environment variables are set.")
        print("You can now run: python app.py")
    else:
        print("Please set the missing required variables in your .env file.")
        print("Check README.md for instructions.")


if __name__ == "__main__":
    test_env_vars()
