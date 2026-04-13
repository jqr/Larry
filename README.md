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

## Step 1: Install Docker Desktop

Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/). Follow the installer prompts and restart your computer if asked. Once installed, open Docker Desktop and wait for it to say "Docker is running" in the bottom-left corner before continuing.

## Step 2: Download This Tool

1. Go to [the project page on GitHub](https://github.com/jqr/Larry)
2. Click the green **Code** button, then click **Download ZIP**
3. Open the downloaded ZIP file and extract it to a folder you'll remember (e.g. `C:\Users\YourName\Desktop\Larry`)

## Step 3: Build the Tool (One Time)

1. Open **PowerShell** — press the Windows key, type `powershell`, and hit Enter
2. Navigate to the folder you extracted:
   ```powershell
   cd C:\Users\YourName\Desktop\Larry
   ```
3. Build the tool:
   ```powershell
   docker build -t screenshot-to-csv .
   ```
   This will take a minute or two the first time. You only need to do this once.

## Step 4: Run It

Copy your screenshots into a folder called `screenshots` inside the project folder (e.g. `C:\Users\YourName\Desktop\Larry\screenshots\`). Then run:

```powershell
docker run --rm -v ${PWD}\screenshots:/data screenshot-to-csv
```

When it finishes, you'll find `output.csv` inside your `screenshots` folder. Open it with Excel or any spreadsheet app.

You can also point it at screenshots anywhere on your computer using a full path:

```powershell
docker run --rm -v C:\Users\YourName\Desktop\my-screenshots:/data screenshot-to-csv
```

## Advanced: Custom Search Patterns

By default, the tool looks for text like "Device ID: ABC123" and "Phone: 555-123-4567" in your screenshots. If your screenshots use different labels, you can tell the tool what to look for by setting custom patterns.

| Variable | What it controls | Default |
|---|---|---|
| `DEVICE_ID_REGEX` | How to find the device ID | Looks for "Device ID", "IMEI", or "Serial" followed by the ID |
| `PHONE_REGEX` | How to find the phone number | Looks for "Phone", "Mobile", "Cell", or "Tel" followed by the number |

Example — if your screenshots just say "ID:" instead of "Device ID:":

```powershell
docker run --rm `
  -e DEVICE_ID_REGEX='(?i)ID[\s:=]*([A-Z0-9\-]+)' `
  -e PHONE_REGEX='(\+?\d[\d\-]{9,})' `
  -v ${PWD}\screenshots:/data screenshot-to-csv
```

If you're not sure what the tool is "seeing" in a screenshot, you can check the raw text it reads from an image:

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

**"No image files found"**
Make sure your screenshots folder actually contains image files (PNG, JPG, etc.) and that you typed the path correctly.

**"no device_id/phone pair detected" on most files**
The tool couldn't find a device ID or phone number in the screenshot text. Your screenshots might use different labels than the defaults. See [Custom Search Patterns](#advanced-custom-search-patterns) above to adjust what the tool looks for.

**"path not found" or the tool says the folder is empty**
Make sure you're running the command from inside the project folder (the one with the `Dockerfile`). Use `cd` to navigate there first. You can also try using a full path instead: `-v C:\Users\YourName\Desktop\screenshots:/data`

**The text it reads is garbled or wrong**
OCR works best on clean, high-resolution screenshots. If your screenshots are small or blurry, try zooming in or taking higher-quality captures. Cropping to just the relevant area also helps.

**Pairs are mismatched (wrong phone number with wrong device ID)**
The tool matches the first device ID it finds with the first phone number, the second with the second, and so on. If a screenshot has multiple pairs, they need to appear in a consistent top-to-bottom order.
