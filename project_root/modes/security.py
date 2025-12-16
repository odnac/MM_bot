# security.py
import os
import getpass


def check_password():
    system_pw = os.getenv("APP_PASSWORD")
    if not system_pw:
        print("\n⚠️ The environment variable (APP_PASSWORD) is not set.")
        return False

    user_pw = getpass.getpass("\n🔒 Enter password to start: ")

    if user_pw != system_pw:
        print("\n❌ Wrong password. Access denied.\n\n")
        return False

    print("✅ Access granted!")
    return True
