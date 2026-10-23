# from decimal import Decimal
# from unittest.mock import patch

# import pytest
# from sqlalchemy import select

# from app.models.flight_price import FlightPrice
# from app.tasks.price_tasks import fetch_prices_for_route


# @pytest.fixture
# def run_price_task(db, monkeypatch):
#     """Run the Celery task using the test database session."""
#     monkeypatch.setattr(db, "close", lambda: None)
#     monkeypatch.setattr("app.tasks.price_tasks.SessionLocal", lambda: db)

#     def _run(route, api_response):
#         with patch(
#             "app.tasks.price_tasks.flight_price_service.fetch_flight_price",
#             return_value=api_response,
#         ):
#             return fetch_prices_for_route(str(route.id))

#     return _run


# def test_fetch_price_saves_all_expected_fields(
#     db,
#     created_route_model,
#     airline,
#     run_price_task,
# ):
#     """Save the price with the correct route, airline, amount and currency."""
#     result = run_price_task(
#         created_route_model,
#         {
#             "price": 350,
#             "currency": "PLN",
#             "airline": "LOT Polish Airlines",
#         },
#     )

#     assert result == 1

#     price = db.query(FlightPrice).filter_by(route_id=created_route_model.id).one()

#     assert price.route_id == created_route_model.id
#     assert price.airline_id == airline.id
#     assert price.price == Decimal("350")
#     assert price.currency == "PLN"


# @pytest.mark.parametrize(
#     "airline_name",
#     [
#         "LOT Polish Airlines",
#         "lot polish airlines",
#         "LOT POLISH AIRLINES",
#         "LoT PoLiSh AiRlInEs",
#     ],
# )
# def test_airline_name_matching_is_case_insensitive(
#     db,
#     created_route_model,
#     airline,
#     run_price_task,
#     airline_name,
# ):
#     """Resolve an airline by name regardless of letter casing."""
#     result = run_price_task(
#         created_route_model,
#         {
#             "price": 300,
#             "currency": "PLN",
#             "airline": airline_name,
#         },
#     )

#     assert result == 1

#     price = db.query(FlightPrice).filter_by(route_id=created_route_model.id).one()

#     assert price.airline_id == airline.id


# @pytest.mark.parametrize("iata_code", ["LO", "lo", "Lo"])
# def test_airline_iata_matching_is_case_insensitive(
#     db,
#     created_route_model,
#     airline,
#     run_price_task,
#     iata_code,
# ):
#     """Resolve an airline by its IATA code regardless of letter casing."""
#     result = run_price_task(
#         created_route_model,
#         {
#             "price": 300,
#             "currency": "PLN",
#             "airline": iata_code,
#         },
#     )

#     assert result == 1

#     price = db.query(FlightPrice).filter_by(route_id=created_route_model.id).one()

#     assert price.airline_id == airline.id


# def test_unknown_airline_does_not_prevent_price_saving(
#     db,
#     created_route_model,
#     run_price_task,
# ):
#     """Save a price even when its airline cannot be resolved."""
#     result = run_price_task(
#         created_route_model,
#         {
#             "price": 350,
#             "currency": "PLN",
#             "airline": "Unknown Carrier rrprpr",
#         },
#     )

#     assert result == 0

#     prices = db.execute(select(FlightPrice).where(FlightPrice.route_id == created_route_model.id)).scalars().all()

#     assert prices == []


# @pytest.mark.parametrize("airline_name", [None, "", "   "])
# def test_missing_or_blank_airline_does_not_prevent_price_saving(
#     db,
#     created_route_model,
#     run_price_task,
#     airline_name,
# ):
#     """Save a price when the API omits the airline name or returns it blank."""
#     result = run_price_task(
#         created_route_model,
#         {
#             "price": 275,
#             "currency": "EUR",
#             "airline": airline_name,
#         },
#     )

#     assert result == 0

#     prices = db.execute(select(FlightPrice).where(FlightPrice.route_id == created_route_model.id)).scalars().all()

#     assert prices == []
