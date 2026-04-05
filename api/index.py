import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app
from fastapi import Request
from fastapi.responses import JSONResponse

# Vercel serverless function handler
async def handler(request: Request):
    return await app(request.scope, receive, send)

# For Vercel
app_handler = app

# Export for Vercel
__all__ = ["app_handler", "handler"]
