import os
import chardet

def find_log_files(username):
    log_files = []
    log_directory = '/var/log/'

    # Search for system log files
    for root, dirs, files in os.walk(log_directory):
        for file in files:
            log_files.append(os.path.join(root, file))

    # Search for shell history files in user's home directory
    home_directory = f'/Users/{username}'
    if os.path.isdir(home_directory):
        shell_history_files = [
            '.bash_history',
            '.bash_profile',
            '.bashrc',
            '.bash_logout',
            '.sh_history',
            '.zsh_history',
            '.zshrc',
            '.zlogout'
        ]
        for history_file in shell_history_files:
            history_file_path = os.path.join(home_directory, history_file)
            if os.path.isfile(history_file_path):
                log_files.append(history_file_path)

    return log_files

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    return encoding

def filter_logs_for_user(log_files, username):
    filtered_logs = []

    for log_file in log_files:
        if os.path.isfile(log_file):
            encoding = detect_encoding(log_file)
            try:
                with open(log_file, 'r', encoding=encoding, errors='ignore') as file:
                    for line in file:
                        if username in line or "Setup User" in line:
                            log_entry = line.rstrip()
                            filtered_logs.append((log_file, log_entry))
            except UnicodeDecodeError:
                print(f"Skipping file: {log_file}. Unable to decode using {encoding}.")

    return filtered_logs

# Get username from user input
username = input("Enter the username to investigate in the logs: ")

log_files = find_log_files(username)
filtered_logs = filter_logs_for_user(log_files, username)

# Print the filtered log entries for the specified user with timestamps
print(f"Filtered Log Entries for User: {username}")
for filename, log_entry in filtered_logs:
    print("Filename:", filename)
    print("Path:", os.path.dirname(filename))
    print("Timestamp:", os.path.getmtime(filename))
    print("Log Entry:", log_entry)
    print("-" * 50)
