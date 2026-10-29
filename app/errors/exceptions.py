from typing import Any


class AppError(Exception):
    code = "APP_ERROR"
    message = "an application error occurred"

    def __init__(self, details: dict[str, Any] | None = None) -> None:
        self.details = details
        super().__init__(self.message)


class WorkflowNotFound(AppError):
    code = "WORKFLOW_NOT_FOUND"
    message = "workflow not found"


class WorkflowAlreadyExists(AppError):
    code = "WORKFLOW_ALREADY_EXISTS"
    message = "workflow with the same name already exists"


class ExecutionNotFound(AppError):
    code = "EXECUTION_NOT_FOUND"
    message = "execution not found"


class ExecutionFailed(AppError):
    code = "EXECUTION_FAILED"
    message = "workflow execution failed"


class InvalidWorkflowStep(AppError):
    code = "INVALID_WORKFLOW_STEP"
    message = "invalid workflow step definition"
