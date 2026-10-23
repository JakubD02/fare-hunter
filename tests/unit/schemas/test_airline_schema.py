import pytest
from pydantic import ValidationError

from app.api.v1.schemas.airline import AirlineUpdate


class TestAirlineUpdate:
    def test_empty_update_is_valid_and_sends_nothing(self):
        update = AirlineUpdate()

        assert update.model_dump(exclude_unset=True) == {}

    def test_partial_update_is_accepted(self):
        update = AirlineUpdate(name="LOT Polish Airlines")

        assert update.model_dump(exclude_unset=True) == {"name": "LOT Polish Airlines"}

    @pytest.mark.parametrize("field", ["iata_code", "name"])
    def test_explicit_null_is_rejected(self, field):
        with pytest.raises(ValidationError, match="cannot be null"):
            AirlineUpdate(**{field: None})
