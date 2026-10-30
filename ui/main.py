import json
from datetime import date, timedelta

import httpx
from nicegui import app, ui

from app.core.config import settings

API_URL = "http://localhost:8000"

ROUTES_PER_PAGE = 5

FIELD_LABELS = {
    "first_name": "First name",
    "email": "Email",
    "password": "Password",
}

PASSWORD_HINT = "At least 8 characters, with upper and lower case letters, a digit and a special character"


def error_text(response: httpx.Response) -> str:
    try:
        detail = response.json().get("detail")
    except ValueError:
        detail = None

    if response.status_code == 401:
        return "Invalid email or password"
    if response.status_code in (409, 422) and isinstance(detail, str):
        return detail
    if response.status_code == 422:
        try:
            lines = []
            for e in response.json()["detail"]:
                field = e["loc"][-1]
                label = FIELD_LABELS.get(field, field.replace("_", " ").capitalize())
                msg = e["msg"].removeprefix("Value error, ")
                if msg.startswith("must "):
                    lines.append(f"{label} {msg}")
                else:
                    lines.append(f"{label}: {msg}")
            return "\n".join(lines)
        except (ValueError, KeyError, TypeError):
            pass
    return f"{response.status_code}: {response.text}"


def call(method: str, path: str, notify: bool = True, **kwargs):
    headers = {}
    token = app.storage.user.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        with httpx.Client(base_url=API_URL, timeout=15) as client:
            response = client.request(method, path, headers=headers, **kwargs)
    except httpx.HTTPError as exc:
        ui.notify(f"Cannot connect to API: {exc}", type="negative", multi_line=True)
        return None

    if response.status_code == 401 and path != "/auth/token":
        app.storage.user.clear()
        ui.navigate.to("/login")
        return None

    if response.is_error:
        if notify:
            ui.notify(error_text(response), type="negative", multi_line=True)
        return None

    if not response.content:
        return {}
    return response.json()


def parse_date(text: str | None) -> date | None:
    try:
        return date.fromisoformat(text) if text else None
    except ValueError:
        return None


def fetch_all(path: str, page_size: int = 100) -> list:
    items: list = []
    offset = 0
    while True:
        batch = call("GET", path, params={"limit": page_size, "offset": offset}) or []
        items.extend(batch)
        if len(batch) < page_size:
            return items
        offset += page_size


def require_login() -> bool:
    if not app.storage.user.get("token"):
        ui.navigate.to("/login")
        return False
    return True


def logout():
    app.storage.user.clear()
    ui.navigate.to("/login")


def frame(title: str):
    with ui.header().classes("items-center justify-between"):
        ui.label("🛫 Fare Hunter").classes("text-lg font-bold")
        with ui.row():
            ui.button("Routes", on_click=lambda: ui.navigate.to("/")).props("flat color=white")
            ui.button("Log out", on_click=logout).props("flat color=white")
    ui.label(title).classes("text-2xl q-my-md")


def stat_tile(label: str, value: str):
    with ui.card().classes("items-center min-w-[120px]"):
        ui.label(label).classes("text-caption text-grey-7")
        ui.label(value).classes("text-h6")


def format_price(value, currency: str) -> str:
    if value is None:
        return "-"
    return f"{float(value):,.2f}".replace(",", " ") + f" {currency}"


def show_stats(stats: dict | None):
    if not stats or not stats.get("sample_count"):
        ui.label("No data yet, wait for the first price fetch").classes("text-grey-7")
        return

    currency = stats.get("currency") or ""
    with ui.row().classes("w-full gap-4"):
        stat_tile("Lowest", format_price(stats["min_price"], currency))
        stat_tile("Average", format_price(stats["avg_price"], currency))
        stat_tile("Highest", format_price(stats["max_price"], currency))
    ui.label(f"Samples: {stats['sample_count']} from the last {stats['period_days']} days").classes(
        "text-caption text-grey-7"
    )


def show_history(history):
    if not history:
        ui.label("No history").classes("text-grey-7")
        return
    if isinstance(history, list) and isinstance(history[0], dict):
        columns = [{"name": k, "label": k, "field": k, "align": "left"} for k in history[0]]
        ui.table(columns=columns, rows=history).classes("w-full")
    else:
        ui.code(json.dumps(history, indent=2, ensure_ascii=False), language="json")


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
        email = ui.input(
            "Email",
            validation={"Enter a valid email address": lambda v: "@" in v},
        ).props("type=email").classes("w-full")
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
    options = {a["id"]: f'{a["iata_code"]} – {a["city"]}' for a in airports}

    page = {"index": 0}
    routes_box = ui.column().classes("w-full")

    def remove(route_id: str):
        if call("DELETE", f"/routes/{route_id}") is not None:
            ui.notify("Route deleted", type="positive")
            refresh()

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
                with ui.card().classes("w-full"):
                    origin_code = codes.get(r["origin_id"], "?")
                    destination_code = codes.get(r["destination_id"], "?")
                    ui.label(f"{origin_code} → {destination_code}").classes("text-lg")
                    ui.label(f"Departure: {r['departure_date']}   Return: {r['return_date'] or '-'}")
                    with ui.row():
                        ui.button("Details", on_click=lambda rid=r["id"]: ui.navigate.to(f"/routes/{rid}"))
                        ui.button("Delete", color="negative", on_click=lambda rid=r["id"]: remove(rid))

            with ui.row().classes("w-full items-center justify-between"):
                prev_button = ui.button("← Previous", on_click=lambda: change_page(-1)).props("flat")
                prev_button.set_enabled(page["index"] > 0)
                ui.label(f"Page {page['index'] + 1}")
                next_button = ui.button("Next →", on_click=lambda: change_page(1)).props("flat")
                next_button.set_enabled(has_next)

    def set_min_day(picker: ui.date, min_day: date):
        picker.props(f':options="(d) => d >= \'{min_day:%Y/%m/%d}\'"')

    def date_input(label: str, min_day: date):
        with ui.input(label).classes("w-full").props("readonly") as field:
            with ui.menu().props("no-parent-event") as menu:
                with ui.date().bind_value(field) as picker:
                    with ui.row().classes("justify-end"):
                        ui.button("OK", on_click=menu.close).props("flat")
            set_min_day(picker, min_day)
            field.on("click", menu.open)
            with field.add_slot("append"):
                ui.icon("close").on("click", lambda: field.set_value("")).classes("cursor-pointer q-mr-xs")
                ui.icon("edit_calendar").classes("cursor-pointer")
        return field, picker

    with ui.expansion("Add new route", icon="add").classes("w-full"):
        origin = ui.select(options, label="From", with_input=True).classes("w-full")
        destination = ui.select(options, label="To", with_input=True).classes("w-full")
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
            set_min_day(return_picker, min_return)
            ret = parse_date(returning.value)
            if ret is not None and ret < min_return:
                returning.set_value("")

        departure.on_value_change(on_departure_change)

        def reset_form():
            origin.set_value(None)
            destination.set_value(None)
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

            ret = parse_date(returning.value)
            if returning.value and (ret is None or ret <= dep):
                ui.notify("Return must be at least one day after departure", type="warning")
                return

            body = {
                "origin_id": origin.value,
                "destination_id": destination.value,
                "departure_date": departure.value,
                "return_date": returning.value or None,
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
    frame("Route details")
    ui.button("← Back", on_click=lambda: ui.navigate.to("/")).props("flat")

    alert_state = {"exists": False}

    with ui.row().classes("w-full items-start"):
        with ui.card().classes("w-2/3"):
            ui.label("Statistics").classes("text-lg")
            show_stats(call("GET", f"/routes/{route_id}/stats", notify=False))
            ui.label("History").classes("text-lg q-mt-md")
            show_history(call("GET", f"/routes/{route_id}/history", notify=False))

        with ui.card().classes("w-1/3"):
            ui.label("Price alert").classes("text-lg")
            threshold = ui.number("Threshold (PLN)", min=1).classes("w-full")
            active = ui.switch("Active", value=True)

            def save_alert():
                if threshold.value is None:
                    ui.notify("Enter a price threshold", type="warning")
                    return
                body = {"threshold_price": threshold.value, "is_active": active.value}
                if call("PUT", f"/routes/{route_id}/alert", json=body) is not None:
                    alert_state["exists"] = True
                    ui.notify("Alert saved", type="positive")

            def delete_alert():
                if not alert_state["exists"]:
                    ui.notify("This route has no alert yet", type="warning")
                    return
                if call("DELETE", f"/routes/{route_id}/alert") is not None:
                    alert_state["exists"] = False
                    threshold.value = None
                    ui.notify("Alert deleted", type="positive")

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
        storage_secret=settings.NICEGUI_STORAGE_SECRET,
    )