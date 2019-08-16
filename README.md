# Simple Use-case

## Start redis with docker compose
```bash
docker-compose up -d
```

## Setup Redis
Set a `value` for key `test`
```bash
SET testkey testvalue
```

Example:
```
docker-compose exec redis /opt/bitnami/redis/bin/redis-cli
127.0.0.1:6379> SET test testvalue
OK
```

## Start aiohttp application
Start the aiohttp application on another terminal
```bash
gunicorn app:app --worker-class aiohttp.GunicornWebWorker --workers=6 --reload
```

This means, the application workers subscribe to a redis channel called `news`.

Call the http config endpoint to see the current config values:
```bash
$> curl localhost:8000/config
{}
```

## Publish a message to the news channel
Go back to the redis-cli terminal and publish a update for the `testkey`.
```bash
127.0.0.1:6379> PUBLISH news "testkey"
(integer) 4
```

## Query the /config endpoint again
```bash
$> curl localhost:8000/config
{"testkey":"testvalue"}
```