FROM python:3.9-slim

WORKDIR /app/reputation_service

COPY . .

RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "reputation.py"]
