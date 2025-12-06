"""Entry point to run the AI Trading Copilot FastAPI server.

Usage (from repo root):

    uvicorn main:app --reload

or:

    python -m uvicorn main:app --reload
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from src.v1_0.api.server import app as fastapi_app


# Load environment variables from .env if present
load_dotenv()

# Expose FastAPI app for uvicorn
app: FastAPI = fastapi_app


if __name__ == "__main__":
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
