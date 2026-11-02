from decimal import Decimal


class TestGetStats:
    """Test GET /routes/{route_id}/stats"""

    def test_get_stats_success(self, client, registered_user, price_history):
        """Get statistics for route with price history"""
        response = client.get(
            f"/routes/{price_history['id']}/stats",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        stats = response.json()

        assert stats["sample_count"] > 0
        assert stats["currency"] == "EUR"
        assert Decimal(stats["min_price"]) == Decimal("100")
        assert Decimal(stats["max_price"]) == Decimal("140")

        assert "sample_count" in stats
        assert "min_price" in stats
        assert "max_price" in stats
        assert "avg_price" in stats

    def test_get_stats_no_history(self, client, registered_user, created_route):
        """Get stats for route without price history"""
        response = client.get(
            f"/routes/{created_route['id']}/stats",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        stats = response.json()
        assert stats["sample_count"] == 0
        assert stats["min_price"] is None
        assert stats["max_price"] is None
        assert stats["avg_price"] is None

    def test_get_stats_route_not_found(self, client, registered_user):
        """Route doesn't exist"""
        response = client.get(
            "/routes/9999999/stats",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404

    def test_get_stats_other_user_route(self, client, registered_user, other_user_price_history):
        """Can't access stats for other user's route"""
        response = client.get(
            f"/routes/{other_user_price_history['id']}/stats",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404

    def test_get_stats_unauthorized(self, client, created_route):
        """Unauthorized access"""
        response = client.get(f"/routes/{created_route['id']}/stats")

        assert response.status_code == 401


class TestGetHistory:
    """Test GET /routes/{route_id}/history"""

    def test_get_history_success(self, client, registered_user, price_history):
        """Get price history for route"""
        response = client.get(
            f"/routes/{price_history['id']}/history",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        history = response.json()
        assert len(history) == 5
        assert all("price" in record for record in history)
        assert all("fetched_at" in record for record in history)
        assert all("currency" in record for record in history)

    def test_get_history_empty(self, client, registered_user, created_route):
        """Get history for route without prices"""
        response = client.get(
            f"/routes/{created_route['id']}/history",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_get_history_route_not_found(self, client, registered_user):
        """Route doesn't exist"""
        response = client.get(
            "/routes/99999/history",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404

    def test_get_history_other_user_route(self, client, registered_user, other_user_price_history):
        """Can't access history for other user's route"""
        response = client.get(
            f"/routes/{other_user_price_history['id']}/history",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 404

    def test_get_history_unauthorized(self, client, created_route):
        """Unauthorized access"""
        response = client.get(f"/routes/{created_route['id']}/history")

        assert response.status_code == 401

    def test_get_history_order(self, client, registered_user, price_history):
        """Price history is ordered correctly"""
        response = client.get(
            f"/routes/{price_history['id']}/history",
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        history = response.json()
        fetched_times = [record["fetched_at"] for record in history]
        assert fetched_times == sorted(fetched_times, reverse=True)

    def test_get_history_sorted_by_price_asc(self, client, registered_user, price_history):
        """History can be sorted by price ascending"""
        response = client.get(
            f"/routes/{price_history['id']}/history",
            params={"sort_by": "price", "order": "asc"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        prices = [Decimal(record["price"]) for record in response.json()]
        assert prices == sorted(prices)
        assert prices[0] == Decimal("100")

    def test_get_history_sorted_by_price_desc(self, client, registered_user, price_history):
        """History can be sorted by price descending"""
        response = client.get(
            f"/routes/{price_history['id']}/history",
            params={"sort_by": "price", "order": "desc"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 200
        prices = [Decimal(record["price"]) for record in response.json()]
        assert prices == sorted(prices, reverse=True)
        assert prices[0] == Decimal("140")

    def test_get_history_invalid_sort_field(self, client, registered_user, price_history):
        """Sorting by a column outside the whitelist is rejected"""
        response = client.get(
            f"/routes/{price_history['id']}/history",
            params={"sort_by": "airline_id"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 422

    def test_get_history_invalid_order(self, client, registered_user, price_history):
        """Only asc/desc are accepted as order"""
        response = client.get(
            f"/routes/{price_history['id']}/history",
            params={"order": "up"},
            headers={"Authorization": f"Bearer {registered_user['token']}"},
        )

        assert response.status_code == 422
