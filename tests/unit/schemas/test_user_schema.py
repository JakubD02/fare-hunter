import pytest
from pydantic import ValidationError

from app.api.v1.schemas.user import UserUpdate


class TestUserUpdate:
    def test_empty_update_is_valid_and_sends_nothing(self):
        update = UserUpdate()

        assert update.model_dump(exclude_unset=True) == {}

    def test_partial_update_is_accepted(self):
        update = UserUpdate(first_name="John")

        assert update.model_dump(exclude_unset=True) == {"first_name": "John"}

    @pytest.mark.parametrize("field", ["first_name", "email"])
    def test_explicit_null_is_rejected(self, field):
        with pytest.raises(ValidationError, match="cannot be null"):
            UserUpdate(**{field: None})
