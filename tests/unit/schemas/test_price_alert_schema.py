import pytest
from pydantic import ValidationError

from app.api.v1.schemas.price_alert import PriceAlertUpdate


class TestPriceAlertUpdate:
    def test_empty_update_is_valid_and_sends_nothing(self):
        update = PriceAlertUpdate()

        assert update.model_dump(exclude_unset=True) == {}

    def test_partial_update_is_accepted(self):
        update = PriceAlertUpdate(is_active=False)

        assert update.model_dump(exclude_unset=True) == {"is_active": False}

    @pytest.mark.parametrize(
        "field",
        ["threshold_price", "currency", "is_active"],
    )
    def test_explicit_null_is_rejected(self, field):
        with pytest.raises(ValidationError, match="cannot be null"):
            PriceAlertUpdate(**{field: None})
