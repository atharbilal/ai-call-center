from main import app

# Vercel needs the app to be exported
__all__ = ["app"]
handler = app

# For Vercel serverless function
def handler(request):
    return app(request)
