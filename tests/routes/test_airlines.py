class TestListAirlines:
    """Test GET /airlines"""

    def test_list_airlines_success(self, client, db):
        """Get list of airlines"""
        response = client.get("/airlines")

        assert response.status_code == 200
        airlines = response.json()
        assert isinstance(airlines, list)
        assert len(airlines) > 0
        assert all("iata_code" in airline for airline in airlines)
        assert all("name" in airline for airline in airlines)

    def test_list_airlines_contains_major_airlines(self, client):
        """Check that major airlines are in the list"""
        response = client.get("/airlines")
        airlines = response.json()
        codes = [airline["iata_code"] for airline in airlines]

        # Common airlines should be there
        assert any(code in codes for code in ["LO", "AA", "BA", "LH"])

    def test_list_airlines_no_auth_required(self, client):
        """Airlines listing doesn't require authentication"""
        response = client.get("/airlines")
        assert response.status_code == 200
