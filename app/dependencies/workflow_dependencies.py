from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.repositories.execution import ExecutionRepository
from app.repositories.workflow import WorkflowRepository
from app.services.workflow import WorkflowService


def get_workflow_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkflowService:
    wf_repo = WorkflowRepository(db)
    exec_repo = ExecutionRepository(db)
    return WorkflowService(wf_repo=wf_repo, exec_repo=exec_repo)


WorkflowServiceDependency = Annotated[WorkflowService, Depends(get_workflow_service)]
