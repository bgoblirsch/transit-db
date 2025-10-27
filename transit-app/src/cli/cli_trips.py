import src.crud as crud
from rich.console import Console
from rich.table import Table
import typer

def register_commands(app: typer.Typer, console: Console):
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
        console.print(f"Trip {trip['trip_id']} added.")


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