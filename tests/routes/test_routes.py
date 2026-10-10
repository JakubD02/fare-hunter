

class TestListRoutes:
    """Test GET /routes/"""
    def test_list_routes_empty(self, client, registered_user):
        """List routes when none exist"""
        response = client.get(
            "/routes/",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_list_routes_with_data(self, client, registered_user, created_route):
        """List routes for current user"""
        response = client.get(
            "/routes/",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1

        assert routes[0]["id"] == created_route["id"]
        assert routes[0]["origin_id"] == created_route["origin_id"]
        assert routes[0]["destination_id"] == created_route["destination_id"]
        assert routes[0]["departure_date"] == created_route["departure_date"]
        assert routes[0]["is_active"] == created_route["is_active"]

    def test_list_routes_only_own_routes(self, client, registered_user, other_user_route):
        """User can only see their own routes"""
        response = client.get(
            "/routes/",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_list_routes_unauthorized(self, client):
        """Unauthorized access"""
        response = client.get("/routes/")

        assert response.status_code == 401

class TestCreateRoute:
    """Test POST /routes/"""

    def test_create_route_success(self, client, registered_user, route_data):
        """Create route successfully"""
        response = client.post(
            "/routes/",
            json=route_data,
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["origin_id"] == route_data["origin_id"]
        assert data["destination_id"] == route_data["destination_id"]
        assert data["departure_date"] == route_data["departure_date"]
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data

    def test_create_route_invalid_airport(self, client, registered_user):
        """Invalid airport IATA code"""
        response = client.post(
            "/routes/",
            json={
                "origin_id": "INVALID",
                "destination_id": "NYC",
                "departure_date": "2026-12-25",
            },
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404

    def test_create_route_past_date(self, client, registered_user):
        """Departure date in the past"""
        response = client.post(
            "/routes/",
            json={
                "origin_iata": "WAW",
                "destination_iata": "NYC",
                "departure_date": "2020-01-01",
            },
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )


        assert response.status_code == 422

    def test_create_route_missing_field(self, client, registered_user):
        """Missing required field"""
        response = client.post(
            "/routes/",
            json={
                "origin_iata": "WAW",
                "destination_iata": "NYC",
            },
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 422

    def test_create_route_unauthorized(self, client, route_data):
        """Unauthorized access"""
        response = client.post("/routes/", json=route_data)

        assert response.status_code == 401

class TestGetRoute:
    """Test GET /routes/{route_id}"""

    def test_get_route_success(self, client, registered_user, created_route):
        """Get route details"""
        response = client.get(
            f"/routes/{created_route['id']}",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_route["id"]
        assert data["origin_id"] == created_route["origin_id"]

    def test_get_route_not_found(self, client, registered_user):
        """Route doesn't exist"""
        response = client.get(
            "/routes/99999999",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Route not found."

    def test_get_route_other_user(self, client, registered_user, other_user_route):
        """Can't access other user's route"""
        response = client.get(
            f"/routes/{other_user_route['id']}",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404

    def test_get_route_unauthorized(self, client, created_route):
        """Unauthorized access"""
        response = client.get(f"/routes/{created_route['id']}")

        assert response.status_code == 401


class TestUpdateRoute:
    """Test PATCH /routes/{route_id}"""

    def test_update_route_success(self, client, registered_user, created_route, update_route_data, db):
        """Update route"""
        pass

    def test_update_route_other_user(self, client, registered_user, other_user_route):
        """Can't update other user's route"""
        response = client.patch(
            f"/routes/{other_user_route['id']}",
            json={"destination_id": "LHR"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404

    def test_update_route_invalid_data(self, client, registered_user, created_route):
        pass

    def test_update_route_unauthorized(self, client, created_route):
        """Unauthorized access"""
        response = client.patch(
            f"/routes/{created_route['id']}",
            json={"destination_id": "LHR"},
        )

        assert response.status_code == 401
