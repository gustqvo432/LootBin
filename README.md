# 🏴‍☠️ LootBin
**LootBin** is a multi-threaded Python tool to hunt public pastes on [termbin.com](https://termbin.com), looking for interesting content based on keywords you provide. It automatically saves found links and matching pastes into organized folders — perfect for research, OSINT, or just exploring what's out there.

## ✨ Features
- Multi-threaded scanning
- Custom keywords to search for
- Saves matching links & full pastes
- Command-line configurable (threads, delay, loot folder, etc.)
- Clean logging to console and file
- Only logs useful events (found, loot, errors)

## ⚙️ Installation
```bash
git clone https://github.com/Ninja-Yubaraj/LootBin.git
cd LootBin
```
### 🐍 Using virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** If `requirements.txt` isn’t there, install manually:

```bash
pip install requests
```

## 🚀 Usage
Default files & folders:
- `keywords.txt` → keywords (one per line)
- `loot/` → folder to save loot
- `foundlinks.txt` → found 200 OK URLs
- `scanner.log` → log file

### ▶ Run with defaults

```bash
python LootBin.py
```

### ⚡ Run with custom options

```bash
python LootBin.py \
  --threads 20 \
  --delay 0.1 \
  --keywords mywords.txt \
  --loot myloot \
  --found links.txt \
  --log mylog.log
```

| Option       | Description                                | Default          |
| ------------ | ------------------------------------------ | ---------------- |
| `--threads`  | Number of worker threads                   | `10`             |
| `--delay`    | Delay between starting new tasks (seconds) | `0.2`            |
| `--keywords` | Path to keywords file                      | `keywords.txt`   |
| `--loot`     | Folder to save loot                        | `loot`           |
| `--found`    | File to save found 200 OK links            | `foundlinks.txt` |
| `--log`      | Log file                                   | `scanner.log`    |


## 📂 Output
- **Loot folder:** text files named by random suffix, containing matching pastes
- **foundlinks.txt:** list of termbin links returning 200 OK
- **scanner.log:** clean logs of useful events


## 📝 Example keywords.txt
```text
password
api_key
secret
token
```

## ☕ Contributing
Pull requests & suggestions welcome! Feel free to fork and add:

- Colored logs
- JSON output
- Live stats
- Dockerfile

## ✨ Author
Made with ❤️ by [Ninja-Yubaraj](https://github.com/Ninja-Yubaraj)

> For educational & research purposes only. Use responsibly!
