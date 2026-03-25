#!/usr/bin/env python3
"""
Extract device ID and phone number pairs from screenshots and output as CSV.

Uses Tesseract OCR — fully local and free. No API keys needed.

Usage:
    python screenshot_to_csv.py <screenshot_dir> [--output output.csv]

Requires:
    pip install pytesseract Pillow
    Also install Tesseract itself:
        Ubuntu/Debian: sudo apt install tesseract-ocr
        macOS:         brew install tesseract
        Windows:       https://github.com/UB-Mannheim/tesseract/wiki
"""

import csv
import re
import sys
from pathlib import Path

import pytesseract
from PIL import Image

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff"}

# Patterns to match device IDs and phone numbers.
# Adjust these if your screenshots use a different format.
DEVICE_ID_PATTERN = re.compile(
    r"(?i)(?:device\s*(?:id)?|dev\s*id|IMEI|serial)[\s:=]*([A-Za-z0-9\-_]+)"
)
PHONE_PATTERN = re.compile(
    r"(?:phone|number|ph|mobile|cell|tel)[\s:=]*([\+]?[\d\s\-\(\)\.]{7,20})"
    r"|"
    r"((?:\+?1?[\s\-\.]?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}))"  # raw phone numbers
    , re.IGNORECASE
)


def normalize_phone(raw: str) -> str:
    """Strip formatting from a phone number, keeping leading +."""
    raw = raw.strip()
    digits = re.sub(r"[^\d+]", "", raw)
    return digits


def extract_pairs(text: str) -> list[tuple[str, str]]:
    """Find device ID and phone number pairs from OCR text."""
    device_ids = DEVICE_ID_PATTERN.findall(text)
    phone_matches = PHONE_PATTERN.findall(text)

    # Each phone match has two groups (labeled vs raw); pick whichever matched
    phones = []
    for match in phone_matches:
        raw = match[0] if match[0] else match[1]
        normalized = normalize_phone(raw)
        if len(normalized.replace("+", "")) >= 7:
            phones.append(normalized)

    pairs = list(zip(device_ids, phones))
    return pairs


def ocr_image(path: Path) -> str:
    """Run Tesseract OCR on a single image."""
    img = Image.open(path)
    return pytesseract.image_to_string(img)


def process_screenshots(screenshot_dir: Path, output_path: Path):
    image_files = sorted(
        f for f in screenshot_dir.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not image_files:
        print(f"No image files found in {screenshot_dir}")
        sys.exit(1)

    print(f"Found {len(image_files)} screenshots to process")

    all_pairs = []
    errors = []

    for i, path in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] {path.name}...", end=" ", flush=True)
        try:
            text = ocr_image(path)
            pairs = extract_pairs(text)
            if pairs:
                all_pairs.extend(pairs)
                print(f"found {len(pairs)} pair(s)")
            else:
                print("no pairs found")
                errors.append(f"{path.name}: no device_id/phone pair detected")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(f"{path.name}: {e}")

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["device_id", "phone_number"])
        writer.writerows(all_pairs)

    print(f"\nDone! Wrote {len(all_pairs)} pairs to {output_path}")
    if errors:
        print(f"\n{len(errors)} warnings/errors:")
        for e in errors:
            print(f"  - {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract device ID and phone number pairs from screenshots into CSV"
    )
    parser.add_argument("screenshot_dir", type=Path, help="Directory containing screenshots")
    parser.add_argument(
        "--output", "-o", type=Path, default=Path("output.csv"), help="Output CSV path (default: output.csv)"
    )
    args = parser.parse_args()

    if not args.screenshot_dir.is_dir():
        print(f"Error: {args.screenshot_dir} is not a directory")
        sys.exit(1)

    process_screenshots(args.screenshot_dir, args.output)


if __name__ == "__main__":
    main()
