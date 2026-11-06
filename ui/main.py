from datetime import date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from nicegui import app, ui

from app.core.config import settings

API_URL = settings.API_URL

ROUTES_PER_PAGE = 5
CURRENCIES = ["PLN", "EUR", "USD", "GBP"]

FIELD_LABELS = {
    "first_name": "First name",
    "email": "Email",
    "password": "Password",
}

PASSWORD_HINT = "At least 8 characters, with upper and lower case letters, a digit and a special character"

LOCAL_TZ = ZoneInfo(settings.APP_TIMEZONE)

HISTORY_PAGE_SIZE = 10

HISTORY_COLUMNS: list[dict[str, Any]] = [
    {"name": "fetched_at", "label": "Fetched", "field": "fetched_at", "align": "left", "sortable": True},
    {"name": "airline", "label": "Airline", "field": "airline", "align": "left", "sortable": True},
    {"name": "price", "label": "Price", "field": "price", "align": "right", "sortable": True},
    {
        "name": "departure_date",
        "label": "Departure",
        "field": "departure_date",
        "align": "left",
    },
    {"name": "duration", "label": "Departure duration", "field": "duration", "align": "left"},
    {"name": "return_date", "label": "Return", "field": "return_date", "align": "left"},
]


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


def max_day() -> date:
    """Latest departure or return date the API accepts."""
    return date.today() + timedelta(days=settings.route.max_days_ahead)


def format_date(value: str | None) -> str:
    parsed = parse_date(value)
    return parsed.strftime("%d.%m.%Y") if parsed else "-"


def format_datetime(value: str | None) -> str:
    if not value:
        return "-"
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return value
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(LOCAL_TZ).strftime("%d.%m.%Y %H:%M")


def format_price(value, currency: str) -> str:
    if value is None:
        return "-"
    return f"{float(value):,.2f}".replace(",", " ") + f" {currency}"


def format_minutes(value: int | None) -> str:
    if value is None:
        return "-"
    hours, minutes = divmod(int(value), 60)
    return f"{hours}h {minutes:02d}m"


def format_time(value: str | None) -> str:
    return value[:5] if value else ""


def airport_label(airport: dict | None) -> str:
    if airport is None:
        return "Unknown airport"
    name = airport.get("name")
    base = f"{airport['city']} ({airport['iata_code']})"
    return f"{base} · {name}" if name else base


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


def confirm_delete(message: str, on_confirm) -> None:
    """Show a confirmation dialog and run on_confirm only if the user agrees."""
    with ui.dialog() as dialog, ui.card().classes("min-w-[320px]"):
        ui.label("Are you sure?").classes("text-lg")
        ui.label(message).classes("text-grey-8")
        with ui.row().classes("w-full justify-end q-mt-md"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            def confirmed():
                dialog.close()
                on_confirm()

            ui.button("Delete", color="negative", on_click=confirmed)
    dialog.open()


def stat_tile(label: str, value: str, original: str | None = None):
    with ui.card().classes("items-center min-w-[120px]"):
        ui.label(label).classes("text-caption text-grey-7")
        ui.label(value).classes("text-h6")
        if original:
            ui.label(original).classes("text-caption text-grey-6")


def get_rate(base: str, quote: str) -> float | None:
    """Exchange rate base -> quote, or None if the API is unavailable."""
    if base == quote:
        return 1.0
    data = call(
        "GET",
        "/currency/convert",
        params={"amount": 1, "base": base, "quote": quote},
        notify=False,
    )
    return float(data["result"]) if data else None


def convert_hint(amount, base: str, quote: str = "PLN") -> str:
    if amount is None or base == quote:
        return ""
    data = call(
        "GET",
        "/currency/convert",
        params={"amount": amount, "base": base, "quote": quote},
        notify=False,
    )
    if not data:
        return ""
    return "≈ " + format_price(data["result"], quote)


def show_stats(stats: dict | None, target_currency: str):
    if not stats or not stats.get("sample_count"):
        ui.label("No data yet, wait for the first price fetch").classes("text-grey-7")
        return

    source_currency = stats.get("currency") or target_currency
    rate = get_rate(source_currency, target_currency)
    converted = rate is not None and source_currency != target_currency

    def tile(label: str, value) -> None:
        if converted:
            stat_tile(
                label,
                "≈ " + format_price(float(value) * rate, target_currency),
                format_price(value, source_currency),
            )
        else:
            stat_tile(label, format_price(value, source_currency))

    with ui.row().classes("w-full gap-4"):
        tile("Lowest", stats["min_price"])
        tile("Average", stats["avg_price"])
        tile("Highest", stats["max_price"])
    ui.label(f"Samples: {stats['sample_count']} from the last {stats['period_days']} days").classes(
        "text-caption text-grey-7"
    )
    if converted:
        ui.label(f"Prices converted from {source_currency} to {target_currency} at the current exchange rate").classes(
            "text-caption text-grey-7"
        )


def history_rows(history: list, airlines: dict[str, str], target_currency: str) -> list[dict]:
    # One rate lookup per source currency per page, not per row
    rates: dict[str, float | None] = {}

    def price_cell(item: dict) -> str:
        source = item.get("currency", "")
        value = item.get("price")
        if value is None or source == target_currency:
            return format_price(value, source)
        if source not in rates:
            rates[source] = get_rate(source, target_currency)
        rate = rates[source]
        if rate is None:
            return format_price(value, source)
        return "≈ " + format_price(float(value) * rate, target_currency)

    return [
        {
            "id": item.get("id"),
            "fetched_at": format_datetime(item.get("fetched_at")),
            "airline": airlines.get(item.get("airline_id"), "Unknown"),
            "price": price_cell(item),
            "departure_date": format_date(item.get("departure_date")),
            "departure_time": format_time(item.get("departure_time")),
            "return_date": format_date(item.get("return_date")),
            "duration": format_minutes(item.get("duration")),
        }
        for item in history
    ]


def history_table(route_id: str, airlines: dict[str, str], target_currency: str):
    """Price history table with server-side sorting and paging."""
    table = ui.table(
        columns=HISTORY_COLUMNS,
        rows=[],
        row_key="id",
        pagination={
            "sortBy": "fetched_at",
            "descending": True,
            "page": 1,
            "rowsPerPage": HISTORY_PAGE_SIZE,
            "rowsNumber": 0,
        },
    ).classes("w-full")
    table.add_slot(
        "body-cell-departure_date",
        """
        <q-td :props="props">
            <span>{{ props.row.departure_date }}</span>
            <span v-if="props.row.departure_time" style="color: #1f2a5a; font-weight: 700; margin-left: 6px;">
                {{ props.row.departure_time }}
            </span>
        </q-td>
        """,
    )
    table.props('binary-state-sort no-data-label="No history" :rows-per-page-options="[]"')
    table.props(""":pagination-label="(first, end) => first + ' - ' + end" """)
    table.props(
        'table-header-class="text-weight-bold text-subtitle2 text-indigo-10 bg-blue-1" table-class="text-body1"'
    )
    table.props('table-style="font-size: 15px;" bordered separator="cell"')

    last_sort = {"sortBy": "fetched_at", "descending": True}

    def load(p: dict) -> None:
        sort_by = p.get("sortBy") or "fetched_at"
        descending = bool(p.get("descending"))

        if (sort_by, descending) != (last_sort["sortBy"], last_sort["descending"]):
            p = {**p, "page": 1}
            last_sort.update(sortBy=sort_by, descending=descending)

        page_size = p["rowsPerPage"]
        offset = (p["page"] - 1) * page_size
        data = (
            call(
                "GET",
                f"/routes/{route_id}/history",
                params={
                    "sort_by": sort_by,
                    "order": "desc" if descending else "asc",
                    "limit": page_size + 1,
                    "offset": offset,
                },
                notify=False,
            )
            or []
        )

        has_next = len(data) > page_size
        table.rows = history_rows(data[:page_size], airlines, target_currency)
        table.pagination = {**p, "rowsNumber": offset + len(table.rows) + (1 if has_next else 0)}
        table.update()

    table.on("request", lambda e: load(e.args["pagination"]))
    load(table.pagination)
    return table


def set_day_range(picker: ui.date, min_day: date, max_day_value: date):
    picker.props(f":options=\"(d) => d >= '{min_day:%Y/%m/%d}' && d <= '{max_day_value:%Y/%m/%d}'\"")


def date_input(label: str, min_day: date, value: str = ""):
    with ui.input(label, value=value).classes("w-full").props("readonly") as field:
        with ui.menu().props("no-parent-event") as menu:
            with ui.date().bind_value(field) as picker:
                with ui.row().classes("justify-end"):
                    ui.button("OK", on_click=menu.close).props("flat")
        set_day_range(picker, min_day, max_day())
        field.on("click", menu.open)
        with field.add_slot("append"):
            ui.icon("close").on("click", lambda: field.set_value("")).classes("cursor-pointer q-mr-xs")
            ui.icon("edit_calendar").classes("cursor-pointer")
    return field, picker


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
                with ui.card().classes("w-full"):
                    origin_code = codes.get(r["origin_id"], "?")
                    destination_code = codes.get(r["destination_id"], "?")
                    ui.label(f"{origin_code} → {destination_code}").classes("text-lg")

                    details = f"Departure: {format_date(r['departure_date'])}"
                    if r["return_date"]:
                        details += f"   Return: {format_date(r['return_date'])}"
                    ui.label(details)

                    with ui.row():
                        ui.button("Details", on_click=lambda rid=r["id"]: ui.navigate.to(f"/routes/{rid}"))
                        label = f"{origin_code} → {destination_code}"
                        ui.button(
                            "Delete",
                            color="negative",
                            on_click=lambda rid=r["id"], lbl=label: ask_remove(rid, lbl),
                        )

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

    with ui.row().classes("w-full items-start"):
        with ui.card().classes("w-2/3"):
            ui.label("Statistics").classes("text-lg")
            show_stats(call("GET", f"/routes/{route_id}/stats", notify=False), route["currency"])
            ui.label("History").classes("text-lg q-mt-md")
            history_table(route_id, airlines, route["currency"])

        with ui.card().classes("w-1/3"):
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
