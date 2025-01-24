# Efficient Market Data Consumption and Retrieval

## Motivation

Market data is an important part of an exchange whether for portfolio management, order matching, or real-time analytics. While browsing https://app.universal.xyz I noticed it takes 5-10 seconds to load the list of tokens and prices, same with fetching the historical price data for populating the graphs. 

For my task I demo'd how I would approach solving the slow fetching of ticker price market data by leveraging Redis time series for fast data retrieval to provide a more responsive user experience. To gather this market data I wrote a microservice for consuming + writing Binance websocket API to Redis.

On the frontend, all displayed numbers are retrieved live from Redis. I provide an option to retrieve "all data" which returns an excessive 52,000+ uncompressed data points in ~700ms end-to-end to demonstrate the responsiveness of using Redis. A more reasonable time bucket of 1min (1,440 data points) takes ~100ms.

## Architecture

Included Dockerfiles (images pushed to Dockerhub) and Kubernetes yaml files so entire system is deployable on Kubernetes.

- `websocket_consumer`: service for consuming real-time ticker data from Binance websocket API and writing them to Redis
  - `pre_populate_redis` (initContainer): handles initial setup of Redis time series keys and compaction rules. Also pre-populates Redis with fake data so frontend has data to display. (All data after spinning up stack will be real data from Binance).
- `market_data_frontend`: minimal Flask frontend to show current token prices and fast data retrieval from Redis for any time bucket. Each time the graph is updated, after clicking the dropdown menu, data is re-fetched from Redis on purpose to demonstrate there are minimal load times even without caching
- `redis-stack`: uses Redis time series to store ticker data and compact time series data using `TS.CREATERULE` to display for different time bucket graphs (all data, 1min, 1hr, 1day)


## Install + Run using [minikube](https://minikube.sigs.k8s.io/)

```bash
minikube start
minikube addons enable ingress
kubectl apply -f manifests
kubectl logs deployments/consumer
# wait for consumer to start, may take a few minutes for pre_populate_redis to finish populating Redis
minikube ip
> 192.xxx.xx.x  # open IP in browser to interact with frontend
```

## Ideas for improvements

- for demo purposes frontend calls Redis directly, instead frontend should call a backend API for data
- support sharding `websocket_consumer` service
- add Redis persistence
- use Redis Pub/Sub to rebroadcast market data so other parts of exchange can consume them
