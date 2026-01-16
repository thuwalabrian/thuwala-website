# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 15:27:07 2026

@author: DMZ
"""

import subprocess
import sys

# Check Python and pip
print("Python executable:", sys.executable)

# Try different pip commands
try:
    subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    print("pip is available")
except:
    print("pip not found, trying alternative...")

# Try using conda if you have Anaconda
try:
    subprocess.check_call(["conda", "install", "-c", "anaconda", "flask"])
    print("Installed via conda")
except:
    print("Conda not available")
