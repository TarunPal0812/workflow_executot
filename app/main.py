from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import execution_router, workflow_router
from app.db.database import init_db
from app.errors.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Ok"
    }


app.include_router(workflow_router, prefix="/api/v1")
app.include_router(execution_router, prefix="/api/v1")
app.include_router(workflow_router)
app.include_router(execution_router)