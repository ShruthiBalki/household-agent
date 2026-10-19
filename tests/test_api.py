from __future__ import annotations

from fastapi.testclient import TestClient

from household_agent.app import app, get_service
from household_agent.contracts import RecommendationResponse
from household_agent.errors import ProviderError


class StubService:
    async def recommend(self, product):
        return RecommendationResponse(
            outcome="Insufficient evidence",
            explanation="No defensible evidence was found.",
            source_basis="none",
            evidence=[],
            uncertainty="No reliable replacement guidance was established.",
            next_action=None,
        )


def test_health_and_minimal_ui() -> None:
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    page = client.get("/")
    assert page.status_code == 200
    assert "product_name" in page.text


def test_api_accepts_minimal_input() -> None:
    app.dependency_overrides[get_service] = lambda: StubService()
    try:
        response = TestClient(app).post(
            "/api/v1/recommendations", json={"product_name": "pan"}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["outcome"] == "Insufficient evidence"


def test_api_rejects_invalid_input_with_422() -> None:
    app.dependency_overrides[get_service] = lambda: StubService()
    try:
        response = TestClient(app).post(
            "/api/v1/recommendations", json={"product_name": "   "}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_input"


def test_provider_failure_is_a_controlled_503() -> None:
    def unavailable():
        raise ProviderError(stage="configuration", detail="secret diagnostic")

    app.dependency_overrides[get_service] = unavailable
    try:
        response = TestClient(app, raise_server_exceptions=False).post(
            "/api/v1/recommendations", json={"product_name": "pan"}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "provider_unavailable",
            "message": "The external provider could not complete the request.",
            "stage": "configuration",
        }
    }


def test_unexpected_failure_is_logged_and_controlled(caplog) -> None:
    class BrokenService:
        async def recommend(self, product):
            raise RuntimeError("unexpected")

    app.dependency_overrides[get_service] = lambda: BrokenService()
    try:
        response = TestClient(app, raise_server_exceptions=False).post(
            "/api/v1/recommendations", json={"product_name": "pan"}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "request_failed code=internal_error error_type=RuntimeError" in caplog.text
