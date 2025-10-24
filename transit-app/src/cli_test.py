import typer
from rich.table import Table
from rich.console import Console
import crud

app = typer.Typer(help="Transit CRUD CLI")
console = Console()

####################
## Route Commands ##
####################

@app.command("route-add")
def add_route(
    route_id: int = typer.Argument(...),
    name: str = typer.Argument(...),
    route_type: str = typer.Option(..., "--type", "-t"),
):
    route = crud.add_route(route_id, name, route_type)
    console.print(f"✅ Added route: {route['route_name']} (ID: {route['route_id']})")

@app.command("route-get")    
def get_route(route_name: str):
    route = crud.get_route(route_name)
    table = Table(title=f"Route {route['route_name']}")
    for key, value in route.items():
        table.add_row(key, str(value))
    console.print(table)

@app.command("route-list")
def list_routes():
    routes = crud.list_routes()
    table = Table(title="Routes", show_lines=True)
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Type")
    for route in routes:
        table.add_row(str(route["route_id"]), route["route_name"], route["route_type"])
    console.print(table)

@app.command("route-update")
def update_route(
    route_id: int = typer.Argument(...),
    name: str = typer.Option(None, "--name", "-n"),
    rtype: str = typer.Option(None, "--type", "-t"),
):
    updated = crud.update_route(route_id, route_name=name, route_type=rtype)
    console.print(f"✅ Updated route {updated['route_id']}")

@app.command("route-delete")
def delete_route(route_id: int = typer.Argument(...)):
    crud.delete_route(route_id)
    console.print(f"🗑️ Deleted route {route_id}")


######################
## Vehicle Commands ##
######################

@app.command("vehicle-add")
def add_vehicle(
    vehicle_id: int = typer.Argument(...),
    vehicle_class: str = typer.Option(..., "--class", "-c", help="Vehicle Class: Bus/Metro"),
    manufacturer: str = typer.Option(..., "--manufacturer", "-m"),
    manufacture_year: int = typer.Option(..., "--year", "-y", min=1960, max=2026),
    vehicle_type: str = typer.Option(..., "--type", "-t", help="Standard, Articulated, etc."),
    capacity: int | None = typer.Option(None, "--capacity", "-n", min=0, max=500, help="Passenger capacity"),
):
    """Create a new vehicle record."""
    result = crud.add_vehicle(vehicle_id, vehicle_class, manufacturer, manufacture_year, vehicle_type, capacity)
    console.print(f"Added vehicle {result['vehicle_id']}")


@app.command("vehicle-get")
def get_vehicle(vehicle_id: int = typer.Argument(..., help="Vehicle ID")):
    """Show one vehicle."""
    v = crud.get_vehicle(vehicle_id)
    table = Table(title=f"Vehicle {v['vehicle_id']}")
    table.add_column("Field")
    table.add_column("Value")
    for field in ["vehicle_id", "vehicle_class", "manufacturer", "manufacture_year", "vehicle_type", "capacity"]:
        table.add_row(field, str(v[field]))
    console.print(table)


@app.command("vehicle-list")
def vehicle_list(
    vehicle_id: int | None = None,
    vehicle_class: str | None = None,
    manufacturer: str | None = None,
    manufacture_year: tuple[str, int] | None = None,
    vehicle_type: str | None = None,
    capacity: tuple[str, int] | None = None
):
    """List vehicles with optional filters."""
    vehicles = crud.list_vehicles(vehicle_id, vehicle_class, manufacturer, manufacture_year, vehicle_type, capacity)
    table = Table(title="Vehicles")
    for col in ["ID", "Class", "Manufacturer", "Year", "Type", "Capacity"]:
        table.add_column(col)
    for v in vehicles:
        table.add_row(
            str(v["vehicle_id"]),
            v["vehicle_class"],
            v["manufacturer"],
            str(v["manufacture_year"]),
            v["vehicle_type"],
            str(v["capacity"]) if v["capacity"] is not None else "—"
        )
    console.print(table)


@app.command("vehicle-update")
def vehicle_update(
    vehicle_id: int = typer.Argument(...),
    vehicle_class: str | None = typer.Option(None, "--class", "-c"),
    manufacturer: str | None = typer.Option(None, "--manufacturer", "-m"),
    manufacture_year: int | None = typer.Option(None, "--year", "-y"),
    vehicle_type: str | None = typer.Option(None, "--type", "-t"),
    capacity: int | None = typer.Option(None, "--capacity", "-n"),
):
    """Update one or more fields on a vehicle."""
    result = crud.update_vehicle(vehicle_id, vehicle_class, manufacturer, manufacture_year, vehicle_type, capacity)
    console.print(f"Updated vehicle {result['vehicle_id']}")


@app.command("vehicle-delete")
def vehicle_delete(vehicle_id: int = typer.Argument(..., help="Vehicle ID")):
    """Delete a vehicle by ID."""
    crud.delete_vehicle(vehicle_id)
    console.print(f"Deleted vehicle {vehicle_id}")


#####################
## Driver Commands ##
#####################

@app.command("driver-add")
def driver_add(
    driver_name: str = typer.Argument(...),
    driver_classification: str = typer.Option(..., "--class", "-c"),
    start_date: str | None = typer.Option(None, "--start", "-s"),
    pay: float = typer.Option(..., "--pay", "-p"),
):
    """Create a new driver."""
    result = crud.add_driver(driver_name, driver_classification, start_date, pay)
    console.print(f"Added driver {result['driver_name']}")


@app.command("driver-get")
def driver_get(driver_id: int = typer.Argument(...)):
    """Retrieve a driver by ID."""
    d = crud.get_driver(driver_id)
    table = Table(title=f"Driver {d['driver_name']}")
    table.add_column("Field")
    table.add_column("Value")
    for field in ["driver_id", "driver_name", "driver_classification", "start_date", "pay"]:
        table.add_row(field, str(d[field]))
    console.print(table)


@app.command("driver-list")
def driver_list():
    """List all drivers."""
    drivers = crud.list_drivers()
    table = Table(title="Drivers")
    for col in ["ID", "Name", "Class", "Start Date", "Pay"]:
        table.add_column(col)
    for d in drivers:
        table.add_row(
            str(d["driver_id"]),
            d["driver_name"],
            d["driver_classification"],
            d["start_date"].isoformat() if d["start_date"] else "—",
            f"{d['pay']:.2f}"
        )
    console.print(table)


@app.command("driver-update")
def driver_update(
    driver_id: int = typer.Argument(...),
    driver_name: str | None = typer.Option(None),
    driver_classification: str | None = typer.Option(None, "--class", "-c"),
    start_date: str | None = typer.Option(None),
    pay: float | None = typer.Option(None, "--pay", "-p"),
):
    """Update a driver."""
    result = crud.update_driver(driver_id, driver_name, driver_classification, start_date, pay)
    console.print(f"Updated driver {result['driver_name']}")


@app.command("driver-delete")
def driver_delete(driver_id: int = typer.Argument(...)):
    """Delete a driver."""
    crud.delete_driver(driver_id)
    console.print(f"Deleted driver {driver_id}")

##########################
## Maintenance Commands ##
##########################

@app.command("maintenance-add")
def add_maintenance(
    vehicle_id: int = typer.Argument(...),
    work_date: str = typer.Argument(..., help="YYYY-MM-DD"),
    work_performed: str = typer.Argument(..., help="Description"),
):
    """Create a maintenance record."""
    record = crud.add_maintenance(vehicle_id, work_date, work_performed)
    console.print(f"Added maintenance record {record['maintenance_id']} for vehicle {vehicle_id}")

@app.command("maintenance-get")
def get_maintenance(
    maintenance_id: int = typer.Argument(...),
):
    """Show one maintenance record."""
    record = crud.get_maintenance(maintenance_id)
    table = Table(title=f"Maintenance {maintenance_id}")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for k, v in record.items():
        table.add_row(k, str(v))
    console.print(table)

@app.command("maintenance-list")
def list_maintenance(
    vehicle_id: int | None = typer.Option(
        None, "--vehicle", "-v", help="Filter by vehicle ID"
    ),
    work_date: str | None = typer.Option(
        None, "--date", "-d", help="Filter by work date YYYY-MM-DD"
    ),
):
    """List maintenance records. Optionally filter by vehicle ID or work date."""
    records = crud.list_maintenance(vehicle_id, work_date)
    table = Table(title="Maintenance Records")
    for col in ("ID", "Vehicle", "Date", "Work Performed"):
        table.add_column(col)
    for r in records:
        table.add_row(
            str(r["maintenance_id"]),
            str(r["vehicle_id"]),
            r["work_date"].isoformat() if r["work_date"] else "—",
            r["work_performed"]
        )
    console.print(table)

@app.command("maintenance-update")
def update_maintenance(
    maintenance_id: int = typer.Argument(...),
    vehicle_id: int | None = typer.Option(None),
    work_date: str | None = typer.Option(None),
    work_performed: str | None = typer.Option(None),
):
    """Update a maintenance record."""
    record = crud.update_maintenance(maintenance_id, vehicle_id, work_date, work_performed)
    console.print(f"Updated maintenance record {maintenance_id}")

@app.command("maintenance-delete")
def delete_maintenance(
    maintenance_id: int = typer.Argument(...),
):
    """Delete a maintenance record."""
    crud.delete_maintenance(maintenance_id)
    console.print(f"Deleted maintenance record {maintenance_id}")

###################
## Stop Commands ##
###################

@app.command("stop-add")
def add_stop(
    stop_id: int = typer.Argument(...),
    stop_direction: str = typer.Argument(..., help="N/S/E/W (1 char)"),
    street_name: str = typer.Argument(...),
    cross_street: str = typer.Argument(...),
    latitude: float | None = typer.Option(None),
    longitude: float | None = typer.Option(None),
):
    """Create a new stop."""
    record = crud.add_stop(stop_id, stop_direction,
                           street_name, cross_street,
                           latitude, longitude)
    console.print(f"Added stop {record['stop_id']} at {record['street_name']} and "
                  f"{record['cross_street']} ({record['stop_direction']} bound).")

@app.command("stop-get")
def get_stop(stop_id: int = typer.Argument(...)):
    """Show one stop."""
    record = crud.get_stop(stop_id)
    table = Table(title=f"Stop {record['stop_id']}")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for field in ("stop_id", "stop_direction", "street_name", "cross_street", "latitude", "longitude"):
        val = record[field] if record[field] is not None else "—"
        table.add_row(field, str(val))
    console.print(table)

@app.command("stop-list")
def list_stop(street_name: str | None = typer.Option(
        None, "--street", "-s", help="Filter by primary street name"
    )):
    """List stops. Optionally filter by street name."""
    stops = crud.list_stops(street_name=street_name)
    table = Table(title="Stops")
    for col in ("ID", "Dir", "Street", "Cross", "Lat", "Lon"):
        table.add_column(col)
    for s in stops:
        table.add_row(
            str(s['stop_id']),
            s['stop_direction'],
            s['street_name'],
            s['cross_street'],
            f"{s['latitude']:.6f}" if s['latitude'] is not None else "—",
            f"{s['longitude']:.6f}" if s['longitude'] is not None else "—",
        )
    console.print(table)
    if not stops:
        console.print("No stops found.")

@app.command("stop-update")
def update_stop(
    stop_id: int = typer.Argument(...),
    stop_direction: str | None = typer.Option(None),
    street_name: str | None = typer.Option(None),
    cross_street: str | None = typer.Option(None),
    latitude: float | None = typer.Option(None),
    longitude: float | None = typer.Option(None),
):
    """Update a stop."""
    record = crud.update_stop(stop_id, stop_direction,
                              street_name, cross_street,
                              latitude, longitude)
    console.print(f"Updated stop {record['stop_id']}")

@app.command("stop-delete")
def delete_stop(stop_id: int = typer.Argument(...)):
    """Delete a stop."""
    crud.delete_stop(stop_id)
    console.print(f"Deleted stop {stop_id}")

###############
## Trip CLI  ##
###############

@app.command("trip-add")
def trip_add(
    trip_id: int = typer.Argument(..., help="Trip ID"),
    route_id: int = typer.Argument(..., help="Route ID"),
    driver_id: int = typer.Argument(..., help="Driver ID"),
    vehicle_id: int = typer.Argument(..., help="Vehicle ID"),
    trip_date: str = typer.Argument(..., help="Trip date (YYYY-MM-DD)"),
    trip_direction: str = typer.Argument(..., help="Trip direction"),
):
    trip = crud.add_trip(
        trip_id=trip_id,
        route_id=route_id,
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        trip_date=trip_date,
        trip_direction=trip_direction,
    )
    console.print(f"[green]Trip {trip['trip_id']} added.[/green]")


@app.command("trip-get")
def trip_get(trip_id: int = typer.Argument(..., help="Trip ID")):
    trip = crud.get_trip(trip_id)
    table = Table(title=f"Stop {trip['stop_id']}")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for field in ("trip_id", "route_id", "driver_id", "vehicle_id", "trip_date", "trip_direction"):
        val = trip[field] if trip[field] is not None else "—"
        table.add_row(field, str(val))
    console.print(table)


@app.command("trip-list")
def trip_list(
    trip_id: int = typer.Option(None, help="Filter by Trip ID"),
    route_id: int = typer.Option(None, help="Filter by Route ID"),
    route_name: str = typer.Option(None, help="Filter by Route name"),
    driver_id: int = typer.Option(None, help="Filter by Driver ID"),
    driver_name: str = typer.Option(None, help="Filter by Driver name"),
    vehicle_id: int = typer.Option(None, help="Filter by Vehicle ID"),
    trip_date: str = typer.Option(None, help="Filter by Trip date (YYYY-MM-DD)"),
):
    trips = crud.list_trips(
        trip_id=trip_id,
        route_id=route_id,
        route_name=route_name,
        driver_id=driver_id,
        driver_name=driver_name,
        vehicle_id=vehicle_id,
        trip_date=trip_date,
    )

    if not trips:
        console.print("No trips found matching filter criteria.")
        return

    table = Table(title="Trips", show_lines=True)
    table.add_column("trip_id")
    table.add_column("trip_date")
    table.add_column("trip_direction")
    table.add_column("route_id")
    table.add_column("route_name")
    table.add_column("driver_id")
    table.add_column("driver_name")
    table.add_column("vehicle_id")
    for trip in trips:
        table.add_row(
            str(trip["trip_id"]), 
            str(trip["trip_date"]),
            trip["trip_direction"],
            str(trip["route_id"]),
            trip["route_name"],
            str(trip["driver_id"]),
            trip["driver_name"],
            str(trip["vehicle_id"])
        )
    console.print(table)

@app.command("trip-update")
def trip_update(
    trip_id: int = typer.Argument(..., help="Trip ID"),
    route_id: int = typer.Option(None, help="New Route ID"),
    driver_id: int = typer.Option(None, help="New Driver ID"),
    vehicle_id: int = typer.Option(None, help="New Vehicle ID"),
    trip_date: str = typer.Option(None, help="New Trip date (YYYY-MM-DD)"),
    trip_direction: str = typer.Option(None, help="New Trip direction"),
):
    trip = crud.update_trip(
        trip_id=trip_id,
        route_id=route_id,
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        trip_date=trip_date,
        trip_direction=trip_direction,
    )
    console.print(f"Updated Trip {trip['trip_id']}")


@app.command("trip-delete")
def trip_delete(trip_id: int = typer.Argument(..., help="Trip ID")):
    crud.delete_trip(trip_id)
    console.print(f"Deleted trip {trip_id}")

@app.command("routes-stops-add")
def routes_stops_add(
    route_id: int = typer.Argument(..., help="Route ID"),
    stop_id: int = typer.Argument(..., help="Stop ID"),
    route_direction: str = typer.Argument(..., help="Route Direction"),
    stop_order: int = typer.Argument(..., help="Stop Order")
):
    routes_stops = crud.add_routes_stops(
        route_id=route_id,
        stop_id=stop_id,
        route_direction=route_direction,
        stop_order=stop_order
    )
    console.print(f"Stop ID {routes_stops['stop_id']} added for route ID {routes_stops['route_id']} added.")


@app.command("routes-stops-list")
def routes_stops_list(
    route_id: int = typer.Option(None, help="Route ID"),
    route_direction: str = typer.Option(None, help="Route Direction")
):
    routes_stops = crud.list_route_stop(
        route_id=route_id,
        route_direction=route_direction
    )
    if not routes_stops:
        console.print("No route stops found matching filter criteria.")
        return
    table = Table(title="Route-Stops", show_lines=True)
    table.add_column("route_id")
    table.add_column("stop_id")
    table.add_column("route_direction")
    table.add_column("stop_order")
    for route_stop in routes_stops:
        table.add_row(
            str(route_stop["route_id"]),
            str(route_stop["stop_id"]),
            route_stop["route_direction"],
            str(route_stop["stop_order"]),
        )
    console.print(table)


@app.command("routes-stops-update")
def routes_stops_update(
    route_id: int = typer.Argument(..., help="Route ID"),
    stop_id: int = typer.Argument(..., help="Stop ID"),
    route_direction: str = typer.Argument(..., help="Route Direction"),
    stop_order: int = typer.Option(..., help="New Stop Order")
):
    route_stop = crud.update_route_stop(
        route_id=route_id,
        stop_id=stop_id,
        route_direction=route_direction,
        stop_order=stop_order
    )
    console.print(
        f"Updated Route-Stop {route_stop['route_id']}-{route_stop['stop_id']} "
        f"({route_stop['route_direction']}) to order {route_stop['stop_order']}"
    )


@app.command("routes-stops-delete")
def routes_stops_delete(
    route_id: int = typer.Argument(..., help="Route ID"),
    stop_id: int = typer.Argument(..., help="Stop ID"),
    route_direction: str = typer.Argument(..., help="Route Direction")
):
    crud.delete_route_stop(
        route_id=route_id,
        stop_id=stop_id,
        route_direction=route_direction
    )
    console.print(f"Deleted Route-Stop {route_id}-{stop_id} ({route_direction})")


#####################
## Trips-Stops CLI ##
#####################

@app.command("trips-stops-add")
def trip_stops_add(
    trip_id: int = typer.Argument(..., help="Trip ID"),
    stop_id: int = typer.Argument(..., help="Stop ID"),
    arrival: str = typer.Argument(..., help="Arrival time (either HH:MM or integer minutes)"),
):
    """Add a stop to a trip. Accepts arrival time as HH:MM or raw minutes."""
    try:
        if ":" in arrival:
            trip_stop = crud.add_trip_stop_time(trip_id, stop_id, arrival)
        else:
            trip_stop = crud.add_trip_stop_minutes(trip_id, stop_id, int(arrival))
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    console.print(
        f"Added Trip-Stop {trip_stop['trip_id']}-{trip_stop['stop_id']} "
        f"(arrival {trip_stop['arrival_hhmm']})"
    )

@app.command("trips-stops-list")
def trip_stops_list(
    trip_id: int = typer.Option(None, help="Trip ID"),
):
    trip_stops = crud.list_trip_stop(trip_id=trip_id)
    if not trip_stops:
        console.print(f"No stops found for trip {trip_id}.")
        return

    table = Table(title=f"Trip {trip_id} Stops", show_lines=True)
    table.add_column("trip_id")
    table.add_column("route_name")
    table.add_column("stop_id")
    table.add_column("street_name")
    table.add_column("cross_street")
    table.add_column("arrival_time (min)")
    table.add_column("arrival_time (HH:MM)")
    for ts in trip_stops:
        table.add_row(
            str(ts["trip_id"]),
            ts["route_name"],
            str(ts["stop_id"]),
            ts["street_name"],
            ts["cross_street"],
            str(ts["arrival_time"]),
            ts["arrival_hhmm"]
        )
    console.print(table)

@app.command("trips-stops-update")
def trip_stops_update(
    trip_id: int = typer.Argument(..., help="Trip ID"),
    stop_id: int = typer.Argument(..., help="Stop ID"),
    arrival: str = typer.Argument(..., help="New arrival time (HH:MM or minutes)"),
):
    try:
        if ":" in arrival:
            hour, minute = map(int, arrival.split(":"))
            arrival_time = hour * 60 + minute
        else:
            arrival_time = int(arrival)
    except Exception:
        console.print("[red]Invalid time format. Use HH:MM or integer minutes.[/red]")
        raise typer.Exit(code=1)

    trip_stop = crud.update_trip_stop(trip_id=trip_id, stop_id=stop_id, arrival_time=arrival_time)
    console.print(
        f"Updated Trip-Stop {trip_stop['trip_id']}-{trip_stop['stop_id']} "
        f"to arrival {trip_stop['arrival_hhmm']}"
    )


@app.command("trips-stops-delete")
def trip_stops_delete(
    trip_id: int = typer.Argument(..., help="Trip ID"),
    stop_id: int = typer.Argument(..., help="Stop ID")
):
    crud.delete_trip_stop(trip_id, stop_id)
    console.print(f"Deleted Trip-Stop {trip_id}-{stop_id}")

if __name__ == "__main__":
    app()
