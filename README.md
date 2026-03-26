# Screenshot to CSV

Bulk-extract device ID and phone number pairs from screenshots into a CSV file.

Point it at a folder of screenshots — each containing a device ID and phone number pairing — and it OCRs every image, pulls out the data, and writes a clean CSV. Handles hundreds of screenshots in one run. Everything runs locally using [Tesseract OCR](https://github.com/tesseract-ocr/tesseract); no API keys, no cloud services, completely free.

## How It Works

1. Scans a directory for image files (PNG, JPG, JPEG, GIF, WebP, BMP, TIFF)
2. Runs Tesseract OCR on each image to extract text
3. Applies regex patterns to find device IDs and phone numbers in the OCR text
4. Pairs them up positionally (first device ID with first phone number, etc.)
5. Writes all pairs to a CSV with `device_id` and `phone_number` columns

The default regex patterns recognize common labels like "Device ID", "Dev ID", "IMEI", "Serial" for device IDs, and "Phone", "Mobile", "Cell", "Tel" for phone numbers. It also picks up raw US-format phone numbers without labels. If your screenshots use different labeling, you can override the patterns via environment variables (see [Custom Regex](#custom-regex-patterns) below).

## Prerequisites

Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) and make sure it's running.

## Setup

Open PowerShell or Command Prompt in the project directory and build the image (one time):

```powershell
docker build -t screenshot-to-csv .
```

## Usage

Put your screenshots in a folder (e.g. `screenshots\`), then run:

```powershell
# PowerShell:
docker run --rm -v ${PWD}\screenshots:/data screenshot-to-csv

# Command Prompt:
docker run --rm -v %cd%\screenshots:/data screenshot-to-csv
```

The output CSV appears at `screenshots\output.csv`.

You can also use an absolute path:

```powershell
docker run --rm -v C:\Users\me\Desktop\screenshots:/data screenshot-to-csv
```

## Custom Regex Patterns

The extraction patterns are configurable via environment variables. Each regex must contain **one capture group** — the text inside `()` is what gets extracted.

| Variable | Description | Default behavior |
|---|---|---|
| `DEVICE_ID_REGEX` | Pattern to capture the device ID | Matches text after labels like "Device ID", "IMEI", "Serial" |
| `PHONE_REGEX` | Pattern to capture the phone number | Matches labeled phone numbers and raw US-format numbers |

### Examples

```powershell
# PowerShell:
docker run --rm `
  -e DEVICE_ID_REGEX='(?i)ID[\s:=]*([A-Z0-9\-]+)' `
  -e PHONE_REGEX='(\+?\d[\d\-]{9,})' `
  -v ${PWD}\screenshots:/data screenshot-to-csv
```

```cmd
:: Command Prompt:
docker run --rm ^
  -e DEVICE_ID_REGEX="(?i)ID[\s:=]*([A-Z0-9\-]+)" ^
  -e PHONE_REGEX="(\+?\d[\d\-]{9,})" ^
  -v %cd%\screenshots:/data screenshot-to-csv
```

### Writing Custom Patterns

- Use [regex101.com](https://regex101.com/) (set flavor to Python) to test patterns against sample OCR text
- The regex must have exactly **one capture group** `()` — that group's match becomes the value in the CSV
- If the OCR output isn't what you expect, run Tesseract directly on a sample image to see the raw text:
  ```powershell
  docker run --rm -v ${PWD}\screenshots:/data --entrypoint tesseract screenshot-to-csv /data/sample.png stdout
  ```

## Supported Image Formats

PNG, JPG/JPEG, GIF, WebP, BMP, TIFF

## Output Format

```csv
device_id,phone_number
ABC123,+15551234567
DEV-456,5559876543
```

Phone numbers are normalized to digits only (with leading `+` preserved for international numbers).

## Troubleshooting

| Problem | Fix |
|---|---|
| "No image files found" | Check that the directory path is correct and contains supported image types |
| "no device_id/phone pair detected" on many files | The default regex may not match your screenshot format — inspect the raw OCR output (see above) and set custom `DEVICE_ID_REGEX`/`PHONE_REGEX` |
| Docker says "path not found" or empty `/data` | Make sure you're using the right path syntax for your shell (`${PWD}` in PowerShell, `%cd%` in cmd). Or use a full absolute path like `C:\Users\me\screenshots` |
| Poor OCR accuracy | Ensure screenshots are reasonably high resolution. Cropping to just the relevant area can help. Tesseract works best on clean, high-contrast text |
| Pairs are mismatched | The tool pairs device IDs and phone numbers by position (first ID with first phone, etc.). If your screenshots contain multiple pairs, make sure the OCR reads them in the correct order — top to bottom, left to right |
