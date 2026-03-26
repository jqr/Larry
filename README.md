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

## Quick Start (Docker)

Docker is the easiest way to run this — no need to install Python or Tesseract on your machine.

```bash
# Build the image (one time):
docker build -t screenshot-to-csv .

# Run it — mount your screenshots folder to /data:
docker run --rm -v ./screenshots:/data screenshot-to-csv
```

The output CSV appears at `./screenshots/output.csv`.

### Windows (Docker Desktop)

1. Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. Open PowerShell or Command Prompt in the project directory
3. Build and run:

```powershell
docker build -t screenshot-to-csv .

# PowerShell — use ${PWD} for the current directory:
docker run --rm -v ${PWD}/screenshots:/data screenshot-to-csv

# Command Prompt — use %cd% instead:
docker run --rm -v %cd%\screenshots:/data screenshot-to-csv
```

### macOS / Linux (Docker)

```bash
docker build -t screenshot-to-csv .
docker run --rm -v ./screenshots:/data screenshot-to-csv
```

## Local Setup (without Docker)

### Linux

```bash
sudo apt install tesseract-ocr
pip install -r requirements.txt
python screenshot_to_csv.py ./screenshots -o output.csv
```

### macOS

```bash
brew install tesseract
pip install -r requirements.txt
python screenshot_to_csv.py ./screenshots -o output.csv
```

### Windows (Native)

1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Download and install the Tesseract OCR engine from [UB Mannheim's builds](https://github.com/UB-Mannheim/tesseract/wiki). During install, note the install path (default is `C:\Program Files\Tesseract-OCR`).
3. Add Tesseract to your system PATH, or set it in the environment:
   ```powershell
   $env:PATH += ";C:\Program Files\Tesseract-OCR"
   ```
4. Install Python dependencies and run:
   ```powershell
   pip install -r requirements.txt
   python screenshot_to_csv.py .\screenshots -o output.csv
   ```

If `pytesseract` can't find the Tesseract binary, you can point it directly by setting the `TESSDATA_PREFIX` environment variable or by setting the path in Python before running:
```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## CLI Options

```
python screenshot_to_csv.py <screenshot_dir> [--output output.csv]
```

| Argument | Description |
|---|---|
| `screenshot_dir` | Path to folder containing screenshot images (required) |
| `--output`, `-o` | Output CSV file path (default: `output.csv`) |

## Custom Regex Patterns

The extraction patterns are configurable via environment variables. Each regex must contain **one capture group** — the text inside `()` is what gets extracted.

| Variable | Description | Default behavior |
|---|---|---|
| `DEVICE_ID_REGEX` | Pattern to capture the device ID | Matches text after labels like "Device ID", "IMEI", "Serial" |
| `PHONE_REGEX` | Pattern to capture the phone number | Matches labeled phone numbers and raw US-format numbers |

### Examples

**Docker:**
```bash
docker run --rm \
  -e DEVICE_ID_REGEX='(?i)ID[\s:=]*([A-Z0-9\-]+)' \
  -e PHONE_REGEX='(\+?\d[\d\-]{9,})' \
  -v ./screenshots:/data screenshot-to-csv
```

**Local (Linux/macOS):**
```bash
DEVICE_ID_REGEX='(?i)ID[\s:=]*([A-Z0-9\-]+)' \
PHONE_REGEX='(\+?\d[\d\-]{9,})' \
python screenshot_to_csv.py ./screenshots
```

**Local (Windows PowerShell):**
```powershell
$env:DEVICE_ID_REGEX = '(?i)ID[\s:=]*([A-Z0-9\-]+)'
$env:PHONE_REGEX = '(\+?\d[\d\-]{9,})'
python screenshot_to_csv.py .\screenshots
```

### Writing Custom Patterns

- Use [regex101.com](https://regex101.com/) (set flavor to Python) to test patterns against sample OCR text
- The regex must have exactly **one capture group** `()` — that group's match becomes the value in the CSV
- If the OCR output isn't what you expect, run Tesseract directly on a sample image to see the raw text:
  ```bash
  # Docker:
  docker run --rm -v ./screenshots:/data --entrypoint tesseract screenshot-to-csv /data/sample.png stdout

  # Local:
  tesseract sample.png stdout
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
| Tesseract not found | Ensure Tesseract is installed and on your PATH. On Windows, verify the install path matches what `pytesseract` expects |
| Poor OCR accuracy | Ensure screenshots are reasonably high resolution. Cropping to just the relevant area can help. Tesseract works best on clean, high-contrast text |
| Pairs are mismatched | The tool pairs device IDs and phone numbers by position (first ID with first phone, etc.). If your screenshots contain multiple pairs, make sure the OCR reads them in the correct order — top to bottom, left to right |
