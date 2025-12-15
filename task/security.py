# security.py
import os
import getpass


# -------------------------------------------------
#  환경변수(APP_PASSWORD)와 사용자 입력 비밀번호를 비교
# -------------------------------------------------
def check_password():
    system_pw = os.getenv("APP_PASSWORD")
    if not system_pw:
        print("⚠️ 환경 변수(APP_PASSWORD)가 설정되지 않았습니다.")
        return False

    user_pw = getpass.getpass("\n🔒 Enter password to start: ")

    if user_pw != system_pw:
        print("❌ Wrong password. Access denied.")
        return False

    print("✅ Access granted!\n")
    return True
