#!/usr/bin/env python3
"""
Extract device ID and phone number pairs from screenshots and output as CSV.

Usage:
    python screenshot_to_csv.py <screenshot_dir> [--output output.csv]

Requires:
    pip install anthropic

Set ANTHROPIC_API_KEY environment variable before running.
"""

import anthropic
import base64
import csv
import sys
import re
from pathlib import Path

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

SYSTEM_PROMPT = (
    "You extract device IDs and phone numbers from screenshots. "
    "For each pair found, output exactly one line in the format: device_id,phone_number\n"
    "Output ONLY the comma-separated pairs, nothing else. No headers, no explanations.\n"
    "If a screenshot contains multiple pairs, output one per line.\n"
    "Normalize phone numbers to digits only (with leading + for international if present).\n"
    "If you cannot find a valid pair, output nothing."
)

BATCH_SIZE = 5


def encode_image(path: Path) -> tuple[str, str]:
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    return media_types[path.suffix.lower()], data


def build_batch_content(paths: list[Path]) -> list[dict]:
    content = []
    for path in paths:
        media_type, data = encode_image(path)
        content.append(
            {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": data},
            }
        )
    content.append(
        {
            "type": "text",
            "text": "Extract all device ID and phone number pairs from these screenshots.",
        }
    )
    return content


def parse_pairs(text: str) -> list[tuple[str, str]]:
    pairs = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(",", 1)
        if len(parts) == 2:
            device_id = parts[0].strip()
            phone = parts[1].strip()
            if device_id and phone:
                pairs.append((device_id, phone))
    return pairs


def process_screenshots(screenshot_dir: Path, output_path: Path):
    client = anthropic.Anthropic()

    image_files = sorted(
        f for f in screenshot_dir.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not image_files:
        print(f"No image files found in {screenshot_dir}")
        sys.exit(1)

    print(f"Found {len(image_files)} screenshots to process")

    all_pairs = []
    errors = []

    for i in range(0, len(image_files), BATCH_SIZE):
        batch = image_files[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(image_files) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} images)...")

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_batch_content(batch)}],
            )
            text = response.content[0].text
            pairs = parse_pairs(text)
            all_pairs.extend(pairs)
            print(f"  Extracted {len(pairs)} pairs")
        except Exception as e:
            error_msg = f"Batch {batch_num} failed: {e}"
            print(f"  ERROR: {error_msg}")
            errors.append(error_msg)
            # Fall back to processing individually
            for path in batch:
                try:
                    media_type, data = encode_image(path)
                    response = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=1024,
                        system=SYSTEM_PROMPT,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": media_type,
                                            "data": data,
                                        },
                                    },
                                    {
                                        "type": "text",
                                        "text": "Extract the device ID and phone number pair from this screenshot.",
                                    },
                                ],
                            }
                        ],
                    )
                    text = response.content[0].text
                    pairs = parse_pairs(text)
                    all_pairs.extend(pairs)
                except Exception as e2:
                    print(f"  ERROR on {path.name}: {e2}")
                    errors.append(f"{path.name}: {e2}")

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["device_id", "phone_number"])
        writer.writerows(all_pairs)

    print(f"\nDone! Wrote {len(all_pairs)} pairs to {output_path}")
    if errors:
        print(f"Encountered {len(errors)} errors (see above)")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract device ID and phone number pairs from screenshots into CSV"
    )
    parser.add_argument("screenshot_dir", type=Path, help="Directory containing screenshots")
    parser.add_argument(
        "--output", "-o", type=Path, default=Path("output.csv"), help="Output CSV path (default: output.csv)"
    )
    parser.add_argument(
        "--batch-size", "-b", type=int, default=BATCH_SIZE, help=f"Images per API call (default: {BATCH_SIZE})"
    )
    args = parser.parse_args()

    if not args.screenshot_dir.is_dir():
        print(f"Error: {args.screenshot_dir} is not a directory")
        sys.exit(1)

    global BATCH_SIZE
    BATCH_SIZE = args.batch_size

    process_screenshots(args.screenshot_dir, args.output)


if __name__ == "__main__":
    main()
