from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create simple FastAPI app
app = FastAPI(title="AI Call Center")

@app.get("/")
async def root():
    return JSONResponse({"message": "AI Call Center is working!"})

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "version": "1.0.0"})

# Vercel handler
def handler(request):
    return app(request.scope, receive, send)

# Export
__all__ = ["handler"]
