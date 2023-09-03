FROM python:3.9-alpine

RUN pip install pyst2 requests

COPY sync_queue_asterisk.py /app/sync_queue_asterisk.py

WORKDIR /app

CMD ["python", "sync_queue_asterisk.py"]
