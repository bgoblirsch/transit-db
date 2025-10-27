import src.crud as crud
from rich.console import Console
from rich.table import Table
import typer

def register_commands(app: typer.Typer, console: Console):
    @app.command("maintenance-add")
    def maintenance_add(
        vehicle_id: int = typer.Argument(...),
        work_date: str = typer.Argument(..., help="YYYY-MM-DD"),
        work_performed: str = typer.Argument(..., help="Description"),
    ):
        """Create a maintenance record."""
        record = crud.add_maintenance(vehicle_id, work_date, work_performed)
        console.print(f"Added maintenance record {record['maintenance_id']} for vehicle {vehicle_id}")

    @app.command("maintenance-get")
    def maintenance_get(
        maintenance_id: int = typer.Argument(...),
    ):
        """Show one maintenance record."""
        record = crud.get_maintenance(maintenance_id)
        table = Table(title=f"Maintenance {maintenance_id}")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        for key, value in record.items():
            table.add_row(key, str(value))
        console.print(table)

    @app.command("maintenance-list")
    def maintenance_list(
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
        for record in records:
            table.add_row(
                str(record["maintenance_id"]),
                str(record["vehicle_id"]),
                record["work_date"].isoformat() if record["work_date"] else "—",
                record["work_performed"]
            )
        console.print(table)

    @app.command("maintenance-update")
    def maintenance_update(
        maintenance_id: int = typer.Argument(...),
        vehicle_id: int | None = typer.Option(None),
        work_date: str | None = typer.Option(None),
        work_performed: str | None = typer.Option(None),
    ):
        """Update a maintenance record."""
        crud.update_maintenance(maintenance_id, vehicle_id, work_date, work_performed)
        console.print(f"Updated maintenance record {maintenance_id}")

    @app.command("maintenance-delete")
    def maintenance_delete(
        maintenance_id: int = typer.Argument(...),
    ):
        """Delete a maintenance record."""
        crud.delete_maintenance(maintenance_id)
        console.print(f"Deleted maintenance record {maintenance_id}")