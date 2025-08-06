# 📬 Anonymous Chat (Gist Message Board Terminal App)

A lightweight terminal-based chat system using **GitHub Gist** as a shared backend.  
This is a real-time message board you can run from your **Android device using Termux**.

---

## 🚀 Quick Start Guide (Termux on Android)

### 1. Install Termux (via [F-Droid](https://f-droid.org/en/packages/com.termux/))

_❗Avoid the outdated Play Store version._

---

### 2. Install Required Packages

```bash
pkg update
pkg install git python
pip install requests
```

---

### 3. Clone the Repository

```bash
git clone https://github.com/makrand999/anonymous-chat.git
cd anonymous-chat
```

---

### 4. Configure Your GitHub Gist

Open `u.py` and **edit the following lines** with your own:

```python
self.token = "your_github_token"
self.gist_id = "your_gist_id"
```

🔐 Tip: To avoid hardcoding, you can export your token like this:

```bash
export GITHUB_TOKEN=your_token
```

And change in code:

```python
self.token = os.getenv("GITHUB_TOKEN")
```

---

### 5. Run the App

```bash
python u.py
```

Start typing to send messages. Use commands like `help`, `count`, `reset`, etc.

---

## ✏️ Commands Reference

| Command | Description                          |
|---------|--------------------------------------|
| clear   | Refresh and reprint the message list |
| count   | Show current message count           |
| reset   | Wipe all messages                    |
| help    | Show available commands              |
| quit    | Exit the application                 |

---

## 📄 License

MIT — Free to use, modify, and share.

---