# Screenshot to CSV

Extract device ID and phone number pairs from screenshots using local OCR (Tesseract). Free, no API keys needed.

## Setup

```bash
# Install Tesseract OCR engine:
# Ubuntu/Debian:
sudo apt install tesseract-ocr
# macOS:
brew install tesseract

# Install Python dependencies:
pip install -r requirements.txt
```

## Usage

```bash
# Put screenshots in a folder, then:
python screenshot_to_csv.py ./screenshots

# Custom output path:
python screenshot_to_csv.py ./screenshots -o results.csv
```

## Output

Produces a CSV with columns: `device_id`, `phone_number`
