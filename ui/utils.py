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

# Toggle value -> `layover` query param (None means no filter)
LAYOVER_FILTERS = {"all": None, "direct": False, "layover": True}

HISTORY_COLUMNS: list[dict[str, Any]] = [
    {"name": "fetched_at", "label": "Fetched", "field": "fetched_at", "align": "left", "sortable": True},
    {"name": "airline", "label": "Airline", "field": "airline", "align": "left", "sortable": True},
    {"name": "price", "label": "Price", "field": "price", "align": "left", "sortable": True},
    {"name": "departure_date", "label": "Departure", "field": "departure_date", "align": "left"},
    {"name": "duration", "label": "Departure duration", "field": "duration", "align": "left", "sortable": True},
    {"name": "return_date", "label": "Return", "field": "return_date", "align": "left"},
    {"name": "layover", "label": "Layover", "field": "layover", "align": "left"},
]

# Green "Direct" chip, orange "Layover" chip, grey dash when the value is unknown (older records)
LAYOVER_SLOT = """
<q-td :props="props">
    <q-chip v-if="props.row.layover === true" dense square color="orange-2" text-color="orange-10" icon="connecting_airports">
        Layover
    </q-chip>
    <q-chip v-else-if="props.row.layover === false" dense square color="green-2" text-color="green-10" icon="flight">
        Direct
    </q-chip>
    <span v-else class="text-grey-6">-</span>
</q-td>
"""


def error_text(response: httpx.Response) -> str:
    """Turn an API error response into a message that is safe to show to the user."""
    try:
        body = response.json()
        detail = body.get("detail") if isinstance(body, dict) else None
    except ValueError:
        detail = None

    if response.status_code == 401:
        return "Invalid email or password"
    if response.status_code == 429:
        return "Too many attempts. Please try again in a moment."
    if response.status_code >= 500:
        return "Server error. Please try again later."
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
    return f"Something went wrong (HTTP {response.status_code})"


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


def local_today() -> date:
    """Today's date in the app timezone (not the server's)."""
    return datetime.now(LOCAL_TZ).date()


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


def frame(title: str, demo: bool = False):
    with ui.header().classes("items-center justify-between"):
        ui.label("🛫 Fare Hunter").classes("text-lg font-bold")
        if not demo:
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
        if converted and rate is not None:
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
            "return_time": format_time(item.get("return_time")) if item.get("return_date") else "",
            "duration": format_minutes(item.get("duration")),
            # Raw bool (or None); LAYOVER_SLOT decides how to render it
            "layover": item.get("layover"),
        }
        for item in history
    ]


def date_time_slot(date_field: str, time_field: str) -> str:
    return f"""
    <q-td :props="props">
        <span>{{{{ props.row.{date_field} }}}}</span>
        <span v-if="props.row.{time_field}" style="color: #1f2a5a; font-weight: 700; margin-left: 6px;">
            {{{{ props.row.{time_field} }}}}
        </span>
    </q-td>
    """


def history_table(
    base_path: str,
    airlines: dict[str, str],
    target_currency: str,
    airline_id: str | None = None,
) -> ui.table:
    """Price history table with server-side sorting, layover filter and paging.

    base_path is the route prefix, e.g. "/routes/{id}" or "/featured/routes/{id}".
    """
    table: ui.table

    layover_toggle = ui.toggle(
        {"all": "All", "direct": "Direct", "layover": "With layover"},
        value="all",
        on_change=lambda _: load({**table.pagination, "page": 1}),
    )

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
    table.add_slot("body-cell-departure_date", date_time_slot("departure_date", "departure_time"))
    table.add_slot("body-cell-return_date", date_time_slot("return_date", "return_time"))
    table.add_slot("body-cell-layover", LAYOVER_SLOT)

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
        params = {
            "sort_by": sort_by,
            "order": "desc" if descending else "asc",
            "limit": page_size + 1,
            "offset": offset,
        }
        layover = LAYOVER_FILTERS[layover_toggle.value]
        if layover is not None:
            params["layover"] = layover
        if airline_id is not None:
            params["airline_id"] = airline_id

        data = call("GET", f"{base_path}/history", params=params, notify=False) or []

        has_next = len(data) > page_size
        table.rows = history_rows(data[:page_size], airlines, target_currency)
        table.pagination = {**p, "rowsNumber": offset + len(table.rows) + (1 if has_next else 0)}
        table.update()

    table.on("request", lambda e: load(e.args["pagination"]))
    load(table.pagination)
    return table


def airline_history(base_path: str, airlines: dict[str, str], currency: str) -> None:
    """Cheapest offer per airline; clicking a row shows that airline's history."""

    def show_airline(airline_id: str | None) -> None:
        detail.clear()
        if airline_id is None:
            return
        with detail:
            ui.button("← All airlines", on_click=lambda: show_airline(None)).props("flat dense")
            history_table(base_path, airlines, currency, airline_id=airline_id)

    rows = call("GET", f"{base_path}/airlines", notify=False) or []
    table = ui.table(
        columns=[
            {"name": "airline", "label": "Airline", "field": "airline", "align": "left"},
            {"name": "price", "label": "Cheapest", "field": "price_text", "align": "left"},
            {"name": "departure", "label": "Departure", "field": "departure", "align": "left"},
            {"name": "offers", "label": "Offers", "field": "offers_count", "align": "right"},
        ],
        rows=[
            {
                **r,
                "airline": airlines.get(r["airline_id"], "?"),
                "price_text": f"{float(r['price']):.2f} {r['currency']}",
                "departure": format_date(r["departure_date"]),
            }
            for r in rows
        ],
        row_key="airline_id",
    )
    detail = ui.column().classes("w-full")
    table.on("rowClick", lambda e: show_airline(e.args[1]["airline_id"]))
    show_airline(rows[0]["airline_id"] if rows else None)


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
