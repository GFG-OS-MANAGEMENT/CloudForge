"""Resource lifecycle orchestration."""

import uuid
from datetime import UTC, datetime

from ..models import Resource, ResourceCreate, ResourceStatus
from ..store import ResourceStore
from .terraform import TerraformError, TerraformRunner


class ResourceNotFound(LookupError):
    pass


class ConfirmationMismatch(ValueError):
    pass


class InvalidResourceState(RuntimeError):
    pass


class ProvisioningFailed(RuntimeError):
    def __init__(self, resource: Resource, message: str) -> None:
        super().__init__(message)
        self.resource = resource


class ResourceService:
    def __init__(self, store: ResourceStore, runner: TerraformRunner) -> None:
        self.store = store
        self.runner = runner

    def create(self, payload: ResourceCreate) -> Resource:
        resource = Resource(
            id=uuid.uuid4().hex[:12],
            name=payload.name,
            resource_type=payload.resource_type,
            region=payload.region,
            tags=payload.tags,
        )
        self.store.add(resource)
        self.store.update(
            resource.id,
            status=ResourceStatus.PROVISIONING,
            message="Provisioning started",
        )
        try:
            outputs = self.runner.apply(
                resource.id,
                {"name": payload.name, "region": payload.region, "tags": payload.tags},
            )
        except TerraformError as exc:
            failed = self.store.update(resource.id, status=ResourceStatus.FAILED, message=str(exc))
            raise ProvisioningFailed(failed, str(exc)) from exc
        return self.store.update(
            resource.id,
            status=ResourceStatus.RUNNING,
            message="Provisioning completed",
            outputs=outputs,
            provisioned_at=datetime.now(UTC),
        )

    def destroy(self, resource_id: str, confirm_name: str) -> Resource:
        resource = self.store.get(resource_id)
        if resource is None:
            raise ResourceNotFound(resource_id)
        if resource.status is ResourceStatus.DESTROYED:
            raise InvalidResourceState("Resource is already destroyed.")
        if resource.status is ResourceStatus.DESTROYING:
            raise InvalidResourceState("Resource is already being destroyed.")
        if confirm_name != resource.name:
            raise ConfirmationMismatch(
                f"Confirmation name does not match '{resource.name}'. Destruction cancelled."
            )

        self.store.update(
            resource_id,
            status=ResourceStatus.DESTROYING,
            message="Destruction started",
        )
        try:
            self.runner.destroy(resource_id)
        except TerraformError as exc:
            failed = self.store.update(resource_id, status=ResourceStatus.FAILED, message=str(exc))
            raise ProvisioningFailed(failed, str(exc)) from exc
        return self.store.update(
            resource_id,
            status=ResourceStatus.DESTROYED,
            message="Destruction completed",
            provisioned_at=None,
        )
