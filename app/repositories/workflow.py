from typing import Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflows import Workflow


class WorkflowRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, name: str, description: Optional[str], steps: list[dict]
    ) -> Workflow:
        wf = Workflow(
            name=name,
            description=description,
            steps=steps,
        )
        self.db.add(wf)
        await self.db.commit()
        await self.db.refresh(wf)
        return wf

    async def get_by_id(self, workflow_id: int) -> Optional[Workflow]:
        query = select(Workflow).where(Workflow.id == workflow_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 50) -> list[Workflow]:
        query = select(Workflow).order_by(desc(Workflow.id)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, workflow: Workflow) -> Workflow:
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def delete(self, workflow: Workflow) -> None:
        await self.db.delete(workflow)
        await self.db.commit()
