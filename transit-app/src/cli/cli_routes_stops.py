import src.crud as crud
from rich.console import Console
from rich.table import Table
import typer

def register_commands(app: typer.Typer, console: Console):
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