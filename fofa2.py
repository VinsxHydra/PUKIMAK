import requests
import base64
import os
import time
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("FOFA_EMAIL")
KEY = os.getenv("FOFA_KEY")

API_URL = "https://fofa.info/api/v1/search/next"

def encode_query(query):
    return base64.b64encode(query.encode()).decode()

def extract_data(results):
    hosts = set()
    roots = set()

    for item in results:
        host, domain = item

        if host:
            host = host.replace("http://", "").replace("https://", "")
            host = host.split("/")[0]
            hosts.add(host)

        if domain:
            roots.add(domain)

    return hosts, roots

def grab_all(query, max_loops=500):
    all_hosts = set()
    all_roots = set()
    next_token = None

    for i in range(max_loops):
        print(f"[+] Loop {i+1}")

        params = {
            "email": EMAIL,
            "key": KEY,
            "qbase64": encode_query(query),
            "fields": "host,domain",
            "size": 100
        }

        if next_token:
            params["next"] = next_token

        try:
            r = requests.get(API_URL, params=params, timeout=10)
            data = r.json()
        except Exception as e:
            print("❌ Request error:", e)
            break

        if data.get("error"):
            print("❌ API Error:", data.get("errmsg"))
            break

        results = data.get("results", [])
        next_token = data.get("next")

        print(f"   ↳ results: {len(results)}")

        if not results:
            print("   ⚠️ No more data")
            break

        hosts, roots = extract_data(results)

        all_hosts.update(hosts)
        all_roots.update(roots)

        if not next_token:
            print("   ⚠️ End of data")
            break

        time.sleep(1)

    return all_hosts, all_roots

def save(hosts, roots):
    with open("hosts.txt", "w") as f:
        for h in sorted(hosts):
            f.write(h + "\n")

    with open("roots.txt", "w") as f:
        for r in sorted(roots):
            f.write(r + "\n")

if __name__ == "__main__":
    query = input("Masukkan FOFA dork: ")

    hosts, roots = grab_all(query, max_loops=100)

    save(hosts, roots)

    print(f"\n[✓] Total host: {len(hosts)}")
    print(f"[✓] Total root domain: {len(roots)}")
