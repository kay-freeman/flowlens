from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from flowlens.config import get_settings
from flowlens.database import check_database_connection
from flowlens.routers.organizations import router as organizations_router


settings = get_settings()


class HealthResponse(BaseModel):
    name: str
    status: str
    version: str


class ReadinessResponse(BaseModel):
    name: str
    status: str
    database: str


app = FastAPI(
    title=settings.app_name,
    description=(
        "The API and workflow engine for the "
        "FlowLens workflow-transformation platform."
    ),
    version=settings.app_version,
)

app.include_router(organizations_router)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Check API health",
)
def health_check() -> HealthResponse:
    return HealthResponse(
        name=settings.app_name,
        status="healthy",
        version=settings.app_version,
    )


@app.get(
    "/ready",
    response_model=ReadinessResponse,
    tags=["System"],
    summary="Check API readiness",
)
def readiness_check() -> ReadinessResponse:
    try:
        check_database_connection()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable.",
        ) from exc

    return ReadinessResponse(
        name=settings.app_name,
        status="ready",
        database="connected",
    )