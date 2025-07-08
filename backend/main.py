from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timedelta,UTC
import random, string

from .models import ShortenRequest, ShortenResponse, StatsResponse, ClickInfo
from .storage import save_url, get_url, increment_click, get_clicks, shortcode_exists
import sys
sys.path.append('../logging')
from logging_middleware.log import Log

app = FastAPI()
SHORTLINK_DOMAIN = "http://short.affordmed.com/"

def generate_shortcode(length=7):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_geolocation(ip: str) -> str:
    # Dummy implementation; replace with real geo-IP lookup if needed
    return "Unknown"
@app.get("/")
async def root():
    return {
        "service": "URL Shortener",
        "status": "running",
        "endpoints": [
            {"POST": "/shorten"},
            {"GET": "/{shortcode}"},
            {"GET": "/stats/{shortcode}"}
        ]
    }
@app.post("/shorten", response_model=ShortenResponse)
async def shorten_url(req: ShortenRequest, request: Request):
    Log("backend", "info", "controller", f"Received shorten request for URL: {req.url}")

    code = req.shortcode
    if code:
        if shortcode_exists(code):
            Log("backend", "warn", "repository", f"Shortcode '{code}' already exists.")
            raise HTTPException(status_code=409, detail="Shortcode already in use.")
    else:
        for _ in range(10):
            code = generate_shortcode()
            if not shortcode_exists(code):
                break
        else:
            Log("backend", "error", "service", "Failed to generate unique shortcode.")
            raise HTTPException(status_code=500, detail="Could not generate unique shortcode.")

    expiry = datetime.utcnow() + timedelta(minutes=req.validity or 30)
    save_url(code, str(req.url), expiry)
    Log("backend", "info", "repository", f"Shortened URL stored with code: {code}")

    return ShortenResponse(shortlink=SHORTLINK_DOMAIN + code, expiry=expiry)

@app.get("/{shortcode}")
async def redirect_to_url(shortcode: str, request: Request):
    entry = get_url(shortcode)
    if not entry:
        Log("backend", "warn", "repository", f"Shortcode '{shortcode}' not found.")
        raise HTTPException(status_code=404, detail="Shortcode not found.")

    if datetime.now(UTC) > entry["expiry"]:
        Log("backend", "info", "service", f"Shortcode '{shortcode}' expired.")
        raise HTTPException(status_code=410, detail="Shortlink expired.")

    entry["click_count"] += 1
    click_info = {
        "timestamp": datetime.now(UTC).isoformat(),
        "source": request.headers.get("referer", "direct"),
        "geo": get_geolocation(request.client.host)
    }
    increment_click(shortcode, click_info)
    Log("backend", "info", "handler", f"Redirected to {entry['original_url']} for shortcode '{shortcode}'.")

    return RedirectResponse(entry["original_url"])

@app.get("/stats/{shortcode}", response_model=StatsResponse)
async def get_stats(shortcode: str):
    entry = get_url(shortcode)
    if not entry:
        Log("backend", "warn", "repository", f"Stats requested for nonexistent shortcode '{shortcode}'.")
        raise HTTPException(status_code=404, detail="Shortcode not found.")

    stats = StatsResponse(
        original_url=entry["original_url"],
        created_at=entry["created_at"],
        expiry=entry["expiry"],
        click_count=entry["click_count"],
        clicks=get_clicks(shortcode)
    )
    Log("backend", "info", "service", f"Stats retrieved for shortcode '{shortcode}'.")
    return stats

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    Log("backend", "error", "handler", f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )