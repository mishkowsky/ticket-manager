
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.service import UserService


class TestHealthEndpoint:
    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestTicketCreation:
    def test_create_ticket_success(self, client: TestClient):
        response = client.post(
            "/api/tickets",
            json={
                "title": "Test Ticket",
                "description": "Test description",
                "priority": "high",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Ticket"
        assert data["description"] == "Test description"
        assert data["priority"] == "high"
        assert data["status"] == "new"

    def test_create_ticket_invalid_title_length(self, client: TestClient):
        response = client.post("/api/tickets", json={"title": "ab"})
        assert response.status_code == 422

    def test_create_ticket_missing_title(self, client: TestClient):
        response = client.post("/api/tickets", json={})
        assert response.status_code == 422

    def test_create_ticket_default_priority(self, client: TestClient):
        response = client.post("/api/tickets", json={"title": "Test"})
        assert response.status_code == 200
        assert response.json()["priority"] == "normal"


class TestTicketRetrieval:
    def test_list_tickets_empty(self, client: TestClient):
        response = client.get("/api/tickets")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_tickets_with_items(self, client: TestClient):
        client.post("/api/tickets", json={"title": "Ticket 1"})
        client.post("/api/tickets", json={"title": "Ticket 2"})
        response = client.get("/api/tickets")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_get_single_ticket(self, client: TestClient):
        create_response = client.post("/api/tickets", json={"title": "Test"})
        ticket_id = create_response.json()["id"]
        response = client.get(f"/api/tickets/{ticket_id}")
        assert response.status_code == 200
        assert response.json()["id"] == ticket_id

    def test_get_nonexistent_ticket(self, client: TestClient):
        response = client.get("/api/tickets/999")
        assert response.status_code == 404


class TestSearch:
    def test_search_by_title(self, client: TestClient):
        client.post("/api/tickets", json={"title": "Login Bug"})
        client.post("/api/tickets", json={"title": "Database Migration"})
        response = client.get("/api/tickets?search=Login")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Login Bug"

    def test_search_by_description(self, client: TestClient):
        client.post("/api/tickets", json={"title": "TesTest1", "description": "OAuth issue"})
        client.post("/api/tickets", json={"title": "TesTest2", "description": "Cache problem"})
        response = client.get("/api/tickets?search=OAuth")
        data = response.json()
        assert data["total"] == 1


class TestFiltering:
    def test_filter_by_status(self, client: TestClient):
        client.post("/api/tickets", json={"title": "Test1"})
        create_resp = client.post("/api/tickets", json={"title": "Test2"})
        ticket_id = create_resp.json()["id"]
        client.patch(f"/api/tickets/{ticket_id}", json={"status": "in_progress"})
        response = client.get("/api/tickets?status=in_progress")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "in_progress"

    def test_filter_by_priority(self, client: TestClient):
        client.post("/api/tickets", json={"title": "Test1", "priority": "high"})
        client.post("/api/tickets", json={"title": "Test2", "priority": "low"})
        response = client.get("/api/tickets?priority=high")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["priority"] == "high"

    def test_filter_by_multiple_criteria(self, client: TestClient):
        client.post("/api/tickets", json={"title": "Test1", "priority": "high"})
        client.post("/api/tickets", json={"title": "Test2", "priority": "high"})
        response = client.get("/api/tickets?priority=high&search=Test1")
        data = response.json()
        assert data["total"] == 1


class TestSorting:
    def test_sort_by_created_at_desc(self, client: TestClient):
        resp1 = client.post("/api/tickets", json={"title": "First"})
        resp2 = client.post("/api/tickets", json={"title": "Second"})

        response = client.get("/api/tickets?sort_by=created_at&sort_order=desc")
        data = response.json()
        assert data["items"][0]["id"] == resp2.json()["id"]
        assert data["items"][1]["id"] == resp1.json()["id"]

    def test_sort_by_created_at_asc(self, client: TestClient):
        resp1 = client.post("/api/tickets", json={"title": "First"})
        resp2 = client.post("/api/tickets", json={"title": "Second"})

        response = client.get("/api/tickets?sort_by=created_at&sort_order=asc")
        data = response.json()
        assert data["items"][0]["id"] == resp1.json()["id"]
        assert data["items"][1]["id"] == resp2.json()["id"]

    def test_sort_by_priority(self, client: TestClient):
        client.post("/api/tickets", json={"title": "Test1", "priority": "low"})
        client.post("/api/tickets", json={"title": "Test2", "priority": "high"})

        response = client.get("/api/tickets?sort_by=priority&sort_order=asc")
        data = response.json()
        assert data["items"][0]["priority"] == "low"
        assert data["items"][1]["priority"] == "high"


class TestPagination:
    def test_pagination_first_page(self, client: TestClient):
        for i in range(15):
            client.post("/api/tickets", json={"title": f"Ticket {i}"})

        response = client.get("/api/tickets?page=1&page_size=10")
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["total_pages"] == 2

    def test_pagination_second_page(self, client: TestClient):
        for i in range(15):
            client.post("/api/tickets", json={"title": f"Ticket {i}"})

        response = client.get("/api/tickets?page=2&page_size=10")
        data = response.json()
        assert len(data["items"]) == 5
        assert data["page"] == 2


class TestStatusUpdate:
    def test_update_ticket_status(self, client: TestClient):
        create_resp = client.post("/api/tickets", json={"title": "Test"})
        ticket_id = create_resp.json()["id"]
        response = client.patch(f"/api/tickets/{ticket_id}", json={"status": "in_progress"})
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_cannot_modify_done_ticket(self, client: TestClient):
        create_resp = client.post("/api/tickets", json={"title": "Test"})
        ticket_id = create_resp.json()["id"]

        client.patch(f"/api/tickets/{ticket_id}", json={"status": "done"})

        response = client.patch(f"/api/tickets/{ticket_id}", json={"status": "in_progress"})
        assert response.status_code == 400
        assert "невозможно изменить заявку, находящуюся" in response.json()["detail"].lower()

    def test_update_nonexistent_ticket(self, client: TestClient):
        response = client.patch("/api/tickets/999", json={"status": "in_progress"})
        assert response.status_code == 404


class TestDeletion:
    def test_delete_ticket_requires_auth(self, client: TestClient):
        """Test that delete requires auth."""
        create_resp = client.post("/api/tickets", json={"title": "Test"})
        ticket_id = create_resp.json()["id"]

        response = client.delete(f"/api/tickets/{ticket_id}")
        assert response.status_code == 401

    def test_delete_ticket_success_with_auth(self, db_session: Session, client: TestClient):
        """Test delete with valid admin credentials."""

        UserService.create_user(db_session, "admin", "admin", is_admin=True)
        create_resp = client.post("/api/tickets", json={"title": "Test"})
        ticket_id = create_resp.json()["id"]

        response = client.delete(
            f"/api/tickets/{ticket_id}",
            auth=("admin", "admin"),
        )
        assert response.status_code == 204

        get_response = client.get(f"/api/tickets/{ticket_id}")
        assert get_response.status_code == 404

    def test_delete_done_ticket_fails(self, db_session: Session, client: TestClient):
        UserService.create_user(db_session, "admin", "admin", is_admin=True)
        create_resp = client.post("/api/tickets", json={"title": "Test"})
        ticket_id = create_resp.json()["id"]

        client.patch(f"/api/tickets/{ticket_id}", json={"status": "done"})

        response = client.delete(
            f"/api/tickets/{ticket_id}",
            auth=("admin", "admin"),
        )
        assert response.status_code == 400

    def test_delete_with_wrong_credentials(self, client: TestClient):
        create_resp = client.post("/api/tickets", json={"title": "Test"})
        ticket_id = create_resp.json()["id"]

        response = client.delete(
            f"/api/tickets/{ticket_id}",
            auth=("user", "wrong"),
        )
        assert response.status_code == 401


class TestUserAuthentication:
    def test_get_current_user_success(self, client: TestClient):
        client.post(
            "/api/users/register",
            json={"username": "testuser", "password": "password123"},
        )
        response = client.get("/api/users/me", auth=("testuser", "password123"))
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"

    def test_get_current_user_invalid_credentials(self, client: TestClient):
        client.post(
            "/api/users/register",
            json={"username": "testuser", "password": "password123"},
        )
        response = client.get("/api/users/me", auth=("testuser", "wrongpassword"))
        assert response.status_code == 401

    def test_get_current_user_no_auth(self, client: TestClient):
        response = client.get("/api/users/me")
        assert response.status_code == 401
