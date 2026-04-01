FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dcgm_exporter.py .

RUN useradd -m -u 1000 exporter && chown -R exporter:exporter /app
USER exporter

EXPOSE 9400

CMD ["python", "dcgm_exporter.py"]
