from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.api.v1.schemas.route import RouteCreate, RouteRead, RouteUpdate

pytestmark = pytest.mark.unit

TODAY = date.today()
FUTURE = TODAY + timedelta(days=30)


def valid_create_data(**overrides) -> dict:
    """Minimal valid payload for RouteCreate, with optional overrides"""
    data = {"origin_id": "1", "destination_id": "2", "departure_date": FUTURE}
    data.update(overrides)
    return data


class TestRouteCreate:
    def test_valid_data_is_accepted_with_defaults(self):
        route = RouteCreate(**valid_create_data())

        assert route.origin_id == "1"
        assert route.destination_id == "2"
        assert route.departure_date == FUTURE
        assert route.return_date is None
        assert route.is_active is True

    def test_departure_today_is_rejected(self):
        """Departure must be strictly in the future, so today is not allowed"""
        with pytest.raises(ValidationError, match="must be in the future"):
            RouteCreate(**valid_create_data(departure_date=TODAY))

    def test_departure_in_past_is_rejected(self):
        with pytest.raises(ValidationError, match="must be in the future"):
            RouteCreate(**valid_create_data(departure_date=TODAY - timedelta(days=1)))

    def test_return_before_departure_is_rejected(self):
        with pytest.raises(ValidationError, match="must not be before departure"):
            RouteCreate(**valid_create_data(return_date=FUTURE - timedelta(days=1)))

    def test_return_on_same_day_as_departure_is_accepted(self):
        route = RouteCreate(**valid_create_data(return_date=FUTURE))

        assert route.return_date == FUTURE

    def test_return_after_departure_is_accepted(self):
        route = RouteCreate(**valid_create_data(return_date=FUTURE + timedelta(days=7)))

        assert route.return_date == FUTURE + timedelta(days=7)

    def test_same_origin_and_destination_is_rejected(self):
        with pytest.raises(ValidationError, match="must be different"):
            RouteCreate(**valid_create_data(destination_id="1"))

    @pytest.mark.parametrize("missing_field", ["origin_id", "destination_id", "departure_date"])
    def test_missing_required_field_is_rejected(self, missing_field):
        data = valid_create_data()
        del data[missing_field]

        with pytest.raises(ValidationError):
            RouteCreate(**data)


class TestRouteUpdate:
    def test_empty_update_is_valid_and_sends_nothing(self):
        update = RouteUpdate()

        assert update.model_dump(exclude_unset=True) == {}

    def test_partial_update_is_accepted(self):
        update = RouteUpdate(destination_id="3")

        assert update.model_dump(exclude_unset=True) == {"destination_id": "3"}

    def test_future_departure_is_accepted(self):
        update = RouteUpdate(departure_date=FUTURE)

        assert update.departure_date == FUTURE

    def test_past_departure_is_rejected(self):
        with pytest.raises(ValidationError, match="must be in the future"):
            RouteUpdate(departure_date=TODAY - timedelta(days=1))

    @pytest.mark.parametrize("field", ["origin_id", "destination_id", "departure_date", "return_date", "is_active"])
    def test_explicit_null_is_rejected(self, field):
        """UpdateSchemaBase forbids null, so a field cannot be cleared to None"""
        with pytest.raises(ValidationError, match="cannot be null"):
            RouteUpdate(**{field: None})


class TestRouteRead:
    def test_builds_from_orm_like_object(self):
        orm_route = SimpleNamespace(
            id="10",
            user_id="7",
            origin_id="1",
            destination_id="2",
            departure_date=FUTURE,
            return_date=None,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

        route = RouteRead.model_validate(orm_route)

        assert route.id == "10"
        assert route.user_id == "7"
        assert route.destination_id == "2"
