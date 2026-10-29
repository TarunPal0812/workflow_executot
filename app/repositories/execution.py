from typing import Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflows import Execution


class ExecutionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, workflow_id: int, initial_input: str) -> Execution:
        execution = Execution(
            workflow_id=workflow_id,
            status="running",
            input=initial_input,
            step_result=[],
            retry_count=0,
        )
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        return execution

    async def get_by_id(self, execution_id: int) -> Optional[Execution]:
        query = select(Execution).where(Execution.id == execution_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        workflow_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Execution]:
        query = select(Execution).order_by(desc(Execution.id))
        if workflow_id is not None:
            query = query.where(Execution.workflow_id == workflow_id)
        if status is not None:
            query = query.where(Execution.status == status)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, execution: Execution) -> Execution:
        await self.db.commit()
        await self.db.refresh(execution)
        return execution
