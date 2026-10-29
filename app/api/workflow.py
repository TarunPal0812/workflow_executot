from fastapi import APIRouter, Query, status

from app.dependencies.workflow_dependencies import WorkflowServiceDependency
from app.errors.exceptions import WorkflowNotFound
from app.schemas.general_response_schema import SuccessResponse
from app.schemas.workflow_schem import (
    ExecuteRequest,
    ExecutionOut,
    WorkflowCreate,
    WorkflowOut,
    WorkflowUpdate,
)
from app.utils.response import success_response

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post(
    "",
    response_model=SuccessResponse[WorkflowOut],
    status_code=status.HTTP_201_CREATED,
)
async def create_workflow(
    body: WorkflowCreate,
    service: WorkflowServiceDependency,
):
    steps_data = [s.model_dump() for s in body.steps]
    created = await service.create_workflow(
        body.name, body.description, steps_data
    )
    return success_response(
        data=created,
        message="Workflow created successfully",
    )


@router.get("", response_model=SuccessResponse[list[WorkflowOut]])
async def list_workflows(
    service: WorkflowServiceDependency,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    workflows = await service.list_workflows(skip, limit)
    return success_response(
        data=workflows,
        message="Workflows fetched successfully",
        meta={"skip": skip, "limit": limit, "count": len(workflows)},
    )


@router.get("/{workflow_id}", response_model=SuccessResponse[WorkflowOut])
async def get_workflow(
    workflow_id: int,
    service: WorkflowServiceDependency,
):
    wf = await service.get_workflow(workflow_id)
    if not wf:
        raise WorkflowNotFound()
    return success_response(
        data=wf,
        message="Workflow fetched successfully",
    )


@router.put("/{workflow_id}", response_model=SuccessResponse[WorkflowOut])
async def update_workflow(
    workflow_id: int,
    body: WorkflowUpdate,
    service: WorkflowServiceDependency,
):
    steps_data = [s.model_dump() for s in body.steps] if body.steps else None
    wf = await service.update_workflow(
        workflow_id, body.name, body.description, steps_data
    )
    if not wf:
        raise WorkflowNotFound()
    return success_response(
        data=wf,
        message="Workflow updated successfully",
    )


@router.delete("/{workflow_id}", response_model=SuccessResponse[None])
async def delete_workflow(
    workflow_id: int,
    service: WorkflowServiceDependency,
):
    success = await service.delete_workflow(workflow_id)
    if not success:
        raise WorkflowNotFound()
    return success_response(
        message="Workflow deleted successfully",
    )


@router.post(
    "/{workflow_id}/execute",
    response_model=SuccessResponse[ExecutionOut],
    status_code=status.HTTP_201_CREATED,
)
async def execute_workflow(
    workflow_id: int,
    body: ExecuteRequest,
    service: WorkflowServiceDependency,
):
    execution = await service.execute_workflow(workflow_id, body.input)
    if not execution:
        raise WorkflowNotFound()
    return success_response(
        data=execution,
        message="Workflow executed successfully",
    )
