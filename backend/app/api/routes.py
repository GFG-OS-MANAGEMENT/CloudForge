"""REST API routes."""

import secrets
from collections import Counter
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from ..config import Settings
from ..models import (
    DestroyRequest,
    MetricsSummary,
    Resource,
    ResourceCreate,
    ResourceStatus,
)
from ..services.provisioner import (
    ConfirmationMismatch,
    InvalidResourceState,
    ProvisioningFailed,
    ResourceNotFound,
    ResourceService,
)
from ..store import ResourceLimitReached

router = APIRouter(prefix="/api")


def get_service(request: Request) -> ResourceService:
    return request.app.state.service


def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    settings: Settings = request.app.state.settings
    if not settings.api_key:
        return
    if x_api_key is None or not secrets.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key.",
        )


@router.get("/health")
def health(request: Request) -> dict[str, object]:
    settings: Settings = request.app.state.settings
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
        "dry_run": settings.dry_run,
        "auth_enabled": bool(settings.api_key),
    }


@router.get("/resources", response_model=list[Resource])
def list_resources(
    service: Annotated[ResourceService, Depends(get_service)],
) -> list[Resource]:
    return service.store.list()


@router.get("/resources/{resource_id}", response_model=Resource)
def get_resource(
    resource_id: str,
    service: Annotated[ResourceService, Depends(get_service)],
) -> Resource:
    resource = service.store.get(resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found.")
    return resource


@router.post(
    "/resources",
    response_model=Resource,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_resource(
    payload: ResourceCreate,
    service: Annotated[ResourceService, Depends(get_service)],
) -> Resource:
    try:
        return service.create(payload)
    except ResourceLimitReached as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except ProvisioningFailed as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": str(exc),
                "resource": exc.resource.model_dump(mode="json"),
            },
        ) from exc


@router.post(
    "/resources/{resource_id}/destroy",
    response_model=Resource,
    dependencies=[Depends(require_api_key)],
)
def destroy_resource(
    resource_id: str,
    payload: DestroyRequest,
    service: Annotated[ResourceService, Depends(get_service)],
) -> Resource:
    try:
        return service.destroy(resource_id, payload.confirm_name)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail="Resource not found.") from exc
    except (ConfirmationMismatch, InvalidResourceState) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProvisioningFailed as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": str(exc),
                "resource": exc.resource.model_dump(mode="json"),
            },
        ) from exc


@router.get("/metrics/summary", response_model=MetricsSummary)
def metrics_summary(
    service: Annotated[ResourceService, Depends(get_service)],
) -> MetricsSummary:
    resources = service.store.list()
    now = datetime.now(UTC)
    counts = Counter(resource.status.value for resource in resources)
    uptime = {
        resource.id: round((now - resource.provisioned_at).total_seconds(), 1)
        for resource in resources
        if resource.status is ResourceStatus.RUNNING and resource.provisioned_at is not None
    }
    return MetricsSummary(
        total=len(resources),
        by_status=dict(counts),
        running=counts.get(ResourceStatus.RUNNING.value, 0),
        uptime_seconds=uptime,
    )
