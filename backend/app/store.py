"""Thread-safe in-memory resource registry.

The store keeps the API stateless with respect to Terraform: it only tracks
lifecycle state. Persisting this registry is a good follow-up contribution.
"""

import threading
from datetime import UTC, datetime

from .models import Resource, ResourceStatus


class ResourceLimitReached(RuntimeError):
    pass


class ResourceStore:
    def __init__(self, max_resources: int) -> None:
        self._lock = threading.Lock()
        self._resources: dict[str, Resource] = {}
        self._max_resources = max_resources

    def add(self, resource: Resource) -> Resource:
        with self._lock:
            active = sum(
                1
                for tracked in self._resources.values()
                if tracked.status is not ResourceStatus.DESTROYED
            )
            if active >= self._max_resources:
                raise ResourceLimitReached(
                    f"Resource limit reached ({self._max_resources}). "
                    "Destroy unused resources before provisioning more."
                )
            self._resources[resource.id] = resource
            return resource

    def get(self, resource_id: str) -> Resource | None:
        with self._lock:
            return self._resources.get(resource_id)

    def list(self) -> list[Resource]:
        with self._lock:
            resources = list(self._resources.values())
        return sorted(resources, key=lambda resource: resource.created_at, reverse=True)

    def update(self, resource_id: str, **changes: object) -> Resource:
        with self._lock:
            resource = self._resources[resource_id]
            updated = resource.model_copy(update={**changes, "updated_at": datetime.now(UTC)})
            self._resources[resource_id] = updated
            return updated
