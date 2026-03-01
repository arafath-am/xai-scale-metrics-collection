FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY sample_payload.json .

# Run as non-root
RUN useradd -m -u 1000 exporter && chown -R exporter:exporter /app
USER exporter

EXPOSE 8000

ENV LISTEN_HOST=0.0.0.0 \
    LISTEN_PORT=8000 \
    POLL_INTERVAL=15 \
    LOG_LEVEL=INFO

CMD ["python", "app.py"]
