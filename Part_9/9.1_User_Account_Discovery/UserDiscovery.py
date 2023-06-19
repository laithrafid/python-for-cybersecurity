import os
import platform
import subprocess
import grp

def get_admin_accounts():
    admins = []
    if platform.system() == "Windows":
        import wmi
        w = wmi.WMI()
        for group in w.Win32_Group():
            if group.Name == "Administrators":
                admins = [a.Name for a in group.associators(wmi_result_class="Win32_UserAccount")]
    elif platform.system() == "Linux":
        with open('/etc/group', 'r') as file:
            for line in file:
                if line.startswith('sudo:'):
                    admins = line.split(':')[1].strip().split(',')
    elif platform.system() == "Darwin":
        admins = subprocess.check_output(['dscl', '.', 'read', '/Groups/admin', 'GroupMembership']).decode().split()[1:]

    return admins

def list_user_accounts():
    admins = get_admin_accounts()
    all_users = []

    if platform.system() == "Windows":
        import wmi
        w = wmi.WMI()
        for user in w.Win32_UserAccount():
            all_users.append(user)
    elif platform.system() == "Linux":
        with open('/etc/passwd', 'r') as file:
            for line in file:
                fields = line.split(':')
                if len(fields) >= 7:
                    username = fields[0]
                    all_users.append(username)
    elif platform.system() == "Darwin":
        result = subprocess.check_output(['dscl', '.', 'list', '/Users']).decode().split()
        for username in result:
            if username != '_amavisd' and username != 'daemon' and username != 'nobody' and username != 'root':
                all_users.append(username)

    for user in all_users:
        if user in admins:
            print("Username: %s (Administrator)" % user)
        else:
            print("Username: %s" % user)

        if platform.system() == "Windows":
            import wmi
            w = wmi.WMI()
            user_info = w.Win32_UserAccount(Name=user)
            if user_info:
                user_info = user_info[0]
                print("Full Name: %s" % user_info.FullName)
                print("Disabled: %s" % user_info.Disabled)
                print("Local: %s" % user_info.LocalAccount)
                print("Password Changeable: %s" % user_info.PasswordChangeable)
                print("Password Expires: %s" % user_info.PasswordExpires)
                print("Password Required: %s" % user_info.PasswordRequired)
        elif platform.system() == "Linux":
            with open('/etc/passwd', 'r') as file:
                for line in file:
                    fields = line.split(':')
                    if len(fields) >= 7 and fields[0] == user:
                        uid = fields[2]
                        gid = fields[3]
                        home_directory = fields[5]
                        shell = fields[6]
                        print("UID: %s" % uid)
                        print("GID: %s" % gid)
                        print("Home Directory: %s" % home_directory)
                        print("Shell: %s" % shell)

                        # Get groups the user is a member of
                        group_names = [group.gr_name for group in grp.getgrall() if user in group.gr_mem]
                        print("Member of Groups: %s" % ", ".join(group_names))
                        break
        elif platform.system() == "Darwin":
            try:
                user_info = subprocess.check_output(['dscl', '.', '-read', '/Users/' + user]).decode()
                uid = user_info.split('UniqueID: ')[1].split('\n')[0]
                gid = user_info.split('PrimaryGroupID: ')[1].split('\n')[0]
                home_directory = user_info.split('NFSHomeDirectory: ')[1].split('\n')[0]
                shell = user_info.split('UserShell: ')[1].split('\n')[0]
                print("UID: %s" % uid)
                print("GID: %s" % gid)
                print("Home Directory: %s" % home_directory)
                print("Shell: %s" % shell)

                # Get groups the user is a member of
                group_names = [group.gr_name for group in grp.getgrall() if user in group.gr_mem]
                print("Member of Groups: %s" % ", ".join(group_names))
            except subprocess.CalledProcessError:
                print("Failed to retrieve user information.")

        print("\n")

def print_password_policy():
    if platform.system() == "Windows":
        os.system("net accounts")
    elif platform.system() == "Linux":
        os.system("sudo grep '^PASS_MAX_DAYS\|^PASS_MIN_DAYS\|^PASS_WARN_AGE' /etc/login.defs")
    elif platform.system() == "Darwin":
        os.system("pwpolicy getaccountpolicies")

# Get list of Administrator Accounts
admins = get_admin_accounts()
print("Administrator Accounts: ", admins)

# List user accounts on the device
print("User Accounts:")
list_user_accounts()

# Print Password Policy
print("Password Policy:")
print_password_policy()
