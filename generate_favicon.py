# generate_favicon.py
from PIL import Image
import os


def generate_favicons(logo_path):
    """Generate favicon files from logo image"""

    logo_dir = os.path.dirname(logo_path)

    # Required sizes for favicons
    sizes = [
        (16, 16),  # Browser tab
        (32, 32),  # Browser tab + taskbar
        (48, 48),  # Windows taskbar
        (64, 64),  # Desktop icon
        (180, 180),  # Apple touch icon
        (192, 192),  # Android/Chrome
        (512, 512),  # Splash screen
    ]

    try:
        # Open the logo image
        img = Image.open(logo_path)
        print(f"✅ Opened logo: {logo_path}")
        print(f"📐 Original size: {img.size}")

        # Convert to RGBA if not already
        if img.mode != "RGBA":
            img = img.convert("RGBA")
            print("✅ Converted to RGBA mode")

        print("\n🎨 Generating favicon files...")

        # Create .ico file (contains multiple sizes)
        icon_sizes = []
        for size in sizes[:4]:  # First 4 sizes for .ico
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_sizes.append(resized)

        # Save as .ico
        icon_path = os.path.join(logo_dir, "favicon.ico")
        icon_sizes[0].save(
            icon_path,
            format="ICO",
            sizes=[(s.width, s.height) for s in icon_sizes],
            append_images=icon_sizes[1:],
        )
        print(f"📄 Created: favicon.ico")

        # Create individual PNG files
        for width, height in sizes:
            # Resize image
            resized = img.resize((width, height), Image.Resampling.LANCZOS)

            # Save as PNG
            filename = f"logo-{width}x{height}.png"
            filepath = os.path.join(logo_dir, filename)
            resized.save(filepath, "PNG")
            print(f"🖼️  Created: {filename}")

        print("\n" + "=" * 50)
        print("🎉 FAVICON GENERATION COMPLETE!")
        print(f"📁 Files saved to: {logo_dir}")
        print("\n📋 Files created:")
        print("   - favicon.ico (multiple sizes)")
        for width, height in sizes:
            print(f"   - logo-{width}x{height}.png")
        print("\n🚀 Next: Update your base.html template")

    except FileNotFoundError:
        print(f"❌ Error: Could not find logo file at {logo_path}")
        print("Please check the file path and try again.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Use your exact favicon image path
    FAVICON_SOURCE = (
        r"C:\Users\DMZ\Desktop\thuwala-website\static\images\logo\TC Logo.png"
    )

    # Check if file exists
    if not os.path.exists(FAVICON_SOURCE):
        print(f"❌ Favicon source file not found at: {FAVICON_SOURCE}")
        print("\n📁 Please verify:")
        print("   1. The file exists at that location")
        print("   2. The filename is exactly 'TC Logo.png'")
        print("   3. The file is not corrupted")

        # Try to find the file
        print("\n🔍 Searching for similar files...")
        logo_dir = r"C:\Users\DMZ\Desktop\thuwala-website\static\images\logo"
        if os.path.exists(logo_dir):
            files = os.listdir(logo_dir)
            print(f"Files found in {logo_dir}:")
            for file in files:
                print(f"   - {file}")
    else:
        generate_favicons(FAVICON_SOURCE)
