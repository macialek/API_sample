# API_sample
fastAPI + OpenTelemetry + Prometheus + JAEGER + CORS

## Available front
* [sample API](http://127.0.0.1:8000/)
* [Jaeger GUI](http://127.0.0.1:16686/)
* [Prometheus GUI](http://127.0.0.1:9090/)

## Build instruction
### Requirements:
* Docker
### Running
```docker compose up```

## Development
### Requirements
* Poetry 1.1.12
* Python 3.9
## Enviroment creation
```poetry install```
## Running api only inside enviroment
```poetry run uvicorn --host=0.0.0.0 --port=8000 app.api:app```