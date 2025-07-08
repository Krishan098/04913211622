# URL Shortener Microservice

## Overview
A robust, FastAPI-based microservice for shortening URLs, with built-in analytics and centralized logging via a custom logging middleware. All logs are sent to a protected remote API. The service supports custom or auto-generated shortcodes, expiry, and click analytics.

---

## Project Structure

```
04913211622/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── storage.py
│   └── analytics.py (optional, for analytics logic)
└── logging_middleware/
    ├── __init__.py
    ├── log.py
    └── security_key.json
```

---

## Features

- **Shorten URLs** with optional custom shortcode and validity period.
- **Globally unique shortcodes** (auto-generated if not provided).
- **Default expiry**: 30 minutes if not specified.
- **Redirection**: Accessing a shortlink redirects to the original URL.
- **Analytics**: Tracks click count, timestamps, source, and geo (dummy).
- **Stats endpoint**: Retrieve analytics for any shortcode.
- **Robust error handling**: Returns proper HTTP status and descriptive JSON.
- **Centralized logging**: All logs sent to a remote API via custom middleware.

---

## API Endpoints

### 1. Root

**GET /**  
Returns service info and available endpoints.

---

### 2. Shorten URL

**POST /shorten**

- **Request Body:**
  ```json
  {
    "url": "https://example.com",
    "validity": 60,           // (optional, in minutes, default: 30)
    "shortcode": "custom123"  // (optional, must be unique, alphanumeric 4-32 chars)
  }
  ```

- **Response:**
  ```json
  {
    "shortlink": "http://short.affordmed.com/AbC123x",
    "expiry": "2025-07-08T13:00:00+00:00"
  }
  ```

- **Errors:**
  - 409: Shortcode already in use
  - 400: Invalid input
  - 500: Could not generate unique shortcode

---

### 3. Redirect

**GET /{shortcode}**

- **Redirects** to the original URL if valid and not expired.
- **Errors:**
  - 404: Shortcode not found
  - 410: Shortlink expired

---

### 4. Analytics

**GET /stats/{shortcode}**

- **Response:**
  ```json
  {
    "original_url": "https://example.com",
    "created_at": "2025-07-08T12:00:00+00:00",
    "expiry": "2025-07-08T13:00:00+00:00",
    "click_count": 2,
    "clicks": [
      {
        "timestamp": "2025-07-08T12:10:00+00:00",
        "source": "direct",
        "geo": "Unknown"
      }
    ]
  }
  ```
- **Errors:**
  - 404: Shortcode not found

---

## Logging

- All logs are sent to a remote API using the `Log` function in `logging_middleware/log.py`.
- No use of Python’s built-in logging or loguru for operational logs.
- Log messages are specific and descriptive, and include context (stack, level, package, message).

---

## Usage Examples

### Shorten a URL (PowerShell)
```powershell
curl.exe -X POST "http://localhost:8000/shorten" `
  -H "Content-Type: application/json" `
  -d '{ "url": "https://example.com" }'
```

### Shorten a URL (cmd.exe)
```cmd
curl -X POST "http://localhost:8000/shorten" ^
  -H "Content-Type: application/json" ^
  -d "{\"url\": \"https://example.com\"}"
```

### Get stats
```sh
curl "http://localhost:8000/stats/AbC123x"
```

---

## Running the Service

1. **Install dependencies:**
   ```
   pip install fastapi uvicorn pydantic requests
   ```

2. **Start the server:**
   ```
   uvicorn backend.main:app --reload
   ```
   or
   ```
   fastapi dev backend\main.py
   ```

3. **Test endpoints** using curl, Postman, or the built-in Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Notes

- All shortcodes are checked for uniqueness.
- If a custom shortcode is provided, it must be alphanumeric and 4-32 characters.
- All analytics are stored in memory (for demo); use a database for production.
- Geo-location is a placeholder; integrate a real geo-IP service for accuracy.
- Logging requires a valid Bearer token in `logging_middleware/security_key.json`.

---

## Example `security_key.json`

```json
{
  "access_token": "YOUR_VALID_BEARER_TOKEN"
}
```

---

## Troubleshooting

- **401 Unauthorized in logging:** Check your Bearer token.
- **JSON decode error:** Ensure your curl JSON body is properly quoted for your shell.
- **Module import errors:** Run from the project root and use package imports.

---

**For any issues, check the FastAPI logs and the logging middleware output for details.**
