from datetime import datetime, timezone
from typing import Optional

from app.models.workflows import Execution, Workflow
from app.repositories.execution import ExecutionRepository
from app.repositories.workflow import WorkflowRepository
from app.services.openai_service import generate_workflow as generate_workflow_ai
from app.services.workflow_engine import execute_workflow


class WorkflowService:
    def __init__(
        self,
        wf_repo: WorkflowRepository,
        exec_repo: ExecutionRepository,
    ) -> None:
        self.wf_repo = wf_repo
        self.exec_repo = exec_repo

    async def create_workflow(
        self, name: str, description: Optional[str], steps: list[dict]
    ) -> Workflow:
        return await self.wf_repo.create(name, description, steps)

    async def get_workflow(self, workflow_id: int) -> Optional[Workflow]:
        return await self.wf_repo.get_by_id(workflow_id)

    async def list_workflows(self, skip: int = 0, limit: int = 50) -> list[Workflow]:
        return await self.wf_repo.list_all(skip, limit)

    async def update_workflow(
        self,
        workflow_id: int,
        name: Optional[str],
        description: Optional[str],
        steps: Optional[list[dict]],
    ) -> Optional[Workflow]:
        wf = await self.wf_repo.get_by_id(workflow_id)
        if not wf:
            return None

        if name is not None:
            wf.name = name
        if description is not None:
            wf.description = description
        if steps is not None:
            wf.steps = steps

        return await self.wf_repo.update(wf)

    async def delete_workflow(self, workflow_id: int) -> bool:
        wf = await self.wf_repo.get_by_id(workflow_id)
        if not wf:
            return False
        await self.wf_repo.delete(wf)
        return True

    async def execute_workflow(
        self, workflow_id: int, initial_input: str
    ) -> Optional[Execution]:
        wf = await self.wf_repo.get_by_id(workflow_id)
        if not wf:
            return None

        exec_record = await self.exec_repo.create(workflow_id, initial_input)

        exec_status, final_output, error_msg, step_results = (
            await execute_workflow(
                steps=wf.steps,
                initial_input=initial_input,
            )
        )

        exec_record.status = exec_status
        exec_record.output = final_output
        exec_record.error = error_msg
        exec_record.step_result = step_results
        exec_record.finished_at = datetime.now(timezone.utc)

        return await self.exec_repo.update(exec_record)

    async def retry_execution(
        self, execution_id: int, from_failed_step: bool = True
    ) -> Optional[Execution]:
        execution = await self.exec_repo.get_by_id(execution_id)
        if not execution:
            return None

        wf = await self.wf_repo.get_by_id(execution.workflow_id)
        if not wf:
            return None

        start_step = 0
        previous_results = None

        if from_failed_step and execution.step_result:
            for idx, res in enumerate(execution.step_result):
                if res.get("status") == "failed":
                    start_step = idx
                    previous_results = execution.step_result[:idx]
                    break

        exec_status, final_output, error_msg, step_results = (
            await execute_workflow(
                steps=wf.steps,
                initial_input=execution.input,
                start=start_step,
                previous_results=previous_results,
            )
        )

        execution.retry_count += 1
        execution.status = exec_status
        execution.output = final_output
        execution.error = error_msg
        execution.step_result = step_results
        execution.finished_at = datetime.now(timezone.utc)

        return await self.exec_repo.update(execution)

    async def get_execution(self, execution_id: int) -> Optional[Execution]:
        return await self.exec_repo.get_by_id(execution_id)

    async def list_executions(
        self,
        workflow_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Execution]:
        return await self.exec_repo.list_all(workflow_id, status, skip, limit)

    async def generate_workflow(
        self,
        description: str,
        custom_name: Optional[str] = None,
        save: bool = False,
    ) -> dict:
        generated = await generate_workflow_ai(
            description, custom_name
        )
        saved_wf = None
        if save:
            saved_wf = await self.create_workflow(
                name=generated["name"],
                description=generated["description"],
                steps=generated["steps"],
            )
        return {
            "name": generated["name"],
            "description": generated["description"],
            "steps": generated["steps"],
            "saved_workflow": saved_wf,
        }
