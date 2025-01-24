from dash import Dash, Input, Output, callback, dcc, dash_table, html
import os
import pandas as pd
import plotly.express as px
import redis
import time
import yaml

host = os.getenv('REDIS_STACK_SERVICE_HOST', 'localhost')
port = int(os.getenv('REDIS_STACK_SERVICE_PORT', 6379))
r = redis.Redis(host=host, port=port)

tickers = yaml.safe_load(open('tickers.yaml'))

# prices are fetched from Redis and displayed on Current Prices table
current_prices = pd.DataFrame({
    'Token': [i.upper() for i in tickers],
    'Price': [f"${r.ts().get(f'price:{i}')[1]:.2f}" for i in tickers],
})

app = Dash()
app.layout = [
    html.H1(children='Market Data Dashboard', style={'textAlign': 'center'}),
    html.H2(children='Current Prices:'),
    html.Div([dash_table.DataTable(current_prices.to_dict('records'))], style={'width': '25%'}),
    html.Br(),
    html.H2(children='Historical Data:'),
    html.P(children='(select ticker + time bucket)'),
    dcc.Dropdown([i.upper() for i in tickers], 'BTCUSDT', id='ticker', style={'width': '50%'}),
    dcc.Dropdown(['all data', 'minute', 'hour', 'daily'], 'all data', id='duration', style={'width': '50%'}),
    dcc.Graph(id='graph-content')
]


# on dropdown menu input change, market data is fetched from Redis
# and displayed on Historical Data graph
@callback(
    Output('graph-content', 'figure'),
    Input('ticker', 'value'),
    Input('duration', 'value'),
)
def update_graph(ticker_value, duration_value):
    if duration_value == 'all data':
        key = f'price:{ticker_value.lower()}'
    else:
        key = f'{duration_value}AvgPrice:{ticker_value.lower()}'

    if duration_value == 'all_data' or duration_value == 'minute':
        start = int(time.time() * 1000) - 24 * 60 * 60 * 1000
    else:
        start = int(time.time() * 1000) - 72 * 60 * 60 * 1000

    end = int(time.time() * 1000)
    data = r.ts().range(key, start, end)

    df = pd.DataFrame(data, columns=['UTC Time', 'Price($)'])
    df['UTC Time'] = pd.to_datetime(df['UTC Time'], unit='ms')
    df['Price($)'] = df['Price($)']

    return px.line(df, x='UTC Time', y='Price($)')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
