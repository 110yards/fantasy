from yards_py.middleware.auth_middleware import AuthMiddleware
from yards_py.middleware.logging_middleware import LoggingMiddleware

from starlette.middleware import Middleware
from starlette_context.plugins.request_id import RequestIdPlugin
from starlette_context.plugins.correlation_id import CorrelationIdPlugin
from starlette_context.middleware.context_middleware import ContextMiddleware


app_middleware = [
    Middleware(
        ContextMiddleware,
        plugins=(
            RequestIdPlugin(),
            CorrelationIdPlugin(),
        ),
    ),
    Middleware(
        LoggingMiddleware
    ),
    Middleware(
        AuthMiddleware
    ),
]
