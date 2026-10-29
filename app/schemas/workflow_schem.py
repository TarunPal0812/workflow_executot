from datetime import datetime
from typing import Annotated, Any, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field

TextTransformOperation = Literal[
    "uppercase",
    "upppercase",
    "lowercase",
    "trim",
    "strip",
    "reverse",
    "replace",
    "title",
    "capitalize",
    "length",
]

ArithmeticOperation = Literal[
    "add",
    "subtract",
    "multiply",
    "division",
    "divide",
    "power",
    "modulo",
]


class TextTransformStep(BaseModel):
    type: Literal["text_transform"] = "text_transform"
    operation: TextTransformOperation
    value: Optional[str] = None
    replace_with: Optional[str] = None


class ArithmeticStep(BaseModel):
    type: Literal["arithmetic", "arithmatic"] = "arithmetic"
    operation: ArithmeticOperation
    operand: float


class AIClassifyStep(BaseModel):
    type: Literal["ai_classify", "ai_text_classification"] = "ai_classify"
    categories: list[str] = Field(
        default_factory=lambda: ["positive", "negative", "neutral"]
    )


Step = Annotated[
    Union[TextTransformStep, ArithmeticStep, AIClassifyStep],
    Field(discriminator="type"),
]


class StepResult(BaseModel):
    index: int
    type: str
    operation: Optional[str] = None
    input: str
    output: Optional[str] = None
    status: Literal["success", "failed"]
    error: Optional[str] = None
    duration_ms: Optional[float] = None


class ExecuteRequest(BaseModel):
    input: str


class RetryRequest(BaseModel):
    from_failed_step: bool = True


class ExecutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_id: int
    status: str
    input: str
    output: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    step_result: list[Any] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    steps: list[Step] = Field(..., min_length=1)


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    steps: Optional[list[Step]] = Field(None, min_length=1)


class WorkflowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    steps: list[dict]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GenerateWorkflowRequest(BaseModel):
    description: str = Field(..., min_length=3)
    name: Optional[str] = None
    save: bool = False


class GenerateWorkflowResponse(BaseModel):
    name: str
    description: str
    steps: list[dict]
    saved_workflow: Optional[WorkflowOut] = None