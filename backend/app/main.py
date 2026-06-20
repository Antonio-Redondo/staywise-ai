"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.middleware import ExceptionMiddleware

# Observability init (Sentry + LangSmith)
try:
    from app.observability import init_observability
    init_observability()
except Exception:
    # Observability is best-effort; don't block startup if libs missing
    pass

# Simple in-memory rate limiter for dev/testing
from collections import defaultdict
import time

_REQUEST_COUNTS = defaultdict(list)
RATE_LIMIT = 60  # requests
RATE_WINDOW = 3600  # seconds

def rate_limited(key: str) -> bool:
    now = time.time()
    window = _REQUEST_COUNTS[key]
    # drop old
    while window and window[0] < now - RATE_WINDOW:
        window.pop(0)
    if len(window) >= RATE_LIMIT:
        return True
    window.append(now)
    return False

app = FastAPI(
    title="StayWiseAI Backend",
    description="Housing recommendation engine API",
    version="0.1.0",
)

# Routes
app.include_router(router)
app.add_middleware(ExceptionMiddleware)


@app.middleware("http")
async def check_rate_limit(request, call_next):
    key = request.client.host if request.client else "anon"
    if rate_limited(key):
        from fastapi.responses import JSONResponse

        return JSONResponse({"error": "rate limit exceeded"}, status_code=429)
    return await call_next(request)


# CORS middleware — added LAST so it is the outermost layer. This ensures the
# Access-Control-Allow-Origin header is attached to every response, including
# errors raised by ExceptionMiddleware and 429s from the rate limiter; otherwise
# the browser blocks those responses and the fetch rejects with "Failed to fetch".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://staywise.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
