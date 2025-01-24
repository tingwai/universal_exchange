FROM python:3.10

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY tickers.yaml .
COPY websocket_consumer.py .
COPY pre_populate_redis.py .

CMD ["python", "websocket_consumer.py"]
