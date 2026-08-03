from fastapi import FastAPI
from pydantic import BaseModel


class HealthResponse(BaseModel):
    name: str
    status: str
    version: str


app = FastAPI(
    title="FlowLens API",
    description=(
        "The API and workflow engine for the FlowLens "
        "workflow-transformation platform."
    ),
    version="0.1.0",
)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Check API health",
)
def health_check() -> HealthResponse:
    return HealthResponse(
        name="FlowLens API",
        status="healthy",
        version=app.version,
    )