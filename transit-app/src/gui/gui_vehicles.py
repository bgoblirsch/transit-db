import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.crud import vehicles as crud
from .utils import autosize_tree, clear_panel, valid_year
from sqlalchemy.exc import OperationalError

def register_gui(app):
    def load_vehicles():
        clear_panel(app.main_panel)
        # Filter button section
        vehicle_filter_frame = tk.LabelFrame(app.main_panel, text="Filter")
        vehicle_filter_frame.pack(pady=5, fill='x')

        # tree view 
        fields = ["ID", "Class", "Manufacturer", "Type", "Year", "Capacity"]
        for field in fields:
            tk.Button(
                vehicle_filter_frame,
                text=f"By {field}",
                command=lambda f=field: prompt_vehicle_filter(f)
            ).pack(side='left', padx=5)

        # reset filters
        tk.Button(vehicle_filter_frame, text="Reset Filters", command=populate_vehicle_table).pack(side='left', padx=10)

        populate_vehicle_table()

    def prompt_vehicle_filter(field):
        form = tk.Toplevel(app.main_panel)
        form.title(f"Filter Vehicles by {field}")

        tk.Label(form, text=f"{field}:").pack(padx=10, pady=5)
        entry = tk.Entry(form)
        entry.pack(padx=10, pady=5)

        operator_var = tk.StringVar(value='=')
        if field in ("Year", "Capacity"):
            op_frame = tk.Frame(form)
            op_frame.pack(pady=5)
            for op in ('=', '<', '>'):
                tk.Radiobutton(op_frame, text=op, variable=operator_var, value=op).pack(side='left')

        def apply():
            val = entry.get().strip()
            filters = {}
            try:
                if field == "ID" and val:
                    filters["vehicle_id"] = int(val)
                elif field == "Class" and val:
                    filters["vehicle_class"] = val
                elif field == "Manufacturer" and val:
                    filters["manufacturer"] = val
                elif field == "Type" and val:
                    filters["vehicle_type"] = val
                elif field == "Year" and val:
                    filters["manufacture_year"] = (operator_var.get(), int(val))
                elif field == "Capacity" and val:
                    filters["capacity"] = (operator_var.get(), int(val))
                else:
                    messagebox.showinfo("No Input", "Please enter a valid value.")
                    return
                populate_vehicle_table(**filters)
                form.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "ID must be an integer.")

        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_vehicle_table(**filters):
        if hasattr(app, 'vehicle_tree_container') and app.vehicle_tree_container.winfo_exists():
            app.vehicle_tree_container.destroy()
        if hasattr(app, 'vehicle_button_frame') and app.vehicle_button_frame.winfo_exists():
            app.vehicle_button_frame.destroy()

        app.vehicle_tree_container = tk.Frame(app.main_panel)
        app.vehicle_tree_container.pack(fill='both', expand=True)

        tree = ttk.Treeview(
            app.vehicle_tree_container,
            columns=("ID", "Class", "Manufacturer", "Year", "Type", "Capacity"),
            show='headings'
        )
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill='both', expand=True)

        vehicles = crud.list_vehicles(**filters)
        for vehicle in vehicles:
            tree.insert('', 'end', values=(
                vehicle['vehicle_id'],
                vehicle['vehicle_class'],
                vehicle['manufacturer'],
                vehicle['manufacture_year'],
                vehicle['vehicle_type'],
                vehicle['capacity']
            ))

        autosize_tree(tree)

        app.vehicle_button_frame = tk.Frame(app.main_panel)
        app.vehicle_button_frame.pack(pady=10)

        tk.Button(app.vehicle_button_frame, 
                  text="Add", 
                  command=lambda: vehicle_add(app.main_panel)).pack(side='left', padx=5)
        tk.Button(app.vehicle_button_frame, 
                  text="Update", 
                  command=lambda: vehicle_update(tree)).pack(side='left', padx=5)
        tk.Button(app.vehicle_button_frame, 
                  text="Delete", 
                  command=lambda: vehicle_delete(tree)).pack(side='left', padx=5)

    def vehicle_add(panel):
        form = tk.Toplevel(panel)
        form.title("Add Vehicle")

        labels = ["ID", "Class", "Manufacturer", "Year", "Type", "Capacity"]
        entries = []
        for i, label in enumerate(labels):
            tk.Label(form, text=label).grid(row=i, column=0)
            entry = tk.Entry(form)
            entry.grid(row=i, column=1)
            entries.append(entry)

        def submit():
            try:
                #year validation
                year = int(entries[3].get())
                if not valid_year(year):
                    messagebox.showerror("Invalid year", "Year format must be > 1900 and in the format YYYY")
                    return
                
                # id validation
                vehicle_id = int(entries[0].get())
                if vehicle_id < 0:
                    messagebox.showerror("Invalid ID", "ID cannot be negative.")
                    return
                if crud.vehicle_id_exists(vehicle_id):
                    messagebox.showerror("Duplicate ID", f"Vehicle ID {vehicle_id} already exists.")
                    return
                
                crud.add_vehicle(
                    vehicle_id=vehicle_id,
                    vehicle_class=entries[1].get(),
                    manufacturer=entries[2].get(),
                    year=year,
                    vtype=entries[4].get(),
                    capacity=int(entries[5].get())
                )
                form.destroy()
                load_vehicles()
            except OperationalError as oe:
                messagebox.showerror("Permission Denied", "Permission Denied. Only Admins may manage vehicles.") 
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=len(labels), columnspan=2)

    def vehicle_update(tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Vehicle", "Please select a vehicle to update.")
            return

        values = tree.item(selected[0])['values']
        vehicle_id, vclass, manufacturer, year, vtype, capacity = values

        form = tk.Toplevel(app.main_panel)
        form.title("Update Vehicle")

        fields = ["Class", "Manufacturer", "Year", "Type", "Capacity"]
        vals = [vclass, manufacturer, year, vtype, capacity]
        entries = []

        for i, (label, val) in enumerate(zip(fields, vals)):
            tk.Label(form, text=label).grid(row=i, column=0)
            e = tk.Entry(form)
            e.insert(0, val)
            e.grid(row=i, column=1)
            entries.append(e)

        def submit():
            try:
                #year validation
                year = int(entries[2].get())
                if not valid_year(year):
                    messagebox.showerror("Invalid year", "Year format must be greater than 1900 and less than 2030 and in the format YYYY")
                    return
                crud.update_vehicle(
                    vehicle_id,
                    vclass=entries[0].get(),
                    manufacturer=entries[1].get(),
                    year=int(entries[2].get()),
                    vtype=entries[3].get(),
                    capacity=int(entries[4].get())
                )
                form.destroy()
                load_vehicles()
            except OperationalError as oe:
                messagebox.showerror("Permission Denied", "Permission Denied. Only Admins may manage vehicles.") 
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=len(fields), columnspan=2)

    def vehicle_delete(tree):
        selected = tree.selection()
        if not selected:
            return
        vehicle_id = tree.item(selected[0])['values'][0]
        try:
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Vehicle ID {vehicle_id}?")
            if not confirm:
                return
            crud.delete_vehicle(vehicle_id)
            load_vehicles()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    app.load_vehicles = load_vehicles