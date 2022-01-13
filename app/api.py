from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware  # CORS
from starlette.exceptions import HTTPException as StarletteHTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # OTEL
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from datetime import datetime, timezone
import logging
import os
from app import config, model
from app.tools import logger_extra

# logger
logger = logging.getLogger(config.APP_NAME)

# OTEL exporter
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)

# Tracing provider
tracer_provider = TracerProvider()
resource = Resource(attributes={"service.name": config.APP_NAME})
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(span_processor)
tracer = trace.get_tracer(__name__)


# Endpoints groups definition
tags_metadata = [
    {
        "name": "sample",
        "description": "Some sample description of sample endpoints",
    },
    {"name": "health", "description": "Application healthchecks"},
    {"name": "docs", "description": "Application doccumentation"},
]

# fastAPI application
app_version = os.getenv("VERSION")
if not app_version:
    app_version = "local"

app = FastAPI(
    title="Sample fastAPI application",
    docs_url="/",
    description=config.API_SUMMARY,
    openapi_tags=tags_metadata,
    version=app_version,
)
start_date = datetime.now(timezone.utc)
logger.info(f"Uruchomiłem aplikację {config.APP_NAME} w wersji {app_version}")

# CORS
origins = ["http://localhost"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus instrumentation
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(
    app, include_in_schema=True, should_gzip=True, tags=["health"], summary="metryki Prometheusa"
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    logger.error(f"Error {exc.status_code}: {str(exc.detail)}", extra=logger_extra(request))
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Błąd walidacji danych: {str(exc)}", extra=logger_extra(request))
    return await request_validation_exception_handler(request, exc)


@app.get("/docs", summary="Doccumentation", status_code=307, response_class=Response, tags=["docs"])
async def redirect():
    return RedirectResponse("/")


@app.get("/health", summary="Healthcheck", response_model=model.HealthCheck, tags=["health"])
def health():
    return {
        "status": "Server available",
        "up_since": str(start_date),
        "uptime": str(datetime.now(timezone.utc) - start_date),
    }


@app.post(
    "/sample",
    summary="POST sample",
    response_model=model.SampleAnswer,
    tags=["sample"],
)
def sample(input: model.SampleInput):
    return {"answer": "This is a sample answer", "param_received": input.input_text}


@app.get("/sample2", summary="GET sample", response_model=model.SampleAnswer, tags=["sample"])
def sample2(input_text: str):
    return {"answer": "This is a second sample answer", "param_received": input_text}


# OpenTelemetry instrumentation
FastAPIInstrumentor.instrument_app(app, tracer_provider=trace, excluded_urls="health,metrics")
