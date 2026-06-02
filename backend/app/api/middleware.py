from fastapi import Request
from fastapi.responses import JSONResponse


class ExceptionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        request = Request(scope, receive=receive)
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            response = JSONResponse({"error": str(e)}, status_code=500)
            await response(scope, receive, send)
