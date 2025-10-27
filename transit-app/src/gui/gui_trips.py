import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.crud import trips as crud
from sqlalchemy.exc import OperationalError
from .utils import autosize_tree, clear_panel, valid_date

def register_gui(app):
    def reset_trip_filters():
        trip_filters = {}
        populate_trip_table()

    def load_trips():
        clear_panel(app.main_panel)

        # Filter button section
        trip_filter_frame = tk.LabelFrame(app.main_panel, text="Filter")
        trip_filter_frame.pack(pady=5, fill='x')

        fields = ["Trip ID", "Trip Date", "Route Name", "Route ID", "Driver Name", "Driver ID", "Vehicle ID",]
        for field in fields:
            tk.Button(
                trip_filter_frame,
                text=f"By {field}",
                command=lambda f=field: prompt_trip_filter(f)
            ).pack(side='left', padx=5)

        # reset filters
        tk.Button(trip_filter_frame, text="View All", command=reset_trip_filters).pack(side='left', padx=10)

        populate_trip_table()

    def prompt_trip_filter(field):
        form = tk.Toplevel(app.main_panel)
        form.title(f"Filter Trips by {field}")

        tk.Label(form, text=f"{field}:").pack(padx=10, pady=5)
        entry = tk.Entry(form)
        entry.pack(padx=10, pady=5)

        def apply():
            val = entry.get().strip()
            filters = {}

            try:
                if field == "Trip ID" and val:
                    filters["trip_id"] = int(val)
                elif field == "Route ID" and val:
                    filters["route_id"] = int(val)
                elif field == "Route Name" and val:
                    filters["route_name"] = val
                elif field == "Driver ID" and val:
                    filters["driver_id"] = int(val)
                elif field == "Driver Name" and val:
                    filters["driver_name"] = val
                elif field == "Vehicle ID" and val:
                    filters["vehicle_id"] = int(val)
                elif field == "Trip Date" and val:
                    try:
                        datetime.strptime(val, "%Y-%m-%d")  # strict validation
                        filters["trip_date"] = val
                    except ValueError:
                        messagebox.showerror("Invalid Input", "Date must be in YYYY-MM-DD format.")
                        return
                else:
                    messagebox.showinfo("No Input", "Please enter a valid value.")
                    return
                populate_trip_table(**filters)
                form.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Numeric fields must be integers.")
        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_trip_table(**filters):
        # Destroy existing tree container if it exists
        if hasattr(app, 'trip_tree_container') and app.trip_tree_container.winfo_exists():
            app.trip_tree_container.destroy()
        if hasattr(app, 'trip_button_frame') and app.trip_button_frame.winfo_exists():
            app.trip_button_frame.destroy()

        app.trip_tree_container = tk.Frame(app.main_panel)
        app.trip_tree_container.pack(fill='both', expand=True)

        tree = ttk.Treeview(
            app.trip_tree_container,
            columns=("ID", "Date", "Route Name", "Route ID", "Direction", "Driver Name", "Driver ID", "Vehicle ID"),
            show='headings'
        )

        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill='both', expand=True)

        trips = crud.list_trips(**filters)
        tree.delete(*tree.get_children())

        for trip in trips:
            tree.insert('', 'end', values=(
                trip['trip_id'],
                trip['trip_date'],
                trip['route_name'],
                trip['route_id'],
                trip['trip_direction'],
                trip['driver_name'],
                trip['driver_id'],
                trip['vehicle_id']
            ))

        autosize_tree(tree)

        app.trip_button_frame = tk.Frame(app.main_panel)
        app.trip_button_frame.pack(pady=10)

        tk.Button(app.trip_button_frame, 
                  text="Add", 
                  command=lambda: trip_add(app.main_panel)).pack(side='left', padx=5)
        tk.Button(app.trip_button_frame, 
                  text="Update", 
                  command=lambda: trip_update(tree)).pack(side='left', padx=5)
        tk.Button(app.trip_button_frame, 
                  text="Delete", 
                  command=lambda: trip_delete(tree)).pack(side='left', padx=5)

    def trip_add(tree):
        form = tk.Toplevel(app.main_panel)
        form.title("Add Trip")

        labels = ["Trip ID", "Route ID", "Driver ID", "Vehicle ID", "Trip Date (YYYY-MM-DD)", "Direction"]
        entries = []
        for i, label in enumerate(labels):
            tk.Label(form, text=label).grid(row=i, column=0)
            e = tk.Entry(form)
            e.grid(row=i, column=1)
            entries.append(e)

        def submit():
            try:
                crud.add_trip(
                    trip_id=int(entries[0].get()),
                    route_id=int(entries[1].get()),
                    driver_id=int(entries[2].get()),
                    vehicle_id=int(entries[3].get()),
                    trip_date=entries[4].get(),
                    trip_direction=entries[5].get()
                )
                form.destroy()
                load_trips()
            except OperationalError as oe:
                messagebox.showerror("Driver Conflict", f"Driver conflict, driver is already assigned to a differnt route on that day.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=len(labels), columnspan=2)

    def trip_update(tree):

        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Trip", "Please select a trip to update.")
            return

        selected_values = tree.item(selected[0])['values']
        crud_values = selected_values[:2] + selected_values[3:5] + selected_values[6:]
        trip_id, date, route_id, direction, driver_id, vehicle_id = crud_values

        form = tk.Toplevel(app.main_panel)
        form.title("Update Trip")

        #fields = ["Trip Date (YYYY-MM-DD)", "Route ID", "Direction", "Driver ID", "Vehicle ID"]
        #vals = [date, route_id, direction, driver_id, vehicle_id]

        fields = ["Route ID", "Driver ID", "Vehicle ID", "Trip Date (YYYY-MM-DD)", "Direction"]
        vals = [route_id, driver_id, vehicle_id, date, direction]
        
        entries = []
        for i, (label, val) in enumerate(zip(fields, vals)):
            tk.Label(form, text=label).grid(row=i, column=0)
            e = tk.Entry(form)
            e.insert(0, val)
            e.grid(row=i, column=1)
            entries.append(e)

        def submit():
            try:
                crud.update_trip(
                    trip_id,
                    route_id=int(entries[0].get()),
                    driver_id=int(entries[1].get()),
                    vehicle_id=int(entries[2].get()),
                    trip_date=entries[3].get(),
                    trip_direction=entries[4].get()
                )
                form.destroy()
                load_trips()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=len(fields), columnspan=2)

    def trip_delete(tree):
        selected = tree.selection()
        if not selected:
            return
        trip_id = tree.item(selected[0])['values'][0]
        try:
            crud.delete_trip(trip_id)
            load_trips()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    app.load_trips = load_trips