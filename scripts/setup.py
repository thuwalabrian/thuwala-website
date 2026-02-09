# setup.py
import os
import sys


def setup_project():
    print("Setting up Thuwala Co. Website...")

    # Create folders
    folders = [
        "static/css",
        "static/js",
        "static/images",
        "static/uploads",
        "templates/admin",
        "instance",
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Created: {folder}")

    print("\n✅ Project setup complete!")
    print("\nNext steps:")
    print("1. Install packages: pip install -r requirements.txt")
    print("2. Run the app: python app.py")
    print("3. Open browser: http://localhost:5000")
    print("4. Admin panel: http://localhost:5000/admin/login")
    print("   Username: admin")
    print("   Password: Admin@2024")


if __name__ == "__main__":
    setup_project()
