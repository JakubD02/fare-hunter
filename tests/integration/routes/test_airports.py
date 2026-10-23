class TestListAirports:
    """Test GET /airports"""

    def test_list_airports_success(self, client, db):
        """Get list of airports"""
        response = client.get("/airports")

        assert response.status_code == 200
        airports = response.json()
        assert isinstance(airports, list)
        assert len(airports) > 0
        assert all("iata_code" in airport for airport in airports)
        assert all("name" in airport for airport in airports)

    def test_list_airports_contains_major_airports(self, client):
        """Check that major airports are in the list"""
        response = client.get("/airports")
        airports = response.json()
        iata_codes = [airport["iata_code"] for airport in airports]

        # Common airports should be there
        assert "WAW" in iata_codes
        assert "NYC" in iata_codes or "JFK" in iata_codes

    def test_list_airports_no_auth_required(self, client):
        """Airport listing doesn't require authentication"""
        response = client.get("/airports")
        assert response.status_code == 200
