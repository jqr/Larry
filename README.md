# Screenshot to CSV

Extract device ID and phone number pairs from screenshots using local OCR (Tesseract). Free, no API keys needed.

## Quick Start (Docker)

```bash
docker build -t screenshot-to-csv .

# Drop screenshots in a folder and run:
docker run --rm -v ./screenshots:/data screenshot-to-csv
# Output: ./screenshots/output.csv
```

## Custom Regex via Environment Variables

```bash
docker run --rm \
  -e DEVICE_ID_REGEX='(?i)ID[\s:=]*([A-Z0-9\-]+)' \
  -e PHONE_REGEX='(\+?\d[\d\-]{9,})' \
  -v ./screenshots:/data screenshot-to-csv
```

| Variable | Description | Default |
|---|---|---|
| `DEVICE_ID_REGEX` | Regex with one capture group for device ID | Matches labels like "Device ID", "IMEI", "Serial" |
| `PHONE_REGEX` | Regex with one capture group for phone number | Matches labeled and raw US phone numbers |

## Local Setup (without Docker)

```bash
# Install Tesseract OCR engine:
# Ubuntu/Debian:
sudo apt install tesseract-ocr
# macOS:
brew install tesseract

# Install Python dependencies:
pip install -r requirements.txt

# Run:
python screenshot_to_csv.py ./screenshots -o output.csv
```

## Output

Produces a CSV with columns: `device_id`, `phone_number`
