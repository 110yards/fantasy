

from typing import List, Optional
from xmlrpc.client import Boolean
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from yards_py.core.abort import abort_unauthorized


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    key: str = None
    anonymous_routes: List[str] = None

    @classmethod
    def setup(cls, key: str, anonymous_routes: Optional[List[str]] = None):
        cls.key = key
        cls.anonymous_routes = anonymous_routes

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        assert self.key, "Key not set, call setup during startup."

        key = request.query_params.get("key", None)

        if key == self.key or self.anonymous_allowed(request):
            return await call_next(request)
        else:
            abort_unauthorized()

    def anonymous_allowed(self, request: Request) -> Boolean:
        path = request.scope.get("path", "")

        if path.endswith("/"):
            path = path[:-1]

        if path in self.anonymous_routes:
            return True

        return False
