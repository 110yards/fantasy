from api.app.domain.repositories.user_repository import create_user_repository
from typing import List, Union
from api.app.config.settings import get_settings
from api.app.core.role import Role
from api.app.core.abort import abort_unauthorized
from fastapi import Request
from firebase_admin import auth
from api.app.core.logging import Logger
from functools import wraps
from starlette_context import context

anonymous_endpoints = [
    "",
    "/login",
    "/user/register/email",
    "/user/exists",
]

anonymous_prefixes = [
    "/projection",
    "/score",
]

api_key_endpoints = [
    "/league/subscriptions",
    "/system/games",
    "/system/games/all",
    "/system/players",
    "/system/league_command",
    "/system/smoke_test",
    "/system/configure",
    "/system/end_of_day",
    "/system/end_of_week",
]


def check_token(req: Request):
    if req.method == "OPTIONS":  # don't check auth for CORS requests
        return

    if requires_key(req):
        if __check_api_key(req):
            return
    else:
        if __get_token(req):
            return

    if anonymous_allowed(req):
        return

    abort_unauthorized()


def anonymous_allowed(req: Request):
    path = req.scope.get("path", "")

    if path.endswith("/"):
        path = path[:-1]

    if path in anonymous_endpoints:
        return True

    for prefix in anonymous_prefixes:
        if path.startswith(prefix):
            return True

    return False


def requires_key(req: Request):
    path = req.scope.get("path", "")

    if path.endswith("/"):
        path = path[:-1]

    return path in api_key_endpoints


def __get_token(request: Request):
    if "Authorization" not in request.headers:
        return None

    header = request.headers["Authorization"]

    try:
        parts = header.split(" ")
        if len(parts) < 2:
            Logger.warn("Invalid bearer token (less than 2 parts)")
            return None

        token = parts[1]
        # Logger.info(token)
        token = auth.verify_id_token(token, check_revoked=True)
        uid = token["uid"]
        request.state.uid = uid
        context.data["user_id"] = uid
        return token

    except auth.ExpiredIdTokenError:
        Logger.warn("Expired token encountered")
    except auth.InvalidIdTokenError:
        Logger.warn("Invalid token encountered")
    except BaseException as ex:
        Logger.error("Exception occurred while decoding token", exc_info=ex)
        return None


def get_current_user_id(request: Request) -> str:
    return request.state.uid


def __check_api_key(request: Request) -> dict:
    key = request.query_params.get("key", None)

    try:
        config = get_settings()
        return key == config.api_key
    except Exception as ex:
        Logger.error("Error occurred while checking api key for request", exc_info=ex)
        return None


def require_role(roles: Union[str, List[Role]], **kwargs):
    '''
    request: Request must be in the route params
    '''
    def decorator(function):
        @wraps(function)
        async def wrapper(**kwargs):
            request = kwargs.get("request", None)

            if not request:
                abort_unauthorized()

            current_user_id = get_current_user_id(request)
            if not current_user_id:
                abort_unauthorized()

            # user_roles_repo = create_user_roles_repository()
            user_repo = create_user_repository()

            roles_to_check = roles
            if not isinstance(roles, List):
                roles_to_check = [roles]

            allowed = False
            # user_roles = user_roles_repo.get(current_user_id)
            user = user_repo.get(current_user_id)

            if not user:
                return abort_unauthorized()

            for role in roles_to_check:
                # this could be better
                if role == Role.admin and user.is_admin:
                    allowed = True
                    break

            if not allowed:
                abort_unauthorized()

            return await function(**kwargs)
        return wrapper
    return decorator
