import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.crud import routes_stops as crud
from .utils import autosize_tree, clear_panel

def register_gui(app):
    def load_route_stops():
        clear_panel(app.main_panel)

        filter_frame = tk.LabelFrame(app.main_panel, text="Filter")
        filter_frame.pack(pady=5, fill='x')

        tk.Button(filter_frame, 
                  text="By Route ID", 
                  command= lambda: prompt_route_stop_filter("Route ID")
        ).pack(side="left", padx=5)

        # reset filters
        tk.Button(filter_frame, text="Reset Filters", command=populate_route_stop_table).pack(side='left', padx=10)

        populate_route_stop_table()

    def prompt_route_stop_filter(field):
        form = tk.Toplevel(app.main_panel)
        form.title(f"Filter Route-Stops by {field}")

        tk.Label(form, text=f"{field}:").pack(padx=10, pady=5)
        entry = tk.Entry(form)
        entry.pack(padx=10, pady=5)

        def apply():
            val = entry.get().strip()
            filters = {}

            try:
                if field == "Route ID" and val:
                    filters["route_id"] = int(val)
                elif field == "Direction" and val:
                    filters["route_direction"] = val
                elif field == "Route Name" and val:
                    filters["route_name"] = val
                else:
                    messagebox.showinfo("No Input", "Please enter a valid value.")
                    return

                populate_route_stop_table(**filters)
                form.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Route ID must be an integer.")

        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_route_stop_table(**filters):
        if hasattr(app, 'route_stop_tree_container') and app.route_stop_tree_container.winfo_exists():
            app.route_stop_tree_container.destroy()
        if hasattr(app, 'route_stop_button_frame') and app.route_stop_button_frame.winfo_exists():
            app.route_stop_button_frame.destroy()

        app.route_stop_tree_container = tk.Frame(app.main_panel)
        app.route_stop_tree_container.pack(fill='both', expand=True)

        tree = ttk.Treeview(
            app.route_stop_tree_container,
            columns=("Route ID", "Route Name", "Direction", "Stop ID", "Cross Street", "Stop Order"),
            show='headings'
        )
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill='both', expand=True)

        records = crud.list_route_stop(**filters)
        for record in records:
            tree.insert('', 'end', values=(
                record['route_id'],
                record['route_name'],
                record['route_direction'],
                record['stop_id'],
                record['cross_street'],
                record["stop_order"]
            ))

        autosize_tree(tree)

        app.route_stop_button_frame = tk.Frame(app.main_panel)
        app.route_stop_button_frame.pack(pady=10)
        tk.Button(app.route_stop_button_frame, 
                  text="Add", 
                  command=lambda: route_stop_add(app.main_panel)).pack(side='left', padx=5)
        tk.Button(app.route_stop_button_frame, 
                  text="Update", 
                  command=lambda: route_stop_update(tree)).pack(side='left', padx=5)
        tk.Button(app.route_stop_button_frame, 
                  text="Delete", 
                  command=lambda: route_stop_delete(tree)).pack(side='left', padx=5)

    def route_stop_add(panel):
        form = tk.Toplevel(panel)
        form.title("Add Route-Stop Link")

        tk.Label(form, text="Route ID:").grid(row=0, column=0)
        route_entry = tk.Entry(form)
        route_entry.grid(row=0, column=1)

        tk.Label(form, text="Stop ID:").grid(row=1, column=0)
        stop_entry = tk.Entry(form)
        stop_entry.grid(row=1, column=1)

        tk.Label(form, text="Route Direction:").grid(row=2, column=0)
        direction_entry = tk.Entry(form)
        direction_entry.grid(row=2, column=1)

        tk.Label(form, text="Stop Order:").grid(row=3, column=0)
        order_entry = tk.Entry(form)
        order_entry.grid(row=3, column=1)

        def submit():
            try:
                crud.add_route_stop(
                    int(route_entry.get()),
                    int(stop_entry.get()),
                    str(direction_entry.get()),
                    int(order_entry.get())
                )
                populate_route_stop_table()
                form.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Add", command=submit).grid(row=4, columnspan=2, pady=10)

    def route_stop_update(tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a route-stop to update.")
            return

        selection = tree.item(selected[0])["values"]
        route_id = selection[0]
        old_direction = selection[2]
        old_stop_id = selection[3]
        stop_order = selection[-1]

        form = tk.Toplevel(app.main_panel)
        form.title("Update Route-Stop Link")

        tk.Label(form, text="New Stop ID:").grid(row=0, column=0)
        tk.Label(form, text="Direction").grid(row=1, column=0)
        tk.Label(form, text="Stop Order").grid(row=2, column=0)
        stop_entry = tk.Entry(form)
        stop_entry.insert(0, old_stop_id)
        stop_entry.grid(row=0, column=1)
        direction_entry = tk.Entry(form)
        direction_entry.insert(0, old_direction)
        direction_entry.grid(row=1,column=1)
        order_entry = tk.Entry(form)
        order_entry.insert(0, stop_order)
        order_entry.grid(row=2, column=1)

        def submit():
            try:
                new_stop_id = int(stop_entry.get())
                new_direction = direction_entry.get()
                new_order = int(order_entry.get())
                crud.update_route_stop(route_id, 
                                       old_stop_id, 
                                       old_direction,
                                       new_order, 
                                       new_stop_id, 
                                       new_direction)
                form.destroy()
                populate_route_stop_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=3, columnspan=2, pady=10)

    def route_stop_delete(tree):
        selected = tree.selection()
        if not selected:
            return

        selection = tree.item(selected[0])["values"]
        route_id = selection[0]
        direction = selection[2]
        stop_id = selection[3]

        try:
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to this route-stop?")
            if not confirm:
                return
            crud.delete_route_stop(route_id, stop_id, direction)
            populate_route_stop_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    app.load_route_stops = load_route_stops