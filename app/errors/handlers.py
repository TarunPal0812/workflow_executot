from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors.exceptions import (
    AppError,
    ExecutionFailed,
    ExecutionNotFound,
    InvalidWorkflowStep,
    WorkflowAlreadyExists,
    WorkflowNotFound,
)
from app.errors.responses import ErrorDetails, ErrorResponse

ERROR_STATUS_CODE: dict[type[AppError], int] = {
    WorkflowNotFound: status.HTTP_404_NOT_FOUND,
    ExecutionNotFound: status.HTTP_404_NOT_FOUND,
    WorkflowAlreadyExists: status.HTTP_409_CONFLICT,
    ExecutionFailed: status.HTTP_400_BAD_REQUEST,
    InvalidWorkflowStep: status.HTTP_400_BAD_REQUEST,
}


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    status_code = ERROR_STATUS_CODE.get(
        type(exc),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    response = ErrorResponse(
        error=ErrorDetails(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(mode="json"),
    )


async def unexpected_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    response = ErrorResponse(
        error=ErrorDetails(
            code="INTERNAL_SERVER_ERROR", message="Internal server error"
        )
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(mode="json"),
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    validation_errors = []
    for error in exc.errors():
        validation_errors.append(
            {
                "location": list(error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )
    response = ErrorResponse(
        error=ErrorDetails(
            code="VALIDATION_ERROR",
            message="validation fail",
            details=validation_errors,
        )
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response.model_dump(mode="json"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)

