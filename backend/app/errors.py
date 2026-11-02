"""Centralised PostgreSQL → HTTP error mapping."""
import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from psycopg.errors import (
    RaiseException,         # P0001
    CheckViolation,         # 23514
    ForeignKeyViolation,    # 23503
    UniqueViolation,        # 23505
)

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    """Raised when a query returns no row."""
    pass


async def db_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Map database exceptions to the HTTP responses specified in API_SPEC."""
    if isinstance(exc, NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc) or "Not found"})

    if isinstance(exc, RaiseException):
        # P0001 – trigger RAISE EXCEPTION: pass message unchanged
        msg = exc.diag.message_primary or str(exc)
        return JSONResponse(status_code=400, content={"detail": msg})

    if isinstance(exc, CheckViolation):
        # 23514 – friendly message naming the field
        msg = exc.diag.message_primary or str(exc)
        return JSONResponse(status_code=400, content={"detail": msg})

    if isinstance(exc, ForeignKeyViolation):
        # 23503 – foreign key violation on delete
        return JSONResponse(
            status_code=409,
            content={"detail": "Cannot delete: this record is in use"},
        )

    if isinstance(exc, UniqueViolation):
        # 23505 – unique violation
        return JSONResponse(status_code=409, content={"detail": "Already exists"})

    # Unknown – log and return 500
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
