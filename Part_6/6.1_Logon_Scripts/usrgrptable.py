import pwd
import grp
from prettytable import PrettyTable
from colorama import init, Fore, Style

def get_user_info():
    user_info = []
    for user in pwd.getpwall():
        user_entry = {
            "Name": user.pw_name,
            "Password": user.pw_passwd,
            "UID": user.pw_uid,
            "GID": user.pw_gid,
            "Directory": user.pw_dir,
            "Shell": user.pw_shell,
            "GECOS": user.pw_gecos,
            "Groups": get_user_groups(user.pw_name)
        }
        user_info.append(user_entry)
    return user_info

def get_user_groups(username):
    groups = []
    for group in grp.getgrall():
        if username in group.gr_mem:
            groups.append(group.gr_name)
    return ", ".join(groups)

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
    table = PrettyTable(headers)
    for entry in data:
        colored_entry = [colorize_column(truncate_text(entry.get(key, ""), 30), condition_func(entry.get(key, "")) if condition_func else False, color)
                         for key, color in zip(headers, [Fore.YELLOW, Fore.CYAN, Fore.GREEN, Fore.MAGENTA, Fore.BLUE, Fore.RED, Fore.WHITE, Fore.WHITE])]
        table.add_row(colored_entry)
    table.align = "l"  # Align the content to the left
    table.max_width = 100  # Set the maximum width of the table
    print(table)

def main():
    init()  # Initialize colorama
    user_info = get_user_info()

    print("User Information:")
    display_table(user_info, condition_func=lambda shell: shell != "/usr/bin/false")

if __name__ == "__main__":
    main()
