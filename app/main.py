from fastapi import FastAPI
from app.api import execution_router, workflow_router
from app.errors.handlers import register_exception_handlers

app = FastAPI()

register_exception_handlers(app)


@app.get("/")
async def root():
    return {
        "message": "Ok"
    }


app.include_router(workflow_router, prefix="/api/v1")
app.include_router(execution_router, prefix="/api/v1")
app.include_router(workflow_router)
app.include_router(execution_router)