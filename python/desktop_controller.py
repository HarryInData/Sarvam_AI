"""
desktop_controller.py — Full Windows desktop control module.
Handles: apps, files, web, system, email, typing, volume, etc.
"""

import os
import sys
import time
import shutil
import smtplib
import subprocess
import webbrowser
import urllib.parse
import pyautogui
import psutil
import pyperclip
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import CONFIG

# App name → executable / command mapping
APP_MAP = {
    "chrome"       : "chrome",
    "google chrome": "chrome",
    "firefox"      : "firefox",
    "edge"         : "msedge",
    "notepad"      : "notepad",
    "calculator"   : "calc",
    "paint"        : "mspaint",
    "word"         : "winword",
    "excel"        : "excel",
    "powerpoint"   : "powerpnt",
    "vlc"          : "vlc",
    "spotify"      : "spotify",
    "vs code"      : "code",
    "vscode"       : "code",
    "task manager" : "taskmgr",
    "file explorer": "explorer",
    "explorer"     : "explorer",
    "cmd"          : "cmd",
    "powershell"   : "powershell",
    "whatsapp"     : "whatsapp",
    "discord"      : "discord",
    "zoom"         : "zoom",
    "telegram"     : "telegram",
    "obs"          : "obs64",
    "photoshop"    : "photoshop",
    "snipping tool": "snippingtool",
}


class DesktopController:

    # ──────────────────────────────────────────────────────────────────
    #  APPS
    # ──────────────────────────────────────────────────────────────────
    def open_app(self, app: str) -> None:
        """Open any application by name."""
        app_lower = app.lower().strip()
        executable = APP_MAP.get(app_lower, app_lower)
        try:
            subprocess.Popen(executable, shell=True)
            print(f"[✓] Opening: {app}")
        except Exception as e:
            raise RuntimeError(f"Could not open {app}: {e}")

    def close_app(self, app: str) -> None:
        """Kill a process by name."""
        app_lower = app.lower().strip()
        executable = APP_MAP.get(app_lower, app_lower)
        # Try with .exe
        exe_name = executable if executable.endswith(".exe") else executable + ".exe"
        killed = False
        for proc in psutil.process_iter(["name"]):
            if proc.info["name"] and proc.info["name"].lower() in [exe_name.lower(), executable.lower()]:
                proc.kill()
                killed = True
        if not killed:
            # fallback
            os.system(f"taskkill /f /im {exe_name} >nul 2>&1")

    def minimize_all(self) -> None:
        """Show desktop (Win+D)."""
        pyautogui.hotkey("win", "d")

    def take_screenshot(self, filename: str = "screenshot.png") -> str:
        """Take screenshot and save to Desktop."""
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(desktop, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        return path

    # ──────────────────────────────────────────────────────────────────
    #  FILES & FOLDERS
    # ──────────────────────────────────────────────────────────────────
    def open_path(self, path: str) -> None:
        """Open a file or folder."""
        path = os.path.expanduser(path)
        if os.path.exists(path):
            os.startfile(path)
        else:
            raise FileNotFoundError(f"Path not found: {path}")

    def create_file(self, path: str, content: str = "") -> None:
        """Create a file with optional content."""
        path = os.path.expanduser(path)
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def delete_file(self, path: str) -> None:
        """Delete a file or folder."""
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
        else:
            raise FileNotFoundError(f"Not found: {path}")

    def search_files(self, query: str, location: str = "") -> str:
        """Search for files using Windows search."""
        search_loc = location if location else os.path.expanduser("~")
        webbrowser.open(f"search-ms:query={urllib.parse.quote(query)}&crumb=location:{urllib.parse.quote(search_loc)}")
        return f"Searching for {query}..."

    # ──────────────────────────────────────────────────────────────────
    #  WEB
    # ──────────────────────────────────────────────────────────────────
    def web_search(self, query: str) -> None:
        """Search on Google."""
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)

    def open_url(self, url: str) -> None:
        """Open a URL in the browser."""
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)

    def youtube_search(self, query: str) -> None:
        """Search YouTube."""
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(url)

    # ──────────────────────────────────────────────────────────────────
    #  SYSTEM CONTROLS
    # ──────────────────────────────────────────────────────────────────
    def volume_up(self) -> None:
        for _ in range(5):
            pyautogui.press("volumeup")

    def volume_down(self) -> None:
        for _ in range(5):
            pyautogui.press("volumedown")

    def mute(self) -> None:
        pyautogui.press("volumemute")

    def sleep_pc(self) -> None:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    def restart_pc(self) -> None:
        os.system("shutdown /r /t 5")

    def shutdown_pc(self) -> None:
        os.system("shutdown /s /t 5")

    def lock_pc(self) -> None:
        os.system("rundll32.exe user32.dll,LockWorkStation")

    def battery_status(self) -> str:
        battery = psutil.sensors_battery()
        if battery:
            percent = int(battery.percent)
            plugged = "charging" if battery.power_plugged else "on battery"
            return f"Boss, battery {percent}% hai aur {plugged} chal raha hai."
        return "Battery information available nahi hai."

    def get_time(self) -> str:
        now = datetime.now()
        return f"Boss, abhi time hai {now.strftime('%I:%M %p')}."

    def get_date(self) -> str:
        now = datetime.now()
        return f"Aaj {now.strftime('%A, %d %B %Y')} hai boss."

    # ──────────────────────────────────────────────────────────────────
    #  KEYBOARD / TYPING
    # ──────────────────────────────────────────────────────────────────
    def type_text(self, text: str) -> None:
        """Type text at cursor position."""
        time.sleep(0.5)
        pyautogui.typewrite(text, interval=0.05)

    def press_key(self, key: str) -> None:
        """Press a key or key combo like ctrl+c."""
        keys = [k.strip() for k in key.lower().split("+")]
        if len(keys) > 1:
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(keys[0])

    def clipboard_copy(self, text: str) -> None:
        """Copy text to clipboard."""
        pyperclip.copy(text)

    # ──────────────────────────────────────────────────────────────────
    #  EMAIL
    # ──────────────────────────────────────────────────────────────────
    def send_email(self, params: dict) -> str:
        """Send an email via Gmail SMTP."""
        to      = params.get("to", "")
        subject = params.get("subject", "")
        body    = params.get("body", "")

        if not to:
            return "Boss, please recipient email address batao."

        msg = MIMEMultipart()
        msg["From"]    = CONFIG["EMAIL_ADDRESS"]
        msg["To"]      = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(CONFIG["SMTP_SERVER"], CONFIG["SMTP_PORT"])
            server.starttls()
            server.login(CONFIG["EMAIL_ADDRESS"], CONFIG["EMAIL_PASSWORD"])
            server.send_message(msg)
            server.quit()
            return f"Email successfully bhej diya boss {to} ko."
        except Exception as e:
            return f"Email nahi bheja ja saka: {e}"