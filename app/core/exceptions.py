"""
Domain-specific exceptions for the application.

These exceptions are raised by services and repositories.
They are independent of HTTP concerns - the routers or main.py
register FastAPI exception handlers to convert them to HTTP responses.
"""


class DomainError(Exception):
    """Base class for all domain exceptions."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    """Raised when a requested resource does not exist."""


class ForbiddenError(DomainError):
    """Raised when a user attempts an action they are not authorized to perform."""


class ConflictError(DomainError):
    """Raised when a resource conflict occurs (e.g., duplicate email)."""


class ValidationError(DomainError):
    """Raised when input validation fails (e.g., invalid ID format)."""


# ------------------------------------------------------------------------------
# FastAPI exception handlers
# ------------------------------------------------------------------------------
# These functions are registered with the FastAPI app to convert domain exceptions
# into proper HTTP responses. Registration happens in main.py or a setup function.


def register_exception_handlers(app) -> None:
    """Register all domain exception handlers on the FastAPI application."""

    from fastapi import Request, status
    from fastapi.responses import JSONResponse

    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )

    async def forbidden_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.message},
        )

    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message},
        )

    async def validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(ForbiddenError, forbidden_handler)
    app.add_exception_handler(ConflictError, conflict_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
