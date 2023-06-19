import os
import re
from zipfile import ZipFile
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
from termcolor import colored  # Importing colored module for colored output

# Regular expressions and their names
patterns = [
    (r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}', "Email"),
    (r'[(]*[0-9]{3}[)]*-[0-9]{3}-[0-9]{4}', "Phone Number"),
    (r'[0-9]{3}-[0-9]{2}-[0-9]{4}', "SSN"),
    (r'4[0-9]{12}(?:[0-9]{3})?', "Visa Card Number"),
    (r'5[1-5][0-9]{14}', "Mastercard Card Number"),
    (r'3[47][0-9]{13}', "American Express Card Number")
]


# Path to the Tesseract OCR executable (update with the correct path on your system)
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'


def findPII(data):
    matches = []
    for pattern, name in patterns:
        m = re.findall(pattern, data)
        if m:
            matches.append((name, m))
    return matches


def printMatches(filedir, matches):
    if len(matches) > 0:
        print(filedir)
        for name, match_list in matches:
            print(colored(f"Matched {name}:", 'red'))
            for match in match_list:
                print(colored(match,'green'))


def parseDocx(root, docs):
    for doc in docs:
        matches = None
        filedir = os.path.join(root, doc)
        try:
            with ZipFile(filedir, "r") as zip_file:
                data = zip_file.read("word/document.xml")
                matches = findPII(data.decode("utf-8", errors="ignore"))
            printMatches(filedir, matches)
        except Exception as e:
            print(f"Error parsing {filedir}: {str(e)}")


def parseText(root, txts):
    for txt in txts:
        filedir = os.path.join(root, txt)
        try:
            with open(filedir, "r", errors="ignore") as f:
                data = f.read()
            matches = findPII(data)
            printMatches(filedir, matches)
        except Exception as e:
            print(f"Error parsing {filedir}: {str(e)}")


def parsePDF(root, pdfs):
    for pdf in pdfs:
        matches = None
        filedir = os.path.join(root, pdf)
        try:
            with open(filedir, "rb") as f:
                reader = PdfReader(f, strict=False)
                if reader.is_encrypted:
                    reader.decrypt("")
                data = ""
                for page in reader.pages:
                    data += page.extract_text()
                matches = findPII(data)
            printMatches(filedir, matches)
        except Exception as e:
            print(f"Error parsing {filedir}: {str(e)}")


def parseImage(root, images):
    for image in images:
        matches = None
        filedir = os.path.join(root, image)
        try:
            with Image.open(filedir) as img:
                data = pytesseract.image_to_string(img)
                matches = findPII(data)
            printMatches(filedir, matches)
        except Exception as e:
            print(f"Error parsing {filedir}: {str(e)}")


txt_ext = [".txt", ".py", ".csv"]
pdf_ext = [".pdf"]
image_ext = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]


def findFiles(directory):
    for root, dirs, files in os.walk(directory):
        parseDocx(root, [f for f in files if f.endswith(".docx")])
        for ext in txt_ext:
            parseText(root, [f for f in files if f.endswith(ext)])
        for ext in pdf_ext:
            parsePDF(root, [f for f in files if f.endswith(ext)])
        for ext in image_ext:
            parseImage(root, [f for f in files if f.endswith(ext)])


if __name__ == "__main__":
    directory = input("Enter the directory path to search for files: ")
    directory = os.path.abspath(directory)
    if os.path.isdir(directory):
        findFiles(directory)
    else:
        print("Invalid directory path. Please provide a valid directory.")
