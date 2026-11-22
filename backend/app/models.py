"""Request and response schemas."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

NAME_PATTERN = r"^[a-z][a-z0-9-]{2,39}$"
REGION_PATTERN = r"^[a-z0-9-]{2,32}$"


class ResourceStatus(StrEnum):
    PENDING = "pending"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    FAILED = "failed"
    DESTROYING = "destroying"
    DESTROYED = "destroyed"


class ResourceCreate(BaseModel):
    name: str = Field(
        pattern=NAME_PATTERN,
        examples=["demo-web-01"],
        description="Lowercase letters, digits and hyphens, 3-40 characters.",
    )
    resource_type: Literal["local_demo"] = "local_demo"
    region: str = Field(default="local", pattern=REGION_PATTERN)
    tags: dict[str, str] = Field(default_factory=dict)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, tags: dict[str, str]) -> dict[str, str]:
        if len(tags) > 10:
            raise ValueError("at most 10 tags are allowed")
        for key, value in tags.items():
            if not key or len(key) > 32:
                raise ValueError("tag keys must be 1-32 characters")
            if len(value) > 64:
                raise ValueError("tag values must be at most 64 characters")
        return tags


class DestroyRequest(BaseModel):
    confirm_name: str = Field(description="Exact resource name, required to confirm destruction.")


class Resource(BaseModel):
    id: str
    name: str
    resource_type: str
    region: str
    tags: dict[str, str] = Field(default_factory=dict)
    status: ResourceStatus = ResourceStatus.PENDING
    message: str | None = None
    outputs: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provisioned_at: datetime | None = None


class MetricsSummary(BaseModel):
    total: int
    by_status: dict[str, int]
    running: int
    uptime_seconds: dict[str, float]
