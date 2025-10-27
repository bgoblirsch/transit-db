import src.crud as crud
from rich.console import Console
from rich.table import Table
import typer

def register_commands(app: typer.Typer, console: Console):
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
            console.print("Invalid time format. Use HH:MM or integer minutes.")
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