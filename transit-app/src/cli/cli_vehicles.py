import src.crud as crud
from rich.console import Console
from rich.table import Table
import typer

def register_commands(app: typer.Typer, console: Console):
    @app.command("vehicle-add")
    def vehicle_add(
        vehicle_id: int = typer.Argument(...),
        vehicle_class: str = typer.Option(..., "--class", "-c", help="Vehicle Class: Bus/Metro"),
        manufacturer: str = typer.Option(..., "--manufacturer", "-m"),
        manufacture_year: int = typer.Option(..., "--year", "-y", min=1960, max=2026),
        vehicle_type: str = typer.Option(..., "--type", "-t", help="Standard, Articulated, etc."),
        capacity: int | None = typer.Option(None, "--capacity", "-n", min=0, max=500, help="Passenger capacity"),
    ):
        result = crud.add_vehicle(vehicle_id, vehicle_class, manufacturer, manufacture_year, vehicle_type, capacity)
        console.print(f"Added vehicle {result['vehicle_id']}")


    @app.command("vehicle-get")
    def vehicle_get(vehicle_id: int = typer.Argument(..., help="Vehicle ID")):
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
        vehicles = crud.list_vehicles(vehicle_id, vehicle_class, manufacturer, manufacture_year, vehicle_type, capacity)
        table = Table(title="Vehicles")
        for col in ["ID", "Class", "Manufacturer", "Year", "Type", "Capacity"]:
            table.add_column(col)
        for vehicle in vehicles:
            table.add_row(
                str(vehicle["vehicle_id"]),
                vehicle["vehicle_class"],
                vehicle["manufacturer"],
                str(vehicle["manufacture_year"]),
                vehicle["vehicle_type"],
                str(vehicle["capacity"]) if vehicle["capacity"] is not None else "—"
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
        result = crud.update_vehicle(vehicle_id, vehicle_class, manufacturer, manufacture_year, vehicle_type, capacity)
        console.print(f"Updated vehicle {result['vehicle_id']}")


    @app.command("vehicle-delete")
    def vehicle_delete(vehicle_id: int = typer.Argument(..., help="Vehicle ID")):
        crud.delete_vehicle(vehicle_id)
        console.print(f"Deleted vehicle {vehicle_id}")
