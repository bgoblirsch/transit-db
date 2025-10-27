import src.crud as crud
from rich.console import Console
from rich.table import Table
import typer

def register_commands(app: typer.Typer, console: Console):
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
        driver = crud.get_driver(driver_id)
        table = Table(title=f"Driver {driver['driver_name']}")
        table.add_column("Field")
        table.add_column("Value")
        for field in ["driver_id", "driver_name", "driver_classification", "start_date", "pay"]:
            table.add_row(field, str(driver[field]))
        console.print(table)


    @app.command("driver-list")
    def driver_list():
        """List all drivers."""
        drivers = crud.list_drivers()
        table = Table(title="Drivers")
        for col in ["ID", "Name", "Class", "Start Date", "Pay"]:
            table.add_column(col)
        for driver in drivers:
            table.add_row(
                str(driver["driver_id"]),
                driver["driver_name"],
                driver["driver_classification"],
                driver["start_date"].isoformat() if driver["start_date"] else "—",
                f"{driver['pay']:.2f}"
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
