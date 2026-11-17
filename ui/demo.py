from nicegui import ui

from ui.utils import (
    airline_history,
    airport_label,
    call,
    fetch_all,
    format_date,
    frame,
    show_stats,
)


def featured_page():
    frame("Featured routes", demo=True)

    airports = fetch_all("/airports")
    codes = {a["id"]: a["iata_code"] for a in airports}
    cities = {a["id"]: a["city"] for a in airports}

    routes = fetch_all("/featured/routes/")
    if not routes:
        ui.label("No featured routes yet.")
        return

    for r in routes:
        round_trip = r["return_date"] is not None
        with ui.card().classes("w-full q-pa-sm"):
            with ui.row().classes("w-full items-center justify-between no-wrap"):
                with ui.row().classes("items-baseline gap-2"):
                    ui.label(f"{codes.get(r['origin_id'], '?')} → {codes.get(r['destination_id'], '?')}").classes(
                        "text-h6 text-weight-bold"
                    )
                    ui.label(f"{cities.get(r['origin_id'], '?')} → {cities.get(r['destination_id'], '?')}").classes(
                        "text-caption text-grey-7"
                    )
                ui.chip(
                    "Round trip" if round_trip else "One way",
                    icon="sync" if round_trip else "arrow_forward",
                ).props("dense")

            with ui.row().classes("w-full items-center justify-between no-wrap"):
                with ui.row().classes("items-center gap-1"):
                    ui.icon("flight_takeoff", color="primary", size="sm")
                    ui.label(format_date(r["departure_date"])).classes("text-body2")
                    if round_trip:
                        ui.icon("arrow_forward", size="xs", color="grey-6")
                        ui.icon("flight_land", color="primary", size="sm")
                        ui.label(format_date(r["return_date"])).classes("text-body2")
                ui.button(
                    "Details",
                    icon="chevron_right",
                    on_click=lambda rid=r["id"]: ui.navigate.to(f"/routes/{rid}"),
                ).props("flat dense color=primary")


def featured_route_page(route_id: str):
    frame("Featured route", demo=True)
    ui.button("← Back", on_click=lambda: ui.navigate.to("/")).props("flat")

    route = call("GET", f"/featured/routes/{route_id}", notify=False)
    if route is None:
        ui.label("Route not found")
        return

    airports = {a["id"]: a for a in fetch_all("/airports")}
    airlines = {a["id"]: a["name"] for a in fetch_all("/airlines")}

    with ui.card().classes("w-full"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("flight_takeoff").classes("text-2xl text-primary")
            ui.label(airport_label(airports.get(route["origin_id"]))).classes("text-lg")
            ui.icon("arrow_forward").classes("text-grey-6")
            ui.icon("flight_land").classes("text-2xl text-primary")
            ui.label(airport_label(airports.get(route["destination_id"]))).classes("text-lg")
        ui.label("Round trip" if route["return_date"] else "One way").classes("text-caption text-grey-7")
        ui.label("All prices are for 1 passenger").classes("text-caption text-grey-7")

    with ui.row().classes("w-full items-start gap-4 flex-col md:flex-row md:flex-nowrap"):
        with ui.card().classes("w-full md:flex-1 min-w-0"):
            ui.label("Statistics").classes("text-lg")
            show_stats(call("GET", f"/featured/routes/{route_id}/stats", notify=False), route["currency"])
            ui.label("History").classes("text-lg q-mt-md")
            airline_history(f"/featured/routes/{route_id}", airlines, route["currency"])
