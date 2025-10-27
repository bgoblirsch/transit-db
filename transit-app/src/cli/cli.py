from src.database import configure_engine
configure_engine()

import typer
from rich.console import Console

app = typer.Typer(help="Transit CRUD CLI")
console = Console()

from . import cli_drivers, cli_routes
from . import cli_routes
from . import cli_vehicles
from . import cli_maintenance
from . import cli_stops
from . import cli_trips
from . import cli_routes_stops
from . import cli_trips_stops

cli_drivers.register_commands(app, console)
cli_routes.register_commands(app, console)
cli_vehicles.register_commands(app, console)
cli_maintenance.register_commands(app, console)
cli_stops.register_commands(app, console)
cli_trips.register_commands(app, console)
cli_routes_stops.register_commands(app, console)
cli_trips_stops.register_commands(app, console)

if __name__ == "__main__":
    app()
