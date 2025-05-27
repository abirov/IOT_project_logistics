FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["/bin/sh", "-c", "python mqtt_service.py & python influxservice.py"]
