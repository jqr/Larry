FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY screenshot_to_csv.py /app/screenshot_to_csv.py

WORKDIR /data
ENTRYPOINT ["python", "/app/screenshot_to_csv.py", "/data", "-o", "/data/output.csv"]
