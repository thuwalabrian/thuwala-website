# check_env.py
import sys
import os

print("=" * 50)
print("THUWALA CO. - ENVIRONMENT CHECK")
print("=" * 50)

# Check Python
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Virtual env: {'thuwala' in sys.executable}")

# Check critical packages
packages = {
    "Flask": "flask",
    "Flask-SQLAlchemy": "flask_sqlalchemy",
    "Flask-Login": "flask_login",
    "Flask-WTF": "flask_wtf",
    "Werkzeug": "werkzeug",
}

print("\n📦 Checking packages:")
for name, module in packages.items():
    try:
        __import__(module)
        version = (
            sys.modules[module].__version__
            if hasattr(sys.modules[module], "__version__")
            else "OK"
        )
        print(f"  ✓ {name}: {version}")
    except ImportError:
        print(f"  ✗ {name}: MISSING")

# Check if we're in the right directory
print(f"\n📁 Working directory: {os.getcwd()}")
print(f"📁 Project folder: {os.path.basename(os.getcwd())}")

print("\n" + "=" * 50)
print("✅ Ready to run: python app.py")
print("=" * 50)
