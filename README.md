# Screenshot to CSV

Extract device ID and phone number pairs from screenshots using Claude's vision.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

## Usage

```bash
# Put screenshots in a folder, then:
python screenshot_to_csv.py ./screenshots

# Custom output path:
python screenshot_to_csv.py ./screenshots -o results.csv

# Adjust batch size (images per API call, default 5):
python screenshot_to_csv.py ./screenshots -b 3
```

## Output

Produces a CSV with columns: `device_id`, `phone_number`
