import tkinter as tk
from tkinter import ttk, messagebox
from src.crud import trips_stops as crud
from src.utils.utils import time24_to_min
from .utils import autosize_tree, clear_panel

def register_gui(app):
    def load_trip_stops():
        clear_panel(app.main_panel)

        trip_stop_filter_frame = tk.LabelFrame(app.main_panel, text="Filter")
        trip_stop_filter_frame.pack(pady=5, fill='x')

        fields = ["Route Name", "Direction"]
        for field in fields:
            tk.Button(
                trip_stop_filter_frame,
                text=f"By {field}",
                command=lambda f=field: prompt_trip_stop_filter(f)
            ).pack(side='left', padx=5)

        tk.Button(trip_stop_filter_frame, text="Reset Filters", command=populate_trip_stop_table).pack(side='left', padx=10)

        populate_trip_stop_table()

    def prompt_trip_stop_filter(field):
        form = tk.Toplevel(app.main_panel)
        form.title(f"Filter Trip-Stops by {field}")

        tk.Label(form, text=f"{field}:").pack(padx=10, pady=5)
        entry = tk.Entry(form)
        entry.pack(padx=10, pady=5)

        def apply():
            val = entry.get().strip()
            filters = {}
            if field == "Route Name" and val:
                filters["route_name"] = val
            elif field == "Direction" and val:
                filters["trip_direction"] = val
            else:
                messagebox.showinfo("No Input", "Please enter a valid value.")
                return

            populate_trip_stop_table(**filters)
            form.destroy()

        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_trip_stop_table(**filters):
        if hasattr(app, 'trip_stop_tree_container') and app.trip_stop_tree_container.winfo_exists():
            app.trip_stop_tree_container.destroy()

        if hasattr(app, 'trip_stop_button_frame') and app.trip_stop_button_frame.winfo_exists():
            app.trip_stop_button_frame.destroy()

        app.trip_stop_tree_container = tk.Frame(app.main_panel)
        app.trip_stop_tree_container.pack(fill='both', expand=True)

        tree = ttk.Treeview(
            app.trip_stop_tree_container,
            columns=("Trip ID", "Route", "Direction", "Stop ID", "Street", "Cross Street", "Arrival Time"),
            show='headings'
        )
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill='both', expand=True)

        rows = crud.list_trip_stop(**filters)
        for row in rows:
            tree.insert('', 'end', values=(
                row['trip_id'],
                row['route_name'],
                row['trip_direction'],
                row['stop_id'],
                row['street_name'],
                row['cross_street'],
                row['arrival_hhmm']
            ))

        autosize_tree(tree)

        app.trip_stop_button_frame = tk.Frame(app.main_panel)
        app.trip_stop_button_frame.pack(pady=10)
        tk.Button(app.trip_stop_button_frame,
                  text="Add", 
                  command=lambda: trip_stop_add(app.main_panel)).pack(side='left', padx=5)
        tk.Button(app.trip_stop_button_frame, 
                  text="Update", 
                  command=lambda: trip_stop_update(tree)).pack(side='left', padx=5)
        tk.Button(app.trip_stop_button_frame, 
                  text="Delete",
                  command=lambda: trip_stop_delete(tree)).pack(side='left', padx=5)
    
    def trip_stop_add(tree):
        form = tk.Toplevel(app.main_panel)
        form.title("Add Trip-Stop")

        labels = ["Trip ID", "Stop ID", "24 Hr Time (HH:MM)"]
        entries = []
        for i, label in enumerate(labels):
            tk.Label(form, text=label).grid(row=i, column=0)
            entry = tk.Entry(form)
            entry.grid(row=i, column=1)
            entries.append(entry)

        def submit():
            try:
                crud.add_trip_stop(
                    trip_id=int(entries[0].get()),
                    stop_id=int(entries[1].get()),
                    time_str=entries[2].get()
                )
                load_trip_stops()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=len(labels), columnspan=2)

    def trip_stop_update(tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Trip-Stop", "Please select a timetable entry to update.")
            return

        values = tree.item(selected[0])['values']
        trip_id = values[0] 
        stop_id = values[3]
        time_str = values[-1]

        form = tk.Toplevel(app.main_panel)
        form.title("Update Stop")

        fields = ["Trip ID", "Stop ID", "24 Hr Time (HH:MM)"]
        vals = [trip_id, stop_id, time_str]
        entries = []

        for i, (label, val) in enumerate(zip(fields, vals)):
            tk.Label(form, text=label).grid(row=i, column=0)
            entry = tk.Entry(form)
            entry.insert(0, val)
            entry.grid(row=i, column=1)
            entries.append(entry)

        def submit():
            try:
                time_int = time24_to_min(entries[2].get())
                crud.update_trip_stop(
                    trip_id=entries[0].get(),
                    stop_id=entries[1].get(),
                    arrival_time=time_int
                )
                form.destroy()
                load_trip_stops()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=len(fields), columnspan=2)

    def trip_stop_delete(tree):
        selected = tree.selection()
        if not selected:
            return
        trip_id = tree.item(selected[0])['values'][0]
        stop_id = tree.item(selected[0])['values'][3]
        try:
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this trip-stop?")
            if not confirm:
                return
            crud.delete_trip_stop(trip_id, stop_id)
            load_trip_stops()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    app.load_trip_stops = load_trip_stops