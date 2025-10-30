"""
"""
from fastapi import FastAPI, Request
import time, uuid  # group std imports

from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.utils.logger import setup_logger
from app.core.redis_client import get_redis
from app.core.limiter import limiter
from app.modules.auth.routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from prometheus_fastapi_instrumentator import Instrumentator

# --------------------------------------------------------
# Initialize Loguru logger
# --------------------------------------------------------
logger = setup_logger()

# --------------------------------------------------------
# Create FastAPI app instance
# --------------------------------------------------------
app = FastAPI(
    title="MyESI API Gateway",
    version="1.0.0",
)

app = FastAPI()

Instrumentator().instrument(app).expose(app)

# --------------------------------------------------------
# Attach limiter and exception handler
# --------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# --------------------------------------------------------
# Enable CORS
# --------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (restrict in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------
# Startup & Shutdown Events
# --------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    #Initialize Redis on app startup.
    app.state.redis = get_redis()
    logger.info({"event": "startup", "msg": "Redis client initialized"})


@app.on_event("shutdown")
async def shutdown_event():
    #Graceful shutdown.
    try:
        app.state.redis.close()
    except Exception:
        pass
    logger.info({"event": "shutdown", "msg": "App shutdown"})

# --------------------------------------------------------
# Analytics and Logging Middleware
# --------------------------------------------------------
@app.middleware("http")
async def analytics_and_logging_middleware(request: Request, call_next):
    start = time.time()
    request_id = str(uuid.uuid4())
    client_ip = (
        request.client.host
        if request.client
        else request.headers.get("x-forwarded-for", "unknown")
    )

    try:
        response = await call_next(request)
    except Exception:
        latency = time.time() - start
        REQUEST_COUNT.labels(request.method, request.url.path, "500").inc()
        REQUEST_LATENCY.labels(request.method, request.url.path).observe(latency)
        raise

    latency = time.time() - start
    status = response.status_code

    # ✅ Update metrics
    REQUEST_COUNT.labels(request.method, request.url.path, str(status)).inc()
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(latency)

    return response



# --------------------------------------------------------
# Register Routers
# --------------------------------------------------------
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])


# --------------------------------------------------------
# Healthcheck Endpoint
# --------------------------------------------------------
@app.get("/")
def root():
    """Basic healthcheck route."""
    return {"status": "ok", "service": "api-gateway"}

# --------------------------------------------------------
# Prometheus Metrics
# --------------------------------------------------------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Request latency",
    ["method", "path"]
)

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

