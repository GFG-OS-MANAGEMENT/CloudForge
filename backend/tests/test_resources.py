from app.config import Settings
from app.main import create_app
from fastapi.testclient import TestClient


def create_resource(
    client: TestClient,
    name: str = "demo-web-01",
    region: str = "local",
    tags: dict[str, str] | None = None,
):
    return client.post(
        "/api/resources",
        json={"name": name, "region": region, "tags": tags or {}},
    )


def test_create_and_list_resource(client: TestClient) -> None:
    response = create_resource(client, tags={"env": "dev"})

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "running"
    assert body["name"] == "demo-web-01"
    assert body["tags"] == {"env": "dev"}
    assert body["outputs"]["mode"] == "dry-run"
    assert body["provisioned_at"] is not None

    listed = client.get("/api/resources").json()
    assert len(listed) == 1
    assert listed[0]["id"] == body["id"]

    fetched = client.get(f"/api/resources/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "demo-web-01"


def test_get_unknown_resource_returns_404(client: TestClient) -> None:
    response = client.get("/api/resources/does-not-exist")

    assert response.status_code == 404


def test_invalid_input_is_rejected(client: TestClient) -> None:
    assert create_resource(client, name="BadName").status_code == 422
    assert create_resource(client, name="../etc/passwd").status_code == 422
    assert create_resource(client, name="ab").status_code == 422
    assert create_resource(client, name="valid-name", region="UPPER").status_code == 422

    too_many_tags = {f"key{i}": "value" for i in range(11)}
    assert create_resource(client, name="valid-name", tags=too_many_tags).status_code == 422


def test_destroy_requires_exact_confirmation(client: TestClient) -> None:
    resource = create_resource(client).json()

    wrong = client.post(
        f"/api/resources/{resource['id']}/destroy", json={"confirm_name": "wrong-name"}
    )
    assert wrong.status_code == 409
    assert client.get(f"/api/resources/{resource['id']}").json()["status"] == "running"

    destroyed = client.post(
        f"/api/resources/{resource['id']}/destroy",
        json={"confirm_name": resource["name"]},
    )
    assert destroyed.status_code == 200
    assert destroyed.json()["status"] == "destroyed"

    again = client.post(
        f"/api/resources/{resource['id']}/destroy",
        json={"confirm_name": resource["name"]},
    )
    assert again.status_code == 409


def test_destroy_unknown_resource_returns_404(client: TestClient) -> None:
    response = client.post("/api/resources/unknown/destroy", json={"confirm_name": "unknown"})

    assert response.status_code == 404


def test_resource_limit_is_enforced(client: TestClient) -> None:
    for index in range(3):
        assert create_resource(client, name=f"demo-app-{index}").status_code == 201

    limited = create_resource(client, name="demo-app-extra")
    assert limited.status_code == 429


def test_destroyed_resources_release_quota(client: TestClient) -> None:
    resources = [create_resource(client, name=f"quota-app-{index}").json() for index in range(3)]
    assert create_resource(client, name="quota-app-over").status_code == 429

    client.post(
        f"/api/resources/{resources[0]['id']}/destroy",
        json={"confirm_name": resources[0]["name"]},
    )

    assert create_resource(client, name="quota-app-replacement").status_code == 201


def test_metrics_summary(client: TestClient) -> None:
    first = create_resource(client, name="demo-app-01").json()
    create_resource(client, name="demo-app-02")
    client.post(
        f"/api/resources/{first['id']}/destroy",
        json={"confirm_name": first["name"]},
    )

    metrics = client.get("/api/metrics/summary").json()
    assert metrics["total"] == 2
    assert metrics["running"] == 1
    assert metrics["by_status"] == {"running": 1, "destroyed": 1}
    assert first["id"] not in metrics["uptime_seconds"]
    assert all(value >= 0 for value in metrics["uptime_seconds"].values())


def test_api_key_protects_mutations(settings: Settings) -> None:
    secured = settings.model_copy(update={"api_key": "test-key"})
    client = TestClient(create_app(secured))

    assert create_resource(client).status_code == 401

    authorized = client.post(
        "/api/resources",
        json={"name": "demo-secure-01"},
        headers={"X-API-Key": "test-key"},
    )
    assert authorized.status_code == 201

    assert client.get("/api/resources").status_code == 200


def test_provisioning_failure_marks_resource_failed(settings: Settings) -> None:
    live = settings.model_copy(
        update={"dry_run": False, "terraform_binary": "cloudforge-missing-terraform"}
    )
    client = TestClient(create_app(live))

    response = create_resource(client, name="demo-broken-01")

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert detail["resource"]["status"] == "failed"
    assert "Terraform binary" in detail["message"]

    listed = client.get("/api/resources").json()
    assert listed[0]["status"] == "failed"
