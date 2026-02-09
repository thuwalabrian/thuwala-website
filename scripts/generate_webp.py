"""Generate WebP variants for every image under static/.

Run once (or after adding new images):
    python generate_webp.py

Each .jpg / .jpeg / .png gets a sibling .webp at quality 80.
Already-existing .webp files are skipped unless --force is passed.
"""

import argparse
import glob
import os
import sys

from PIL import Image

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
EXTENSIONS = (".jpg", ".jpeg", ".png")
WEBP_QUALITY = 80  # good balance of size vs quality


def convert_to_webp(
    src_path: str, quality: int = WEBP_QUALITY, force: bool = False
) -> str | None:
    """Convert a single image to WebP. Returns the output path, or None if skipped."""
    base, _ = os.path.splitext(src_path)
    dest = base + ".webp"

    if os.path.exists(dest) and not force:
        return None  # already exists

    try:
        with Image.open(src_path) as img:
            # Convert RGBA PNGs properly (WebP supports alpha)
            if img.mode in ("RGBA", "LA"):
                img.save(dest, "WEBP", quality=quality, method=4)
            else:
                rgb = img.convert("RGB")
                rgb.save(dest, "WEBP", quality=quality, method=4)
        return dest
    except Exception as exc:
        print(f"  WARN: Could not convert {src_path}: {exc}", file=sys.stderr)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate WebP variants for static images."
    )
    parser.add_argument(
        "--force", action="store_true", help="Re-generate even if .webp already exists"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=WEBP_QUALITY,
        help="WebP quality 1-100 (default 80)",
    )
    args = parser.parse_args()

    sources: list[str] = []
    for ext in EXTENSIONS:
        sources.extend(
            glob.glob(os.path.join(STATIC_DIR, "**", f"*{ext}"), recursive=True)
        )

    print(f"Found {len(sources)} source images under {STATIC_DIR}")

    created, skipped, errors = 0, 0, 0
    for src in sorted(sources):
        result = convert_to_webp(src, quality=args.quality, force=args.force)
        rel = os.path.relpath(src, STATIC_DIR)
        if result is None and not args.force:
            skipped += 1
            print(f"  SKIP  {rel}  (webp exists)")
        elif result:
            orig_size = os.path.getsize(src)
            webp_size = os.path.getsize(result)
            saving = (1 - webp_size / orig_size) * 100 if orig_size else 0
            print(f"  OK    {rel}  →  {webp_size:,} B  ({saving:+.0f}%)")
            created += 1
        else:
            errors += 1

    print(f"\nDone: {created} created, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
