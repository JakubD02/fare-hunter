import pytest
from pydantic import ValidationError

from app.api.v1.schemas.airport import AirportUpdate


class TestAirportUpdate:
    def test_empty_update_is_valid_and_sends_nothing(self):
        update = AirportUpdate()

        assert update.model_dump(exclude_unset=True) == {}

    def test_partial_update_is_accepted(self):
        update = AirportUpdate(city="Warsaw")

        assert update.model_dump(exclude_unset=True) == {"city": "Warsaw"}

    @pytest.mark.parametrize(
        "field",
        ["iata_code", "name", "city", "country", "country_code"],
    )
    def test_explicit_null_is_rejected(self, field):
        with pytest.raises(ValidationError, match="cannot be null"):
            AirportUpdate(**{field: None})
