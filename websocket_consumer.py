import json
import os
import redis
import websocket
import yaml

host = os.getenv('REDIS_STACK_SERVICE_HOST', 'localhost')
port = int(os.getenv('REDIS_STACK_SERVICE_PORT', 6379))
r = redis.Redis(host=host, port=port)

tickers_file = 'tickers.yaml'


def on_message(ws, message):
    data = json.loads(message)

    ticker = data['s'].lower()
    timestamp = data['E']
    price = float(data['c'])  # convert to cents in US dollars
    print(f'Received message: {timestamp=}, {ticker=}, {price=}')

    # add ticker price to redis time series
    r.ts().add(f'price:{ticker}', timestamp, price)


def on_error(ws, error):
    print(f'Error: {error}')


def on_close(ws, close_status_code, close_msg):
    print(f'WebSocket connection closed: {close_status_code} - {close_msg}')


def on_open(ws):
    print('WebSocket connection opened')
    tickers = yaml.safe_load(open(tickers_file))
    subscribe_message = {
        'method': 'SUBSCRIBE',
        'params': [f'{i}@ticker' for i in tickers],
        'id': 1
    }
    ws.send(json.dumps(subscribe_message))


def on_ping(ws, message):
    print(f'Received ping: {message}')
    ws.send(message, websocket.ABNF.OPCODE_PONG)
    print(f'Sent pong: {message}')


if __name__ == '__main__':
    websocket.enableTrace(False)
    socket = 'wss://stream.binance.com:9443/ws'
    ws = websocket.WebSocketApp(socket,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open,
                                on_ping=on_ping)
    ws.run_forever()
