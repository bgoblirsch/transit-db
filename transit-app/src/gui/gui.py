import logging
from src.gui.transit_app import TransitApp

from src.gui import gui_drivers
from src.gui import gui_vehicles
from src.gui import gui_routes
from src.gui import gui_trips
from src.gui import gui_stops
from src.gui import gui_routes_stops
from src.gui import gui_trips_stops
from src.gui import gui_maintenance
from src.gui import gui_analysis

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    app = TransitApp()

    gui_drivers.register_gui(app)
    gui_vehicles.register_gui(app)
    gui_routes.register_gui(app)
    gui_trips.register_gui(app)
    gui_stops.register_gui(app)
    gui_maintenance.register_gui(app)
    gui_routes_stops.register_gui(app)
    gui_trips_stops.register_gui(app)
    gui_analysis.register_gui(app)

    app.mainloop()