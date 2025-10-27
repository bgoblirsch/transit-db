import src.crud as crud
from rich.console import Console
from rich.table import Table
import typer

def register_commands(app: typer.Typer, console: Console):
    @app.command("stop-add")
    def stop_add(
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
    def stop_get(stop_id: int = typer.Argument(...)):
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
    def stop_list(street_name: str | None = typer.Option(
            None, "--street", "-s", help="Filter by primary street name"
        )):
        """List stops. Optionally filter by street name."""
        stops = crud.list_stops(street_name=street_name)
        table = Table(title="Stops")
        for col in ("ID", "Dir", "Street", "Cross", "Lat", "Lon"):
            table.add_column(col)
        for stop in stops:
            table.add_row(
                str(stop['stop_id']),
                stop['stop_direction'],
                stop['street_name'],
                stop['cross_street'],
                f"{stop['latitude']:.6f}" if stop['latitude'] is not None else "—",
                f"{stop['longitude']:.6f}" if stop['longitude'] is not None else "—",
            )
        console.print(table)
        if not stops:
            console.print("No stops found.")

    @app.command("stop-update")
    def stop_update(
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
    def stop_delete(stop_id: int = typer.Argument(...)):
        """Delete a stop."""
        crud.delete_stop(stop_id)
        console.print(f"Deleted stop {stop_id}")