#!/usr/bin/env python3
"""
Extract device ID and phone number pairs from screenshots and output as CSV.

Uses Tesseract OCR — fully local and free. No API keys needed.

Usage:
    python screenshot_to_csv.py <screenshot_dir> [--output output.csv]

    Or via Docker:
    docker run --rm -v ./screenshots:/data screenshot-to-csv

Configure regex patterns via environment variables:
    DEVICE_ID_REGEX  - regex with one capture group for the device ID
    PHONE_REGEX      - regex with one capture group for the phone number
"""

import csv
import os
import re
import sys
from pathlib import Path

import pytesseract
from PIL import Image

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff"}

DEFAULT_DEVICE_ID_REGEX = (
    r"(?i)(?:device\s*(?:id)?|dev\s*id|IMEI|serial)[\s:=]*([A-Za-z0-9\-_]+)"
)
DEFAULT_PHONE_REGEX = (
    r"(?i)(?:phone|number|ph|mobile|cell|tel)[\s:=]*([\+]?[\d\s\-\(\)\.]{7,20})"
    r"|"
    r"((?:\+?1?[\s\-\.]?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}))"
)


def build_patterns() -> tuple[re.Pattern, re.Pattern]:
    device_regex = os.environ.get("DEVICE_ID_REGEX", DEFAULT_DEVICE_ID_REGEX)
    phone_regex = os.environ.get("PHONE_REGEX", DEFAULT_PHONE_REGEX)

    try:
        device_pat = re.compile(device_regex)
    except re.error as e:
        print(f"Error: invalid DEVICE_ID_REGEX: {e}")
        sys.exit(1)

    try:
        phone_pat = re.compile(phone_regex, re.IGNORECASE)
    except re.error as e:
        print(f"Error: invalid PHONE_REGEX: {e}")
        sys.exit(1)

    return device_pat, phone_pat


def normalize_phone(raw: str) -> str:
    """Strip formatting from a phone number, keeping leading +."""
    return re.sub(r"[^\d+]", "", raw.strip())


def extract_pairs(
    text: str, device_pat: re.Pattern, phone_pat: re.Pattern
) -> list[tuple[str, str]]:
    """Find device ID and phone number pairs from OCR text."""
    device_ids = device_pat.findall(text)

    phone_matches = phone_pat.findall(text)
    phones = []
    for match in phone_matches:
        # Handle both single-group custom regex and multi-group default regex
        if isinstance(match, tuple):
            raw = next((g for g in match if g), "")
        else:
            raw = match
        normalized = normalize_phone(raw)
        if len(normalized.replace("+", "")) >= 7:
            phones.append(normalized)

    return list(zip(device_ids, phones))


def ocr_image(path: Path) -> str:
    """Run Tesseract OCR on a single image."""
    img = Image.open(path)
    return pytesseract.image_to_string(img)


def process_screenshots(
    screenshot_dir: Path,
    output_path: Path,
    device_pat: re.Pattern,
    phone_pat: re.Pattern,
):
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
            pairs = extract_pairs(text, device_pat, phone_pat)
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
    parser.add_argument(
        "screenshot_dir", type=Path, help="Directory containing screenshots"
    )
    parser.add_argument(
        "--output", "-o", type=Path, default=Path("output.csv"),
        help="Output CSV path (default: output.csv)",
    )
    args = parser.parse_args()

    if not args.screenshot_dir.is_dir():
        print(f"Error: {args.screenshot_dir} is not a directory")
        sys.exit(1)

    device_pat, phone_pat = build_patterns()

    if os.environ.get("DEVICE_ID_REGEX") or os.environ.get("PHONE_REGEX"):
        print("Using custom regex patterns from environment")

    process_screenshots(args.screenshot_dir, args.output, device_pat, phone_pat)


if __name__ == "__main__":
    main()
