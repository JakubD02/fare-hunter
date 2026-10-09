from decimal import Decimal


class TestGetAlert:
    def test_get_alert_success(self, client, registered_user, created_route, created_alert):
        """Retrieve existing alert"""
        response = client.get(
            f"/routes/{created_route['id']}/alert",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["threshold_price"] == created_alert["threshold_price"]
        assert data["currency"] == created_alert["currency"]
        assert data["is_active"] is True


    def test_get_alert_not_found(self, client, registered_user, created_route):
        """Alert doesn't exist for route"""
        response = client.get(
            f"/routes/{created_route['id']}/alert",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "No alert configured for this route"


    def test_get_alert_unauthorized(self, client, created_route):
        """Unauthorized access without token"""
        response = client.get(f"/routes/{created_route['id']}/alert")

        assert response.status_code == 401


    def test_get_alert_for_other_user_route(self, client, registered_user, other_user_route):
        """Can't access alert for other user's route"""
        response = client.get(
            f"/routes/{other_user_route['id']}/alert",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404

class TestUpsertAlert:
    def test_create_alert_success(self, client, registered_user, created_route, alert_data):
        """Create new alert"""
        response = client.put(
            f"/routes/{created_route['id']}/alert",
            json=alert_data,
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["threshold_price"]) == Decimal(str(alert_data["threshold_price"]))
        assert data["currency"] == alert_data["currency"]
        assert data["is_active"] is alert_data["is_active"]
        assert "id" in data
        assert "route_id" in data

    def test_update_alert_success(self, client, registered_user, created_route, created_alert):
        """Update existing alert"""
        updated_data = {
            "threshold_price": 200.0,
            "is_active": False,
        }
        response = client.put(
            f"/routes/{created_route['id']}/alert",
            json=updated_data,
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["threshold_price"]) == Decimal(str(200))
        assert data["is_active"] is False
        assert data["currency"] == created_alert["currency"]

    def test_upsert_alert_route_not_found(self, client, registered_user):
        """Route doesn't exist"""
        response = client.put(
            "/routes/99999/alert",
            json={"threshold_price": 150.0},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404

    def test_upsert_alert_other_user_route(self, client, registered_user, other_user_route, alert_data):
        """Can't create alert for other user's route"""
        response = client.put(
            f"/routes/{other_user_route['id']}/alert",
            json=alert_data,
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404

    def test_upsert_alert_invalid_data(self, client, registered_user, created_route):
        """Invalid alert data"""
        response = client.put(
            f"/routes/{created_route['id']}/alert",
            json={"threshold_price": -100.0},  # Invalid negative price
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 422

    def test_upsert_alert_unauthorized(self, client, created_route, alert_data):
        """Unauthorized access"""
        response = client.put(
            f"/routes/{created_route['id']}/alert",
            json=alert_data,
        )

        assert response.status_code == 401

class TestRemoveAlert:
    def test_remove_alert_success(self, client, registered_user, created_route, created_alert):
        """Delete existing alert"""
        response = client.delete(
            f"/routes/{created_route['id']}/alert",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 204

        get_response = client.get(
            f"/routes/{created_route['id']}/alert",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )
        assert get_response.status_code == 404

    def test_remove_alert_not_found(self, client, registered_user, created_route):
        """Alert doesn't exist"""
        response = client.delete(
            f"/routes/{created_route['id']}/alert",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Alert not found."

    def test_remove_alert_unauthorized(self, client, created_route):
        """Unauthorized access"""
        response = client.delete(f"/routes/{created_route['id']}/alert")

        assert response.status_code == 401

    def test_remove_alert_other_user_route(self, client, registered_user, other_user_route):
        """Can't delete alert from other user's route"""
        response = client.delete(
            f"/routes/{other_user_route['id']}/alert",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404
