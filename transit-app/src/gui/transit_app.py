import tkinter as tk
from tkinter import messagebox
from src.database import get_engine, configure_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

from src.gui import gui_drivers
from src.gui import gui_vehicles
from src.gui import gui_maintenance
from src.gui import gui_routes
from src.gui import gui_trips
from src.gui import gui_stops
from src.gui import gui_routes_stops
from src.gui import gui_trips_stops
from src.gui import gui_analysis


class TransitApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.DEV_MODE = True
        self.title("Transit Management System")
        self.geometry("1400x800")

        # cumulative filter variables
        self.vehicle_filters = {}
        self.stop_filters = {}
        self.trip_filters = {}
        self.route_stop_filters = {}
        self.trip_stop_filters = {}

        self.user_info = None
        self.user_role = None

        gui_drivers.register_gui(self)
        gui_vehicles.register_gui(self)
        gui_routes.register_gui(self)
        gui_maintenance.register_gui(self)
        gui_routes.register_gui(self)
        gui_trips.register_gui(self)
        gui_stops.register_gui(self)
        gui_routes_stops.register_gui(self)
        gui_trips_stops.register_gui(self)
        gui_analysis.register_gui(self)

        if self.DEV_MODE:
            # Simulate successful login
            from src.database import get_engine
            engine = get_engine("admin", "admin")  # Use admin user credentials
            configure_engine(engine=engine)
            self.user_role = "admin"
            self.build_main_ui()
        else:
            self.login_screen()

    def login_screen(self):
        self.login_frame = tk.Frame(self)
        self.login_frame.pack(pady=150)

        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0)
        username_entry = tk.Entry(self.login_frame)
        username_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0)
        password_entry = tk.Entry(self.login_frame, show='*')
        password_entry.grid(row=1, column=1)

        def try_login():
            try:
                engine = get_engine(username_entry.get(), password_entry.get())
                configure_engine(engine=engine)

                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    
                self.user_role = username_entry.get()
                self.login_frame.destroy()
                self.build_main_ui()
            except OperationalError as oe:
                messagebox.showerror("Database Error", "Could not connect to the database. Invalid credentials or the database may be offline.")
            except Exception as e:
                messagebox.showerror("Login Failed", f"Connection failed:\n{e}")

        tk.Button(self.login_frame, text="Login", command=try_login).grid(row=2, columnspan=2)

    def build_main_ui(self):
        self.sidebar = tk.Frame(self, width=200, bg='#808080')
        self.sidebar.pack(side='left', fill='y')

        self.main_panel = tk.Frame(self)
        self.main_panel.pack(side='right', expand=True, fill='both')

        buttons = [
            ("Drivers", self.load_drivers),
            ("Routes", self.load_routes),
            ("Vehicles", self.load_vehicles),
            ("Maintenance", self.load_maintenance),
            ("Stops", self.load_stops),
            ("Trips", self.load_trips),
            ("Route-Stops", self.load_route_stops),
            ("Timetables", self.load_trip_stops),
            ("Analysis", self.load_analysis),
        ]

        if self.user_role == "maintenance":
            allowed_labels = {"Maintenance", "Vehicles"}
        else:
            allowed_labels = {label for label, _ in buttons}

        for label, command in buttons:
            if label in allowed_labels:
                btn = tk.Button(
                    self.sidebar, 
                    text=label, 
                    width=20, 
                    height=2, 
                    relief='flat',
                    bg='#5c5c5c', 
                    fg='#292828',
                    activebackground='#5c5c5c',
                    activeforeground='#292828',
                    command=command
                )
                btn.pack(pady=8, padx=10, fill='x')

        self.tree = None
        self.button_frame = None

