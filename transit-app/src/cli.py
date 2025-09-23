import typer
import crudCLI

app = typer.Typer(help="Transit CRUD CLI")

####################
## Route Commands ##
####################

@app.command("route-add")
def add_route(
    route_id: int = typer.Argument(...),
    name: str = typer.Argument(...),
    route_type: str = typer.Option(..., "--type", "-t"),
):
    """Create a new route record."""
    crudCLI.add_route(route_id, name, route_type)

@app.command("route-get")    
def get_route(
    route_name: str = typer.Argument(..., help="Route name to fetch"),
):
    """Show one route by route name."""
    crudCLI.get_route(route_name)

@app.command("route-list")
def list_routes():
    """List all routes."""
    crudCLI.list_routes()

@app.command("route-update")
def update_route(
    route_id: int = typer.Argument(...),
    name: str = typer.Option(None, "--name", "-n"),
    rtype: str = typer.Option(None, "--type", "-t"),
):
    crudCLI.update_route(route_id, name, rtype)

@app.command("route-delete")
def delete_route(route_id: int = typer.Argument(...)):
    "Delete route by ID"
    crudCLI.delete_route(route_id)

######################
## Vehicle Commands ##
######################

@app.command("vehicle-add")
def add_vehicle(
    vehicle_id: int = typer.Argument(...),
    vehicle_class: str = typer.Option(..., "--class", "-c", help="Vehicle Class: Bus/Metro)"),
    manufacturer: str = typer.Option(..., "--manufacturer", "-m"),
    manufacture_year: int = typer.Option(..., "--year", "-y", min=1960, max=2026),
    vehicle_type: str = typer.Option(..., "--type", "-t", help="Standard, Articulated, etc."),
    capacity: int | None = typer.Option(None, "--capacity", "-n", min=0, max=500, help="Passenger capacity"),
):
    """Create a new vehicle record."""
    crudCLI.add_vehicle(
        vehicle_id, vehicle_class, manufacturer,
        manufacture_year, vehicle_type, capacity
    )

@app.command("vehicle-get")
def get_vehicle(
    vehicle_id: int = typer.Argument(..., help="Vehicle ID"),
):
    """Show one vehicle."""
    crudCLI.get_vehicle(vehicle_id)

@app.command("vehicle-list")
def list_vehicles():
    """List vehicles."""
    crudCLI.list_vehicles()

@app.command("vehicle-update")
def update_vehicle(
    vehicle_id: int = typer.Argument(...),
    vehicle_class: str | None = typer.Option(None, "--class", "-c"),
    manufacturer: str | None = typer.Option(None, "--manufacturer", "-m"),
    manufacture_year: int | None = typer.Option(None, "--year", "-y"),
    vehicle_type: str | None = typer.Option(None, "--type", "-t"),
    capacity: int | None = typer.Option(None, "--capacity", "-n"),
):
    """Update one or more fields on a vehicle."""
    crudCLI.update_vehicle(
        vehicle_id, vehicle_class, manufacturer,
        manufacture_year, vehicle_type, capacity
    )

@app.command("vehicle-delete")
def delete_vehicle(
    vehicle_id: int = typer.Argument(...),
):
    """Delete a vehicle by ID."""
    crudCLI.delete_vehicle(vehicle_id)

#####################
## Driver Commands ##
#####################

@app.command("driver-add")
def add_driver(
    driver_name: str = typer.Argument(...),
    driver_classification: str = typer.Option(..., "--class", "-c"),
    start_date: str | None = typer.Option(None, "--start", "-s", help="YYYY-MM-DD (optional)"),
    pay: float = typer.Option(..., "--pay", "-p", help="Hourly pay, e.g. 28.50"),
):
    """Create a new driver."""
    crudCLI.add_driver(driver_name,
                    driver_classification, start_date, pay)

@app.command("driver-get")
def get_driver(
    key: str = typer.Argument(..., help="Driver name or ID"),
    by: crudCLI.DriverKey = typer.Option(
        crudCLI.DriverKey.id,
        "--by",
        case_sensitive=False,
        help="Lookup by 'id' (default) or 'name'",
    ),
):
    """Retrieve a driver by name or ID."""
    crudCLI.get_driver(key, by)

@app.command("driver-list")
def list_driver():
    """List drivers."""
    crudCLI.list_drivers()

@app.command("driver-update")
def update_driver(
    driver_id: int = typer.Argument(...),
    driver_name: str | None = typer.Option(None),
    driver_classification: str | None = typer.Option(..., "--class", "-c"),
    start_date: str | None = typer.Option(None),
    pay: float | None = typer.Option(..., "--pay", "-p"),
):
    """Update a driver."""
    crudCLI.update_driver(driver_id, driver_name,
                       driver_classification, start_date, pay)

@app.command("driver-delete")
def delete_driver(driver_id: int = typer.Argument(...)):
    """Delete a driver."""
    crudCLI.delete_driver(driver_id)

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
    crudCLI.add_maintenance(vehicle_id, work_date, work_performed)

@app.command("maintenance-get")
def get_maintenance(
    maintenance_id: int = typer.Argument(...),
):
    """Show one maintenance record."""
    crudCLI.get_maintenance(maintenance_id)

@app.command("maintenance-list")
def list_maintenance(
    vehicle_id: int | None = typer.Option(
        None, "--vehicle", "-v", help="Filter by vehicle ID"
    ),
):
    """List maintenance records. Optionally filter by a single vehicle."""
    crudCLI.list_maintenance(vehicle_id)

@app.command("maintenance-update")
def update_maintenance(
    maintenance_id: int = typer.Argument(...),
    vehicle_id: int | None = typer.Option(None),
    work_date: str | None = typer.Option(None),
    work_performed: str | None = typer.Option(None),
):
    """Update a maintenance record."""
    crudCLI.update_maintenance(
        maintenance_id, vehicle_id, work_date, work_performed
    )

@app.command("maintenance-delete")
def delete_maintenance(
    maintenance_id: int = typer.Argument(...),
):
    """Delete a maintenance record."""
    crudCLI.delete_maintenance(maintenance_id)


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
    crudCLI.add_stop(stop_id, stop_direction,
                  street_name, cross_street,
                  latitude, longitude)

@app.command("stop-get")
def get_stop(stop_id: int = typer.Argument(...)):
    """Show one stop."""
    crudCLI.get_stop(stop_id)

@app.command("stop-list")
def list_stop(street_name: str | None = typer.Option(
        None, "--street", "-s", help="Filter by street name"
    ),):
    """List stops. Optionally filter by primary street name."""
    crudCLI.list_stops(street_name)

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
    crudCLI.update_stop(stop_id, stop_direction,
                     street_name, cross_street,
                     latitude, longitude)

@app.command("stop-delete")
def delete_stop(stop_id: int = typer.Argument(...)):
    """Delete a stop."""
    crudCLI.delete_stop(stop_id)

###################
## Trip Commands ##
###################

@app.command("trip-add")
def add_trip(
    trip_id: int = typer.Argument(...),
    route_id: int = typer.Argument(...),
    driver_id: int = typer.Argument(...),
    vehicle_id: int = typer.Argument(...),
    trip_date: str = typer.Argument(..., help="YYYY-MM-DD"),
    trip_direction: str = typer.Argument(..., help="N/S/E/W"),
):
    """Create a new trip."""
    crudCLI.add_trip(trip_id, route_id, driver_id, vehicle_id, trip_date, trip_direction)

@app.command("trip-get")
def get_trip(trip_id: int = typer.Argument(...)):
    """Show one trip by ID."""
    crudCLI.get_trip(trip_id)

@app.command("trip-list")
def list_trip(
    route_id: int | None = typer.Option(None, help="Filter by route ID"),
):
    """List trips. Optionally filtered by route."""
    crudCLI.list_trips(route_id)

@app.command("trip-update")
def update_trip(
    trip_id: int = typer.Argument(...),
    route_id: int | None = typer.Option(None),
    driver_id: int | None = typer.Option(None),
    vehicle_id: int | None = typer.Option(None),
    trip_date: str | None = typer.Option(None),
    trip_direction: str | None = typer.Option(None),
):
    """Update a trip record."""
    crudCLI.update_trip(trip_id, route_id, driver_id, vehicle_id, trip_date, trip_direction)

@app.command("trip-delete")
def delete_trip(trip_id: int = typer.Argument(...)):
    """Delete a trip by ID."""
    crudCLI.delete_trip(trip_id)

if __name__ == "__main__":
    app()
