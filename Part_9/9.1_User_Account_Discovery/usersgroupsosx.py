#!/usr/bin/python3
import pwd
import grp
import platform
from prettytable import PrettyTable
from colorama import init, Fore, Style
import subprocess
import datetime

def get_user_info():
    user_info = []
    processed_users = set()
    for user in pwd.getpwall():
        if user.pw_name in processed_users:
            continue
        user_entry = {
            "Name": user.pw_name,
            "PID": get_user_pid(user.pw_name),  # Add the PID field
            "Password": user.pw_passwd,
            "UID": user.pw_uid,
            "GID": user.pw_gid,
            "Directory": user.pw_dir,
            "Shell": user.pw_shell,
            "GECOS": user.pw_gecos,
            "Groups": get_user_groups(user.pw_name),
            "Last Used": get_last_used(user.pw_name)
        }
        user_info.append(user_entry)
        processed_users.add(user.pw_name)
    return user_info

def get_user_groups(username):
    groups = []
    for group in grp.getgrall():
        if username in group.gr_mem:
            groups.append(group.gr_name)
    return ", ".join(groups)

def get_user_pid(username):
    try:
        command = f"pgrep -u {username}"
        output = subprocess.check_output(command, shell=True, text=True)
        pids = output.strip().split("\n")
        return ", ".join(pids)
    except subprocess.CalledProcessError:
        return "N/A"

def get_last_used(username):
    if platform.system() == "Darwin":  # macOS
        try:
            command = f"last | grep {username} | head -n 1"
            output = subprocess.check_output(command, shell=True, text=True)
            last_line = output.strip()
            last_login_time = last_line.split()[4:9]
            last_login_str = " ".join(last_login_time)
            return last_login_str
        except subprocess.CalledProcessError:
            return "N/A"
    else:
        try:
            spwd_entry = pwd.getspnam(username)
            last_used_timestamp = spwd_entry.sp_lstchg * 86400  # Convert to seconds
            last_used_datetime = datetime.datetime.fromtimestamp(last_used_timestamp)
            return last_used_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except KeyError:
            return "N/A"

def colorize_column(value, condition, color):
    if condition:
        return f"{color}{value}{Style.RESET_ALL}"
    else:
        return value

def truncate_text(text, max_length):
    text = str(text)
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text

def display_table(data, condition_func=None):
    headers = list(data[0].keys())
    headers.insert(1, "PID")  # Insert "PID" column header

    # Remove duplicate "PID" field name
    if "PID" in headers[2:]:
        headers.remove("PID")

    table = PrettyTable(headers)
    sorted_data = sorted(data, key=lambda x: x['UID'])
    for entry in sorted_data:
        colored_entry = [
            colorize_column(truncate_text(entry.get(key, ""), 30),
                            condition_func(entry.get(key, "")) if condition_func else False,
                            color)
            for key, color in zip(headers, [Fore.YELLOW, Fore.CYAN, Fore.GREEN, Fore.MAGENTA, Fore.BLUE, Fore.RED, Fore.WHITE, Fore.WHITE, Fore.WHITE, Fore.WHITE, Fore.WHITE])
        ]
        table.add_row(colored_entry)
    table.align = "l"
    table.max_width = 100
    print(table)

def print_group_table():
    try:
        command = "dscl . -list /Groups"
        output = subprocess.check_output(command, shell=True, text=True)
        groups = output.strip().split("\n")
        
        group_table = PrettyTable(["Group Name", "Comment", "Users"])
        group_table.align = "l"
        
        for group in groups:
            group_info = subprocess.check_output(f"dscl . -read /Groups/{group}", shell=True, text=True)
            comment = ""
            users = ""
            lines = group_info.split("\n")
            for i, line in enumerate(lines):
                if "GroupMembership:" in line:
                    users = line.split(":")[1].strip()
                elif "Comment:" in line and i < len(lines) - 1:
                    comment = lines[i + 1].strip()  # Get the comment from the next line
            
            colored_group = colorize_column(group, False, Fore.YELLOW)
            colored_comment = colorize_column(comment, False, Fore.CYAN)
            colored_users = colorize_column(users, False, Fore.GREEN)
            
            group_table.add_row([colored_group, colored_comment, colored_users])
        
        print("Group Information:")
        print(group_table)
        
        total_groups = len(groups)
        print(f"Total number of groups: {total_groups}")
    
    except subprocess.CalledProcessError:
        print("Failed to retrieve group information.")

def main():
    init()
    user_info = get_user_info()

    print("User Information:")
    display_table(user_info, condition_func=lambda shell: shell != "/usr/bin/false")

    total_users = len(user_info)
    print(f"Total number of users: {total_users}")

    print_group_table()

if __name__ == "__main__":
    main()
