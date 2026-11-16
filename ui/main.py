from datetime import date, timedelta

from nicegui import app, ui

from app.core.config import settings
from ui.utils import (
    CURRENCIES,
    PASSWORD_HINT,
    ROUTES_PER_PAGE,
    airport_label,
    call,
    confirm_delete,
    convert_hint,
    date_input,
    fetch_all,
    format_date,
    frame,
    history_table,
    max_day,
    parse_date,
    require_login,
    set_day_range,
    show_stats,
)


@ui.page("/login")
def login_page():
    mode = {"register": False}

    def do_login():
        if "@" not in email.value:
            ui.notify("Enter a valid email address", type="warning")
            return
        if len(password.value) < 8:
            ui.notify("Password must be at least 8 characters", type="warning")
            return

        tokens = call("POST", "/auth/token", data={"username": email.value, "password": password.value})
        if tokens:
            app.storage.user["token"] = tokens["access_token"]
            app.storage.user["refresh_token"] = tokens["refresh_token"]
            ui.navigate.to("/")

    def do_register():
        if "@" not in email.value:
            ui.notify("Enter a valid email address", type="warning")
            return
        if len(password.value) < 8:
            ui.notify("Password must be at least 8 characters", type="warning")
            return
        if password.value != password2.value:
            ui.notify("Passwords do not match", type="warning")
            return
        if len(first_name.value) < 3:
            ui.notify("First name must be at least 3 characters", type="warning")
            return

        user = call(
            "POST",
            "/auth/register",
            json={"first_name": first_name.value, "email": email.value, "password": password.value},
        )
        if user:
            ui.notify("Account created, logging in...", type="positive")
            do_login()

    def toggle_mode():
        mode["register"] = not mode["register"]
        register_fields.set_visibility(mode["register"])
        login_button.set_visibility(not mode["register"])
        register_button.set_visibility(mode["register"])
        if mode["register"]:
            password.props(f'hint="{PASSWORD_HINT}"')
        else:
            password.props(remove="hint")
        switch_button.set_text("I already have an account" if mode["register"] else "I don't have an account")

    with ui.card().classes("absolute-center w-96"):
        ui.label("Fare Hunter").classes("text-2xl")
        email = (
            ui.input(
                "Email",
                validation={"Enter a valid email address": lambda v: "@" in v},
            )
            .props("type=email")
            .classes("w-full")
        )
        password = ui.input("Password", password=True, password_toggle_button=True).classes("w-full")

        with ui.column().classes("w-full") as register_fields:
            password2 = ui.input("Repeat password", password=True, password_toggle_button=True).classes("w-full")
            first_name = ui.input("First name (min. 3 characters)").classes("w-full")
        register_fields.set_visibility(False)

        login_button = ui.button("Log in", on_click=do_login).classes("w-full")
        register_button = ui.button("Register", on_click=do_register).classes("w-full")
        register_button.set_visibility(False)
        switch_button = ui.button("I don't have an account", on_click=toggle_mode).props("flat").classes("w-full")


@ui.page("/")
def routes_page():
    if not require_login():
        return
    frame("Your routes")

    today = date.today()
    first_departure = today + timedelta(days=1)

    airports = fetch_all("/airports")
    codes = {a["id"]: a["iata_code"] for a in airports}
    cities = {a["id"]: a["city"] for a in airports}
    options = {a["id"]: f"{a['iata_code']} – {a['city']}" for a in airports}

    max_routes = settings.route.max_routes_per_user

    page = {"index": 0}
    routes_box = ui.column().classes("w-full")

    def update_add_section():
        total = len(fetch_all("/routes/"))
        limit_reached = total >= max_routes
        add_section.set_visibility(not limit_reached)
        limit_label.set_visibility(limit_reached)

    def remove(route_id: str):
        if call("DELETE", f"/routes/{route_id}") is not None:
            ui.notify("Route deleted", type="positive")
            refresh()

    def ask_remove(route_id: str, label: str):
        confirm_delete(
            f"Route {label} and its price history will be deleted permanently.",
            lambda: remove(route_id),
        )

    def change_page(delta: int):
        page["index"] = max(0, page["index"] + delta)
        refresh()

    def refresh():
        routes_box.clear()
        offset = page["index"] * ROUTES_PER_PAGE
        routes = call("GET", "/routes/", params={"limit": ROUTES_PER_PAGE + 1, "offset": offset}) or []
        has_next = len(routes) > ROUTES_PER_PAGE
        routes = routes[:ROUTES_PER_PAGE]

        if not routes and page["index"] > 0:
            page["index"] -= 1
            refresh()
            return

        with routes_box:
            if not routes:
                ui.label("No routes yet. Add the first one below.")
            for r in routes:
                origin_code = codes.get(r["origin_id"], "?")
                destination_code = codes.get(r["destination_id"], "?")
                round_trip = r["return_date"] is not None
                label = f"{origin_code} → {destination_code}"
                with ui.card().classes("w-full q-pa-sm"):
                    with ui.row().classes("w-full items-center justify-between no-wrap"):
                        with ui.row().classes("items-baseline gap-2"):
                            ui.label(label).classes("text-h6 text-weight-bold")
                            ui.label(
                                f"{cities.get(r['origin_id'], '?')} → {cities.get(r['destination_id'], '?')}"
                            ).classes("text-caption text-grey-7")
                        if round_trip:
                            ui.chip("Round trip", icon="sync", color="indigo-1", text_color="indigo-10").props("dense")
                        else:
                            ui.chip("One way", icon="arrow_forward", color="teal-1", text_color="teal-10").props(
                                "dense"
                            )

                    with ui.row().classes("w-full items-center justify-between no-wrap"):
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("flight_takeoff", color="primary", size="sm")
                            ui.label(format_date(r["departure_date"])).classes("text-body2")
                            if round_trip:
                                ui.icon("arrow_forward", size="xs", color="grey-6")
                                ui.icon("flight_land", color="primary", size="sm")
                                ui.label(format_date(r["return_date"])).classes("text-body2")
                                nights = (parse_date(r["return_date"]) - parse_date(r["departure_date"])).days
                                ui.label(f"· {nights} nights").classes("text-caption text-grey-7")
                        with ui.row().classes("gap-1 no-wrap"):
                            ui.button(
                                "Details",
                                icon="chevron_right",
                                on_click=lambda rid=r["id"]: ui.navigate.to(f"/routes/{rid}"),
                            ).props("flat dense color=primary")
                            ui.button(
                                "Delete",
                                icon="delete",
                                on_click=lambda rid=r["id"], lbl=label: ask_remove(rid, lbl),
                            ).props("flat dense color=negative")

            pager = ui.row().classes("w-full items-center justify-between")
            pager.set_visibility(page["index"] > 0 or has_next)
            with pager:
                prev_button = ui.button("← Previous", on_click=lambda: change_page(-1)).props("flat")
                prev_button.set_enabled(page["index"] > 0)
                ui.label(f"Page {page['index'] + 1}")
                next_button = ui.button("Next →", on_click=lambda: change_page(1)).props("flat")
                next_button.set_enabled(has_next)

        update_add_section()

    limit_label = ui.label(
        f"You have reached the limit of {max_routes} routes. Delete one to add a new route."
    ).classes("text-grey-7")
    limit_label.set_visibility(False)

    with ui.expansion("Add new route", icon="add").classes("w-full") as add_section:
        origin = ui.select(options, label="From", with_input=True).classes("w-full")
        destination = ui.select(options, label="To", with_input=True).classes("w-full")
        currency = ui.select(CURRENCIES, value="PLN", label="Display currency").classes("w-full")
        departure, _ = date_input("Departure", first_departure)
        returning, return_picker = date_input("Return (optional)", first_departure + timedelta(days=1))
        returning.disable()

        def on_departure_change(e):
            dep = parse_date(e.value)
            if dep is None:
                returning.set_value("")
                returning.disable()
                return

            returning.enable()
            min_return = dep + timedelta(days=1)
            set_day_range(return_picker, min_return, max_day())
            ret = parse_date(returning.value)
            if ret is not None and ret < min_return:
                returning.set_value("")

        departure.on_value_change(on_departure_change)

        def reset_form():
            origin.set_value(None)
            destination.set_value(None)
            currency.set_value("PLN")
            departure.set_value("")
            returning.set_value("")

        def create():
            if origin.value is None or destination.value is None:
                ui.notify("Select both origin and destination airports", type="warning")
                return
            if origin.value == destination.value:
                ui.notify("Origin and destination must be different", type="warning")
                return

            dep = parse_date(departure.value)
            if dep is None or dep <= today:
                ui.notify("Select a departure date from tomorrow onwards", type="warning")
                return
            if dep > max_day():
                ui.notify(f"Departure must be within {settings.route.max_days_ahead} days", type="warning")
                return

            ret = parse_date(returning.value)
            if returning.value and (ret is None or ret <= dep):
                ui.notify("Return must be at least one day after departure", type="warning")
                return
            if ret is not None and ret > max_day():
                ui.notify(f"Return must be within {settings.route.max_days_ahead} days", type="warning")
                return

            body = {
                "origin_id": origin.value,
                "destination_id": destination.value,
                "departure_date": departure.value,
                "return_date": returning.value or None,
                "currency": currency.value,
            }
            if call("POST", "/routes/", json=body) is not None:
                ui.notify("Route added", type="positive")
                reset_form()
                page["index"] = 0
                refresh()

        ui.button("Add route", on_click=create)

    refresh()


@ui.page("/routes/{route_id}")
def route_page(route_id: str):
    if not require_login():
        return
    frame("Route")
    ui.button("← Back", on_click=lambda: ui.navigate.to("/")).props("flat")

    route = call("GET", f"/routes/{route_id}", notify=False)
    if route is None:
        ui.label("Route not found")
        return
    airlines = {a["id"]: a["name"] for a in fetch_all("/airlines")}
    airports = {a["id"]: a for a in fetch_all("/airports")}

    origin = airports.get(route["origin_id"])
    destination = airports.get(route["destination_id"])

    with ui.card().classes("w-full"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("flight_takeoff").classes("text-2xl text-primary")
            ui.label(airport_label(origin)).classes("text-lg")
            ui.icon("arrow_forward").classes("text-grey-6")
            ui.icon("flight_land").classes("text-2xl text-primary")
            ui.label(airport_label(destination)).classes("text-lg")
        trip_type = "Round trip" if route["return_date"] else "One way"
        ui.label(trip_type).classes("text-caption text-grey-7")
        ui.label("All prices are for 1 passenger").classes("text-caption text-grey-7")

    alert_state = {"exists": False}

    today = date.today()
    with ui.card().classes("w-full"):
        ui.label("Dates and currency").classes("text-lg")
        departure, _ = date_input("Departure", today + timedelta(days=1), route["departure_date"])
        returning, _ = date_input("Return (optional)", today + timedelta(days=2), route["return_date"] or "")
        currency = ui.select(CURRENCIES, value=route["currency"], label="Display currency").classes("w-full")

        def save_route():
            dep = parse_date(departure.value)
            if dep is None or dep <= today:
                ui.notify("Select a departure date from tomorrow onwards", type="warning")
                return
            if dep > max_day():
                ui.notify(f"Departure must be within {settings.route.max_days_ahead} days", type="warning")
                return
            ret = parse_date(returning.value)
            if returning.value and (ret is None or ret <= dep):
                ui.notify("Return must be at least one day after departure", type="warning")
                return
            if ret is not None and ret > max_day():
                ui.notify(f"Return must be within {settings.route.max_days_ahead} days", type="warning")
                return
            body = {
                "departure_date": departure.value,
                "return_date": returning.value or None,
                "currency": currency.value,
            }
            if call("PATCH", f"/routes/{route_id}", json=body) is not None:
                ui.notify("Route updated", type="positive")
                ui.navigate.to("/")

        ui.button("Save changes", on_click=save_route)

    # Side by side from the md breakpoint up, stacked full width on narrower screens
    with ui.row().classes("w-full items-start gap-4 flex-col md:flex-row md:flex-nowrap"):
        with ui.card().classes("w-full md:flex-1 min-w-0"):
            ui.label("Statistics").classes("text-lg")
            show_stats(call("GET", f"/routes/{route_id}/stats", notify=False), route["currency"])
            ui.label("History").classes("text-lg q-mt-md")
            history_table(route_id, airlines, route["currency"])

        with ui.card().classes("w-full md:w-1/3"):
            ui.label("Price alert").classes("text-lg")
            active = ui.switch("Active", value=True)
            threshold = ui.number(f"Threshold ({route['currency']})", min=1).classes("w-full")
            threshold.bind_enabled_from(active, "value")
            hint = ui.label("").classes("text-caption text-grey-7")
            threshold.on_value_change(lambda e: hint.set_text(convert_hint(e.value, currency.value)))

            def on_currency_change(e):
                threshold.props(f'label="Threshold ({e.value})"')
                hint.set_text(convert_hint(threshold.value, e.value))
                if alert_state["exists"] and e.value != route["currency"]:
                    ui.notify(
                        f"After saving, your alert threshold will be interpreted in {e.value}",
                        type="warning",
                    )

            currency.on_value_change(on_currency_change)

            def save_alert():
                if active.value and threshold.value is None:
                    ui.notify("Enter a price threshold", type="warning")
                    return
                if threshold.value is None:
                    ui.notify("Set a threshold before saving the alert", type="warning")
                    return
                body = {"threshold_price": threshold.value, "is_active": active.value}
                if call("PUT", f"/routes/{route_id}/alert", json=body) is not None:
                    alert_state["exists"] = True
                    ui.notify("Alert saved", type="positive")

            def do_delete_alert():
                if call("DELETE", f"/routes/{route_id}/alert") is not None:
                    alert_state["exists"] = False
                    threshold.value = None
                    ui.notify("Alert deleted", type="positive")

            def delete_alert():
                if not alert_state["exists"]:
                    ui.notify("This route has no alert yet", type="warning")
                    return
                confirm_delete("The price alert for this route will be deleted.", do_delete_alert)

            with ui.row():
                ui.button("Save", on_click=save_alert)
                ui.button("Delete", color="negative", on_click=delete_alert)

    alert = call("GET", f"/routes/{route_id}/alert", notify=False)
    if alert:
        alert_state["exists"] = True
        threshold.value = float(alert["threshold_price"])
        active.value = alert["is_active"]


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Fare Hunter",
        port=8080,
        host="0.0.0.0",
        show=False,
        storage_secret=settings.NICEGUI_STORAGE_SECRET.get_secret_value(),
    )
