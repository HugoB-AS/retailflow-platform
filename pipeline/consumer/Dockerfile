FROM python:3.11-slim

WORKDIR /app

COPY pipeline/requirements.txt /app/pipeline/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/pipeline/requirements.txt

COPY pipeline /app/pipeline

CMD ["python", "pipeline/consumer/event_consumer.py"]
