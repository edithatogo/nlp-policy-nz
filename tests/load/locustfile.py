"""Locust scenarios for API maturity load testing."""

from __future__ import annotations

from locust import HttpUser, between, task


class ApiUser(HttpUser):
    """Exercise versioned API endpoints under load."""

    wait_time = between(1, 2)

    @task(3)
    def health(self) -> None:
        self.client.get("/v2/health")

    @task(2)
    def version(self) -> None:
        self.client.get("/v2/version")

    @task(1)
    def search(self) -> None:
        self.client.post("/v2/search", json={"query": "health policy", "top_k": 3})
