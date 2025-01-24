from random import random
import os
import redis
import time
import yaml

host = os.getenv('REDIS_STACK_SERVICE_HOST', 'localhost')
port = int(os.getenv('REDIS_STACK_SERVICE_PORT', 6379))
r = redis.Redis(host=host, port=port)

tickers_file = 'tickers.yaml'
tickers = yaml.safe_load(open(tickers_file))

fake_price = {
    'btcusdt': 100_000,
    'ethusdt': 3000,
    'xrpusdt': 3,
    'bnbusdt': 670,
    'solusdt': 250,
    'linkusdt': 25,
}


def setup_redis():
    for ticker in tickers:
        price_key = f'price:{ticker}'
        if not r.exists(price_key):
            r.ts().create(price_key)
            print(f'Created key {price_key}')

        # create compacted time series for (time-weighted) average price for ticker every 1 minute
        minute_key = f'minuteAvgPrice:{ticker}'
        if not r.exists(minute_key):
            r.ts().create(minute_key)
            minute_in_milliseconds = 60 * 1000
            r.ts().createrule(price_key, minute_key, 'twa', minute_in_milliseconds)
            print(f'Created key {minute_key}')

        # create compacted time series every 1 hour
        hour_key = f'hourAvgPrice:{ticker}'
        if not r.exists(hour_key):
            r.ts().create(hour_key)
            hour_in_milliseconds = 60 * 60 * 1000
            r.ts().createrule(price_key, hour_key, 'twa', hour_in_milliseconds)
            print(f'Created key {minute_key}')

        # create compacted time series every 1 day
        daily_key = f'dailyAvgPrice:{ticker}'
        if not r.exists(daily_key):
            r.ts().create(daily_key)
            day_in_milliseconds = 24 * 60 * 60 * 1000
            r.ts().createrule(price_key, daily_key, 'twa', day_in_milliseconds)
            print(f'Created key {daily_key}')

        # pre-populate redis with fake market data for past 3 days
        start = int(time.time() * 1000 - 72 * 60 * 60 * 1000)
        end = int(time.time() * 1000)

        # if data found from 72 hours ago, redis is already populated
        if r.ts().range(price_key, start, start + 5 * 60 * 1000):
            print(f'Skipping populating key {price_key}, data already found')
            continue

        # insert a data point for every 5 seconds
        hour_interval = 60 * 60 * 1000
        for t in range(start, end, hour_interval):
            # add multiple data points at once using r.ts().madd
            keys = [price_key for _ in range(60 * 60 // 5)]
            ts = [t + i * 5 * 1000 for i in range(60 * 60 // 5)]
            prices = [int(random() * fake_price[ticker] / 100 + fake_price[ticker]) for _ in range(60 * 60 // 5)]
            data = list(zip(keys, ts, prices))

            r.ts().madd(data)
            print(f'Populated key {price_key} @ timestamp={ts[0]}')


if __name__ == '__main__':
    setup_redis()
