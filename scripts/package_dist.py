#!/usr/bin/env python3
"""
Cross-Platform Distribution Packaging Script for RemindMe PWA
Builds:
1. Standard Python Wheel (.whl) & Source Archive (.tar.gz)
2. Portable Zero-Config ZIP Archive with Windows, macOS & Linux launchers
"""

import os
import sys
import shutil
import zipfile
import hashlib
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
VERSION = "0.3.0"

def get_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def clean():
    print("[*] Cleaning build artifacts...")
    for folder in ["build", "dist", "remindme_pwa.egg-info"]:
        path = os.path.join(PROJECT_ROOT, folder)
        if os.path.exists(path):
            shutil.rmtree(path)
    os.makedirs(DIST_DIR, exist_ok=True)

def build_python_packages():
    print("[*] Building Python wheel and source distribution...")
    cmd = [sys.executable, "setup.py", "sdist", "bdist_wheel"]
    subprocess.check_call(cmd, cwd=PROJECT_ROOT)

def build_portable_zip():
    print("[*] Building cross-platform portable ZIP distribution...")
    zip_filename = f"remindme-v{VERSION}-portable.zip"
    zip_path = os.path.join(DIST_DIR, zip_filename)

    included_files = [
        "README.md",
        "FAQ.md",
        "requirements.txt",
        "run.py",
        "launch.sh",
        "launch.bat",
        "launch.ps1",
    ]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in included_files:
            fpath = os.path.join(PROJECT_ROOT, fname)
            if os.path.exists(fpath):
                zf.write(fpath, arcname=f"remindme/{fname}")

        # Walk app/ directory
        app_dir = os.path.join(PROJECT_ROOT, "app")
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                if "__pycache__" in root or file.endswith((".pyc", ".pyo")):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, PROJECT_ROOT)
                zf.write(full_path, arcname=f"remindme/{rel_path}")

    return zip_path

def main():
    clean()
    build_python_packages()
    build_portable_zip()

    print("\n==================================================================")
    print(f" Distribution Packages Generated Successfully for v{VERSION}")
    print("==================================================================")
    print(f"{'Filename':<42} {'Size':<10} {'SHA-256 Checksum'}")
    print("-" * 115)
    for fname in sorted(os.listdir(DIST_DIR)):
        fpath = os.path.join(DIST_DIR, fname)
        size_kb = f"{os.path.getsize(fpath) / 1024:.1f} KB"
        checksum = get_sha256(fpath)
        print(f"{fname:<42} {size_kb:<10} {checksum}")
    print("==================================================================\n")

if __name__ == "__main__":
    main()
