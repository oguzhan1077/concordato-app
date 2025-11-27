#!/bin/sh
# Railway entrypoint script - PORT environment variable'ını kullanır
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

