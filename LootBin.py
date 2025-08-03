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

def parse_args():
    parser = argparse.ArgumentParser(description='Multi-threaded Termbin.com scanner')
    parser.add_argument('--threads', type=int, default=10, help='Number of worker threads (default: 10)')
    parser.add_argument('--delay', type=float, default=0.2, help='Delay between starting new tasks (seconds, default: 0.2)')
    parser.add_argument('--keywords', type=str, default='keywords.txt', help='Path to keywords file (default: keywords.txt)')
    parser.add_argument('--loot', type=str, default='loot', help='Folder to save loot (default: loot)')
    parser.add_argument('--found', type=str, default='foundlinks.txt', help='File to save found links (default: foundlinks.txt)')
    parser.add_argument('--log', type=str, default='scanner.log', help='Log file (default: scanner.log)')
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

def scan_once(base_url, keywords, loot_dir, found_links_file, log_file):
    suffix = random_suffix()
    url = base_url + suffix

    try:
        response = requests.get(url, timeout=10)
    except Exception as e:
        log(f"[ERROR] Failed to connect to {url}: {e}", log_file)
        return

    if response.status_code == 200:
        log(f"[FOUND] 200 OK: {url}", log_file)
        with file_lock:
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
                        headers = '\n'.join(f"{k}: {v}" for k, v in response.headers.items())
                        lf.write(f"URL: {url}\nStatus Code: {response.status_code}\n\nHeaders:\n{headers}\n\nBody:\n{body}")
                break
        # No keyword found: do nothing
    else:
        # Non-200 responses: do nothing
        pass

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
                executor.submit(scan_once, base_url, keywords, args.loot, args.found, args.log)
                time.sleep(args.delay)
        except KeyboardInterrupt:
            log("[STOP] Scanner stopped by user.", args.log)

if __name__ == "__main__":
    main()
