import tkinter as tk
from tkinter import ttk, messagebox
from src.utils import analysis
from .utils import clear_panel

def register_gui(app):
    def load_analysis():
        clear_panel(app.main_panel)

        # find all shared routes
        app.shared_all_frame = tk.LabelFrame(app.main_panel, text="Find shared stops among all Routes")
        app.shared_all_frame.pack(pady=5, fill='x')
        tk.Button(
            app.shared_all_frame,
            text="Search",
            command=run_stops_shared_by_all_routes
        ).pack(side='left', padx=10)


        # find shared stops between two routes 
        app.analysis_filter_frame = tk.LabelFrame(app.main_panel, text="Find shared routes among two routes")
        app.analysis_filter_frame.pack(pady=5, fill='x')
        # Route A input
        route_a_frame = tk.Frame(app.analysis_filter_frame)
        route_a_frame.pack(side='left', padx=5)
        tk.Label(route_a_frame, text="Route ID A:").pack(side='top')
        app.route_a_entry = tk.Entry(route_a_frame, width=8, bg='white', fg='black', insertbackground='black')
        app.route_a_entry.pack(side='top')
        app.route_a_entry.update_idletasks()
        # Route B input
        route_b_frame = tk.Frame(app.analysis_filter_frame)
        route_b_frame.pack(side='left', padx=5)
        tk.Label(route_b_frame, text="Route ID B:").pack(side='top')
        app.route_b_entry = tk.Entry(route_b_frame, width=8, bg='white', fg='black', insertbackground='black')
        app.route_b_entry.pack(side='top')
        app.route_b_entry.update_idletasks()
        # Submit button
        tk.Button(
            app.analysis_filter_frame,
            text="Find Shared Stops",
            command=run_shared_stops_analysis
        ).pack(side='left', padx=10)


        # find drivers with no assignment on a given day
        app.driver_avail_frame = tk.LabelFrame(app.main_panel, text="Driver Availability by Date")
        app.driver_avail_frame.pack(pady=5, fill='x')
        app.route_b_entry.update_idletasks()
        tk.Label(app.driver_avail_frame, text="Trip Date (YYYY-MM-DD):").pack(side='left', padx=5)
        app.driver_avail_entry = tk.Entry(app.driver_avail_frame, width=12)
        app.driver_avail_entry.pack(side='left', padx=5)
        tk.Button(
            app.driver_avail_frame,
            text="Find Available Drivers",
            command=run_driver_availability_analysis
        ).pack(side='left', padx=10)

        # calcculate vehicle load - total trips by each vehicle
        app.vehicle_usage_frame = tk.LabelFrame(app.main_panel, text="Determine Vehicle Utilization - Number of Trips by Vehicle")
        app.vehicle_usage_frame.pack(pady=5, fill='x')
        tk.Button(
            app.vehicle_usage_frame,
            text="Calculate",
            command=run_vehicle_trip_counts
        ).pack(side='left', padx=10)

        # rank drivers by trip count
        app.driver_rank_frame = tk.LabelFrame(app.main_panel, text="Driver Ranking")
        app.driver_rank_frame.pack(pady=5, fill='x')
        tk.Button(
            app.driver_rank_frame,
            text="Rank Drivers by Trip Count",
            command=run_driver_rank_analysis
        ).pack(side='left', padx=10)

        # average time between maintenance
        app.maint_avg_frame = tk.LabelFrame(app.main_panel, text="Vehicle Maintenance Interval Analysis - Average Days Between Maintenance")
        app.maint_avg_frame.pack(pady=5, fill='x')
        tk.Button(
            app.maint_avg_frame,
            text="Calculate",
            command=run_avg_maintenance_gap
        ).pack(side='left', padx=10)

        app.analysis_tree_container = tk.Frame(app.main_panel)
        app.analysis_tree_container.pack(fill='both', expand=True)

    def run_shared_stops_analysis():
        route_a = app.route_a_entry.get().strip()
        route_b = app.route_b_entry.get().strip()

        if not (route_a.isdigit() and route_b.isdigit()):
            messagebox.showerror("Invalid Input", "Please enter valid route IDs.")
            return

        route_a = int(route_a)
        route_b = int(route_b)

        results = analysis.get_shared_stops(route_a, route_b)

        # Destroy previous tree if needed
        if getattr(app, 'tree', None):
            app.tree.destroy()

        app.tree = ttk.Treeview(
            app.analysis_tree_container,
            columns=("Stop ID", "Street", "Cross Street", "Lat", "Lon"),
            show='headings'
        )
        for col in app.tree["columns"]:
            app.tree.heading(col, text=col)
        app.tree.pack(fill='both', expand=True)

        for row in results:
            app.tree.insert('', 'end', values=(
                row["stop_id"],
                row["street_name"],
                row["cross_street"],
                row["latitude"],
                row["longitude"]
            ))

    def run_stops_shared_by_all_routes():
        results = analysis.get_all_shared_stops()

        if getattr(app, 'tree', None):
            app.tree.destroy()

        app.tree = ttk.Treeview(
            app.analysis_tree_container,
            columns=("Stop ID", "Street", "Cross Street", "Lat", "Lon"),
            show='headings'
        )
        for col in app.tree["columns"]:
            app.tree.heading(col, text=col)
        app.tree.pack(fill='both', expand=True)

        for row in results:
            app.tree.insert('', 'end', values=(
                row["stop_id"],
                row["street_name"],
                row["cross_street"],
                row["latitude"],
                row["longitude"]
            ))

    def run_driver_availability_analysis():
        date = app.driver_avail_entry.get().strip()
        if not date:
            messagebox.showerror("Missing Date", "Please enter a valid trip date (YYYY-MM-DD).")
            return
        try:
            from datetime import datetime
            datetime.strptime(date, "%Y-%m-%d")  # basic format validation
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format.")
            return
        results = analysis.get_available_drivers(date)
        if getattr(app, 'tree', None):
            app.tree.destroy()
        app.tree = ttk.Treeview(
            app.analysis_tree_container,
            columns=("Driver ID", "Name", "Classification", "Pay"),
            show='headings'
        )
        for col in app.tree["columns"]:
            app.tree.heading(col, text=col)
        app.tree.pack(fill='both', expand=True)
        for row in results:
            app.tree.insert('', 'end', values=(
                row["driver_id"],
                row["driver_name"],
                row["driver_classification"],
                row["pay"]
            ))

    def run_vehicle_trip_counts():
        results = analysis.get_vehicle_trip_counts()

        if getattr(app, 'tree', None):
            app.tree.destroy()

        app.tree = ttk.Treeview(
            app.analysis_tree_container,
            columns=("Vehicle ID", "Trip Count", "Class", "Manufacturer", "Year", "Type", "Capacity"),
            show='headings'
        )
        for col in app.tree["columns"]:
            app.tree.heading(col, text=col)
        app.tree.pack(fill='both', expand=True)

        for row in results:
            app.tree.insert('', 'end', values=(
                row["vehicle_id"],
                row["trip_count"],
                row["vehicle_class"],
                row["manufacturer"],
                row["manufacture_year"],
                row["vehicle_type"],
                row["capacity"]
            ))

        column_widths = {
            "Vehicle ID": 60,
            "Class": 80,
            "Manufacturer": 120,
            "Year": 60,
            "Type": 100,
            "Capacity": 80,
            "Trip Count": 80
        }
        for col in app.tree["columns"]:
            app.tree.column(col, width=column_widths.get(col, 100), anchor='center')

    def run_driver_rank_analysis():
        results = analysis.get_driver_trip_ranks()
        if getattr(app, 'tree', None):
            app.tree.destroy()
        app.tree = ttk.Treeview(
            app.analysis_tree_container,
            columns=("Driver ID", "Name", "Trip Count", "Rank"),
            show='headings'
        )
        for col in app.tree["columns"]:
            app.tree.heading(col, text=col)
        app.tree.pack(fill='both', expand=True)
        for row in results:
            app.tree.insert('', 'end', values=(
                row["driver_id"],
                row["driver_name"],
                row["trip_count"],
                row["trip_rank"]
            ))

    def run_avg_maintenance_gap():
        results = analysis.get_avg_days_between_maintenance()

        if getattr(app, 'tree', None):
            app.tree.destroy()

        app.tree = ttk.Treeview(
            app.analysis_tree_container,
            columns=("Vehicle ID", "Avg Days Between Maintenance"),
            show='headings'
        )
        for col in app.tree["columns"]:
            app.tree.heading(col, text=col)
        app.tree.pack(fill='both', expand=True)

        for row in results:
            app.tree.insert('', 'end', values=(
                row["vehicle_id"],
                row["avg_days_between"]
            ))

    app.load_analysis = load_analysis