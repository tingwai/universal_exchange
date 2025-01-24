FROM python:3.10

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY tickers.yaml .
COPY market_data_frontend.py .

EXPOSE 5000
ENV FLASK_APP=market_data_frontend.py

CMD ["python", "market_data_frontend.py"]
