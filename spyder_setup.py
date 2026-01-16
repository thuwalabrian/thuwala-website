# spyder_setup.py
import sys
import os

# Path to your virtual environment
venv_path = r"C:\Users\DMZ\Desktop\thuwala-website\thuwala"

if os.path.exists(venv_path):
    # Add site-packages to path
    site_packages = os.path.join(venv_path, "Lib", "site-packages")
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)
        print(f"✓ Added: {site_packages}")

    # Set Python executable
    python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    if os.path.exists(python_exe):
        print(f"✓ Python: {python_exe}")

    print(f"✓ Virtual environment: {venv_path}")
    print(f"✓ Python version: {sys.version}")
else:
    print("✗ Virtual environment not found at:", venv_path)
