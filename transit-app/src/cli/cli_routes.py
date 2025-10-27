import src.crud as crud
from rich.console import Console
from rich.table import Table
import typer

def register_commands(app: typer.Typer, console: Console):
    @app.command("route-add")
    def route_add(
        route_id: int = typer.Argument(...),
        name: str = typer.Argument(...),
        route_type: str = typer.Option(..., "--type", "-t"),
    ):
        route = crud.add_route(route_id, name, route_type)
        console.print(f"Added route: {route['route_name']} (ID: {route['route_id']})")

    @app.command("route-get")    
    def route_get(route_name: str):
        route = crud.get_route(route_name)
        table = Table(title=f"Route {route['route_name']}")
        for key, value in route.items():
            table.add_row(key, str(value))
        console.print(table)

    @app.command("route-list")
    def route_list():
        routes = crud.list_routes()
        table = Table(title="Routes", show_lines=True)
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Type")
        for route in routes:
            table.add_row(str(route["route_id"]), route["route_name"], route["route_type"])
        console.print(table)

    @app.command("route-update")
    def oute_update(
        route_id: int = typer.Argument(...),
        name: str = typer.Option(None, "--name", "-n"),
        rtype: str = typer.Option(None, "--type", "-t"),
    ):
        updated = crud.update_route(route_id, route_name=name, route_type=rtype)
        console.print(f"Updated route {updated['route_id']}")

    @app.command("route-delete")
    def route_delete(route_id: int = typer.Argument(...)):
        crud.delete_route(route_id)
        console.print(f"Deleted route {route_id}")