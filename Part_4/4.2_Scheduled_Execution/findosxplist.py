#!/usr/bin/python3
import subprocess
import os
from tabulate import tabulate
from colorama import Fore, Style

def get_launchctl_list():
    # Run 'sudo launchctl list' command and capture the output
    result = subprocess.run(['sudo', 'launchctl', 'list'], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip().split('\n')
    else:
        print("Error: Unable to retrieve launchctl list.")
        return []

def find_plist_file(label):
    # Search for .plist file with the given label in various locations
    plist_locations = [
        os.path.expanduser('~/Library/LaunchAgents'),
        '/Library/LaunchAgents',
        '/Library/LaunchDaemons',
        '/System/Library/LaunchAgents',
        '/System/Library/LaunchDaemons'
    ]

    for location in plist_locations:
        files = os.listdir(location)
        for file in files:
            if file.endswith('.plist') and label in file:
                return os.path.join(location, file)

    return None

# Get the launchctl list
launchctl_list = get_launchctl_list()

# Prepare the table headers and data
headers = ['PID', 'Label', 'File Path']
table_data = []

# Process each entry in launchctl list
for entry in launchctl_list:
    # Split the entry into label, pid, and status
    parts = entry.split('\t')
    pid = parts[0]
    label = parts[2]

    # Find corresponding .plist file
    plist_file = find_plist_file(label)

    # Determine the color for the label
    if label.startswith("com.apple"):
        label_color = Fore.BLUE
    else:
        label_color = Fore.RED

    # Create a row with colored columns
    if plist_file:
        row = [
            f"{Fore.GREEN}{pid}{Style.RESET_ALL}",
            f"{label_color}{label}{Style.RESET_ALL}",
            f"{Fore.YELLOW}{plist_file}{Style.RESET_ALL}"
        ]
    else:
        row = [
            f"{Fore.GREEN}{pid}{Style.RESET_ALL}",
            f"{label_color}{label}{Style.RESET_ALL}",
            f"{Fore.RED}No corresponding .plist file{Style.RESET_ALL}"
        ]

    table_data.append(row)

# Print the table
table = tabulate(table_data, headers, tablefmt='pipe')
print(table)
