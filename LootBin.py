import requests
import random
import string
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
import argparse

# Locks for thread safety
log_lock = threading.Lock()
file_lock = threading.Lock()

USER_AGENTS = [
    # Windows Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Windows Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    # Mac Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    # Linux Chrome
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Linux Firefox
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    # Edge Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }

def parse_args():
    parser = argparse.ArgumentParser(description='Multi-threaded Termbin.com scanner')
    parser.add_argument('--threads', type=int, default=10, help='Number of worker threads (default: 10)')
    parser.add_argument('--delay', type=float, default=0.2, help='Delay between starting new tasks (seconds, default: 0.2)')
    parser.add_argument('--keywords', type=str, default='keywords.txt', help='Path to keywords file (default: keywords.txt)')
    parser.add_argument('--loot', type=str, default='loot', help='Folder to save loot (default: loot)')
    parser.add_argument('--found', type=str, default='foundlinks.txt', help='File to save found links (default: foundlinks.txt)')
    parser.add_argument('--log', type=str, default='scanner.log', help='Log file (default: scanner.log)')
    parser.add_argument('--timeout', type=float, default=10, help='Request timeout in seconds (default: 10)')
    return parser.parse_args()

def load_keywords(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[ERROR] Keywords file '{path}' not found. Exiting.")
        exit(1)

def log(message, log_file):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}"
    with log_lock:
        print(full_message)
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(full_message + '\n')

def random_suffix():
    length = random.choice([4, 5])
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def scan_once(base_url, keywords, loot_dir, found_links_file, log_file, timeout):
    suffix = random_suffix()
    url = base_url + suffix
    headers = get_random_headers()

    try:
        response = requests.get(url, timeout=timeout, headers=headers)
    except Exception as e:
        log(f"[ERROR] Failed to connect to {url}: {e}", log_file)
        return

    if response.status_code == 200:
        log(f"[FOUND] 200 OK: {url}", log_file)
        with file_lock:
            # Avoid duplicates in foundlinks.txt
            if not os.path.exists(found_links_file) or url not in open(found_links_file).read():
                with open(found_links_file, 'a', encoding='utf-8') as flf:
                    flf.write(url + '\n')

        body = response.text
        lower_body = body.lower()

        for kw in keywords:
            if kw.lower() in lower_body:
                log(f"[LOOT] Keyword '{kw}' found in {url}! Saving response.", log_file)
                loot_file = os.path.join(loot_dir, f"{suffix}.txt")
                with file_lock:
                    with open(loot_file, 'w', encoding='utf-8') as lf:
                        headers_text = '\n'.join(f"{k}: {v}" for k, v in response.headers.items())
                        lf.write(f"URL: {url}\nStatus Code: {response.status_code}\n\nHeaders:\n{headers_text}\n\nBody:\n{body}")
                break
    elif response.status_code == 429:  # Rate limit
        log(f"[RATE-LIMIT] 429 Too Many Requests. Backing off...", log_file)
        time.sleep(2)

def main():
    args = parse_args()
    base_url = 'https://termbin.com/'

    ascii_art = r"""
 _                _   ____  _       
| |    ___   ___ | |_| __ )(_)_ __  
| |   / _ \ / _ \| __|  _ \| | '_ \ 
| |__| (_) | (_) | |_| |_) | | | | |
|_____\___/ \___/ \__|____/|_|_| |_|
                                    
    Author: Ninja-Yubaraj
    Github: https://github.com/Ninja-Yubaraj/LootBin
    """

    print(ascii_art)

    # Ensure loot directory exists
    os.makedirs(args.loot, exist_ok=True)

    # Load keywords
    keywords = load_keywords(args.keywords)

    log(f"[START] LootBin started with {args.threads} threads, delay={args.delay}s", args.log)
    log(f"[INFO] Keywords loaded: {len(keywords)} items", args.log)

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        try:
            while True:
                executor.submit(scan_once, base_url, keywords, args.loot, args.found, args.log, args.timeout)
                time.sleep(args.delay)
        except KeyboardInterrupt:
            log("[STOP] Scanner stopped by user.", args.log)

if __name__ == "__main__":
    main()
