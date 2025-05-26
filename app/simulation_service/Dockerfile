FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python","-u", "Test_simulation.py"]
