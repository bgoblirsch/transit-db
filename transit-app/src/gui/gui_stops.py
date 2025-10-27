import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.crud import stops as crud
from .utils import autosize_tree, clear_panel

def register_gui(app):
    def load_stops():
        clear_panel(app.main_panel)

        filter_frame = tk.LabelFrame(app.main_panel, text="Filter")
        filter_frame.pack(pady=5, fill='x')

        fields = ["Stop ID", "Direction", "Street"]
        for field in fields:
            tk.Button(
                filter_frame,
                text=f"By {field}",
                command=lambda f=field: prompt_stop_filter(f)
            ).pack(side='left', padx=5)

        # reset filters
        tk.Button(filter_frame, text="Reset Filters", command=populate_stop_table).pack(side='left', padx=10)
        populate_stop_table()

    def prompt_stop_filter(field):
        form = tk.Toplevel(app.main_panel)
        form.title(f"Filter Stops by {field}")

        tk.Label(form, text=f"{field}:").pack(padx=10, pady=5)
        entry = tk.Entry(form)
        entry.pack(padx=10, pady=5)

        def apply():
            val = entry.get().strip()
            filters = {}
            try:
                if field == "Stop ID" and val:
                    filters["stop_id"] = int(val)
                elif field == "Direction" and val:
                    filters["stop_direction"] = val
                elif field == "Street" and val:
                    filters["street_name"] = val
                else:
                    messagebox.showinfo("No Input", "Please enter a valid value.")
                    return

                populate_stop_table(**filters)
                form.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Stop ID must be an integer.")

        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_stop_table(**filters):
        if hasattr(app, 'stop_tree_container') and app.stop_tree_container.winfo_exists():
            app.stop_tree_container.destroy()
        if hasattr(app, 'stop_button_frame') and app.stop_button_frame.winfo_exists():
            app.stop_button_frame.destroy()

        app.stop_tree_container = tk.Frame(app.main_panel)
        app.stop_tree_container.pack(fill='both', expand=True)

        tree = ttk.Treeview(
            app.stop_tree_container,
            columns=("ID", "Direction", "Street", "Cross Street", "Latitude", "Longitude"),
            show='headings'
        )
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill='both', expand=True)
        stops = crud.list_stops(**filters)
        tree.delete(*tree.get_children())
        for record in stops:
            tree.insert('', 'end', values=(
                record['stop_id'],
                record['stop_direction'],
                record['street_name'],
                record['cross_street'],
                record['latitude'],
                record['longitude']
            ))

        autosize_tree(tree)
        app.stop_button_frame = tk.Frame(app.main_panel)
        app.stop_button_frame.pack(pady=10)
        tk.Button(app.stop_button_frame,
                  text="Add", 
                  command=lambda: stop_add(app.main_panel)).pack(side='left', padx=5)
        tk.Button(app.stop_button_frame, 
                  text="Update", 
                  command=lambda: stop_update(tree)).pack(side='left', padx=5)
        tk.Button(app.stop_button_frame, 
                  text="Delete",
                  command=lambda: stop_delete(tree)).pack(side='left', padx=5)

    def stop_add(tree):
        form = tk.Toplevel(app.main_panel)
        form.title("Add Stop")

        labels = ["Stop ID", "Direction", "Street", "Cross Street", "Latitude", "Longitude"]
        entries = []
        for i, label in enumerate(labels):
            tk.Label(form, text=label).grid(row=i, column=0)
            entry = tk.Entry(form)
            entry.grid(row=i, column=1)
            entries.append(entry)

        def submit():
            try:
                crud.add_stop(
                    stop_id=int(entries[0].get()),
                    stop_direction=entries[1].get(),
                    street_name=entries[2].get(),
                    cross_street=entries[3].get(),
                    latitude=float(entries[4].get()) if entries[4].get() else None,
                    longitude=float(entries[5].get()) if entries[5].get() else None
                )
                load_stops()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=len(labels), columnspan=2)

    def stop_update(tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Stop", "Please select a stop to update.")
            return

        values = tree.item(selected[0])['values']
        stop_id, direction, street, cross, lat, lon = values

        form = tk.Toplevel(app.main_panel)
        form.title("Update Stop")

        fields = ["Direction", "Street", "Cross Street", "Latitude", "Longitude"]
        vals = [direction, street, cross, lat, lon]
        entries = []

        for i, (label, val) in enumerate(zip(fields, vals)):
            tk.Label(form, text=label).grid(row=i, column=0)
            entry = tk.Entry(form)
            entry.insert(0, val)
            entry.grid(row=i, column=1)
            entries.append(entry)

        def submit():
            try:
                crud.update_stop(
                    stop_id,
                    stop_direction=entries[0].get(),
                    street_name=entries[1].get(),
                    cross_street=entries[2].get(),
                    latitude=float(entries[3].get()) if entries[3].get() else None,
                    longitude=float(entries[4].get()) if entries[4].get() else None
                )
                form.destroy()
                load_stops()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=len(fields), columnspan=2)

    def stop_delete(tree):
        selected = tree.selection()
        if not selected:
            return
        stop_id = tree.item(selected[0])['values'][0]
        try:
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this stop?")
            if not confirm:
                return
            crud.delete_stop(stop_id)
            load_stops()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    app.load_stops = load_stops