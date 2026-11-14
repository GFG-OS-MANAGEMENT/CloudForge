from fastapi.testclient import TestClient


def test_health_reports_dry_run(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["dry_run"] is True
    assert body["auth_enabled"] is False


def test_dashboard_is_served(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "CloudForge" in response.text
