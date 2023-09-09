# Copyright 2023 University of Stuttgart
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# originally from <https://github.com/buehlefs/flask-template/>


"""Module containing JWT security features for the API."""
import inspect
import warnings
from copy import deepcopy
from datetime import timedelta
from functools import wraps
from os import environ
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from warnings import warn

import jwt
from apispec.core import APISpec
from apispec.utils import deepupdate
from flask.app import Flask
from flask.globals import request
from flask_smorest import Api, abort
from jwt import PyJWKClient, InvalidTokenError

"""Basic JWT security scheme."""
JWT_SCHEME = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT",
    "description": "The jwt access token as returned by login or refresh.",
}

"""Security schemes to be added to the swagger.json api documentation."""
SECURITY_SCHEMES = {
    "jwt": JWT_SCHEME,
}

jwks_client = None
if "JWKS_URL" in environ:
    jwks_client = PyJWKClient(environ["JWKS_URL"], cache_keys=True)

RT = TypeVar("RT")


class JWTMixin:
    """Extend Blueprint to add security documentation and jwt handling"""

    def _validate_request(self, optional):
        auth_header = request.headers.get("Authorization")
        if auth_header is None:
            if optional:
                return None
            abort(401, message="Authorization header missing")
        BEARER = "Bearer "
        if not auth_header.startswith(BEARER):
            abort(401, message="Not a bearer token")
        bearer_token = auth_header[len(BEARER) :]
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(bearer_token)
            payload = jwt.decode(
                bearer_token,
                signing_key.key,
                algorithms=["RS256"],
                leeway=timedelta(minutes=4),
                options={"verify_exp": True, "verify_nbf": True, "verify_aud": False, "verify_iss": False},
            )
            return payload.get("sub")
        except InvalidTokenError as e:
            abort(401, message="Invalid Authorization Token", exc=e)

    def require_jwt(
        self,
        security_scheme: Union[str, Dict[str, List[Any]]] = "jwt",
        optional: bool = False,
    ) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
        """Decorator validating jwt tokens and documenting them for openapi specification (only version 3...)."""
        if isinstance(security_scheme, str):
            security_scheme = {security_scheme: []}

        def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
            # map to names that are less likely to have collisions with user defined arguments!
            _jwt_optional = optional
            # Check if view function accepts a jwt_subject as named parameter
            signature = inspect.signature(func)
            pass_jwt_subject = any(
                p.name == "jwt_subject" or p.kind == inspect.Parameter.VAR_KEYWORD
                for p in signature.parameters.values()
            )

            @wraps(func)
            def wrapper(*args: Any, **kwargs) -> RT:
                if jwks_client is None:
                    warnings.warn("Skipping JWT check because not JWKS Url is set")
                    jwt_subject = None
                else:
                    jwt_subject = self._validate_request(_jwt_optional)
                if pass_jwt_subject:
                    kwargs["jwt_subject"] = jwt_subject
                return func(*args, **kwargs)

            # Store doc in wrapper function
            # The deepcopy avoids modifying the wrapped function doc
            wrapper._apidoc = deepcopy(getattr(func, "_apidoc", {}))
            security_schemes = wrapper._apidoc.setdefault("security", [])
            if _jwt_optional:
                # also add empty security scheme for optional jwt tokens
                security_schemes.append({})
            security_schemes.append(security_scheme)

            return wrapper

        return decorator

    def _prepare_security_doc(
        self,
        doc: Dict[str, Any],
        doc_info: Dict[str, Any],
        *,
        api: Api,
        app: Flask,
        spec: APISpec,
        method: str,
        **kwargs,
    ):
        """Actually prepare the documentation."""
        operation: Optional[List[Dict[str, List[Any]]]] = doc_info.get("security")
        if operation:
            available_schemas: Dict[str, Any] = spec.to_dict().get("components").get("securitySchemes")
            for scheme in operation:
                if not scheme:
                    continue  # encountered empty schema for optional security
                schema_name = next(iter(scheme.keys()))
                if schema_name not in available_schemas:
                    warn(f"The schema '{scheme}' is not specified in the available securitySchemes.")
            doc = deepupdate(doc, {"security": operation})
        return doc
