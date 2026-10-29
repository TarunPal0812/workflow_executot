from typing import Optional
from fastapi import APIRouter, Query

from app.dependencies.workflow_dependencies import WorkflowServiceDependency
from app.errors.exceptions import ExecutionNotFound
from app.schemas.general_response_schema import SuccessResponse
from app.schemas.workflow_schem import ExecutionOut, RetryRequest
from app.utils.response import success_response

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.get("", response_model=SuccessResponse[list[ExecutionOut]])
async def list_executions(
    service: WorkflowServiceDependency,
    workflow_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    executions = await service.list_executions(
        workflow_id, status_filter, skip, limit
    )
    return success_response(
        data=executions,
        message="Executions fetched successfully",
        meta={"skip": skip, "limit": limit, "count": len(executions)},
    )


@router.get("/{execution_id}", response_model=SuccessResponse[ExecutionOut])
async def get_execution(
    execution_id: int,
    service: WorkflowServiceDependency,
):
    execution = await service.get_execution(execution_id)
    if not execution:
        raise ExecutionNotFound()
    return success_response(
        data=execution,
        message="Execution fetched successfully",
    )


@router.post("/{execution_id}/retry", response_model=SuccessResponse[ExecutionOut])
async def retry_execution(
    execution_id: int,
    service: WorkflowServiceDependency,
    body: Optional[RetryRequest] = None,
):
    from_failed_step = body.from_failed_step if body else True
    execution = await service.retry_execution(execution_id, from_failed_step)
    if not execution:
        raise ExecutionNotFound()
    return success_response(
        data=execution,
        message="Execution retried successfully",
    )
