from fastapi.testclient import TestClient

from app.main import app
import app.main as main_module

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "Running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_review(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "save_review",
        lambda review: None
    )

    response = client.post(
        "/api/reviews",
        json={"code": "print('hello')"}
    )

    assert response.status_code == 200
    assert "review_id" in response.json()
    assert response.json()["summary"]["total_issues"] == 1


def test_empty_code_validation():
    response = client.post(
        "/api/reviews",
        json={"code": ""}
    )

    assert response.status_code == 422


def test_list_reviews(monkeypatch):
    sample_reviews = [
        {
            "review_id": "test-123",
            "summary": {
                "total_issues": 1,
                "high": 0,
                "medium": 0,
                "low": 1
            },
            "findings": []
        }
    ]

    monkeypatch.setattr(
        main_module,
        "get_all_reviews",
        lambda: sample_reviews
    )

    response = client.get("/api/reviews")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_review_not_found(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "get_review_by_id",
        lambda review_id: None
    )

    response = client.get("/api/reviews/unknown-id")

    assert response.status_code == 404