from app import app

# Vercel serverless function handler
async def handler(request):
    return await app(request.scope, receive, send)

# Export for Vercel
app_handler = app
__all__ = ["app_handler", "handler"]
