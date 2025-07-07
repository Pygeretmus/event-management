from django.db import IntegrityError
from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import set_rollback


def flatten_errors(detail):
    if isinstance(detail, list):
        if isinstance(detail[0], dict):
            return {x: flatten_errors(y) for z in detail for x, y in z.items()}
        else:
            return " ".join(str(e) for e in detail)
    elif isinstance(detail, dict):
        return {k: flatten_errors(v) for k, v in detail.items()}
    return str(detail)


def exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound(*(exc.args))
    elif isinstance(exc, IntegrityError):
        exc = exceptions.APIException(*(exc.args))

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = f"{exc.wait}"

        errors = flatten_errors(exc.detail)
        data = {"message": "Validation error", "errors": errors} if isinstance(errors, dict) else {"message": errors}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None
