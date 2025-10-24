import logging

from sqlalchemy import text
import crud
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, messagebox
from sqlalchemy.exc import OperationalError
from database import get_engine
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def valid_date(value: str) -> bool:
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.year > 1900
    except ValueError:
        return False
    
def valid_year(value: int) -> bool:
    return value > 1900 and value < 2030

class TransitApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.DEV_MODE = False
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

        if self.DEV_MODE:
            # Simulate successful login
            from database import get_engine
            engine = get_engine("admin", "admin")  # Use admin user credentials
            crud.configure_engine(engine)
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
                crud.configure_engine(engine)

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

    def autosize_tree(self):
        tree_font = tkFont.Font()

        for col_index, col in enumerate(self.tree["columns"]):
            max_width = tree_font.measure(col)
            for row in self.tree.get_children():
                val = self.tree.item(row)['values'][col_index]
                max_width = max(max_width, tree_font.measure(str(val)))
            self.tree.column(col, width=max_width + 20)

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

    def clear_main_panel(self):
        for widget in self.main_panel.winfo_children():
            widget.destroy()


    ################
    ## Driver GUI ##
    ################
    def load_drivers(self):
        self.clear_main_panel()
        self.tree = ttk.Treeview(self.main_panel, columns=("ID", "Name", "Class", "Start", "Pay"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        for driver in crud.list_drivers():
            self.tree.insert('', 'end', values=(
                driver['driver_id'], 
                driver['driver_name'], 
                driver['driver_classification'], 
                driver['start_date'].isoformat() if driver['start_date'] else "—",
                f"{driver['pay']:.2f}"
            ))

        self.autosize_tree()

        self.button_frame = tk.Frame(self.main_panel)
        self.button_frame.pack(pady=10)

        tk.Button(self.button_frame, text="Add", command=self.add_driver).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Update", command=self.update_driver).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Delete", command=self.delete_driver).pack(side='left', padx=5)

    def add_driver(self):
        form = tk.Toplevel(self)
        form.title("Add Driver")

        tk.Label(form, text="Name").grid(row=0, column=0)
        name_entry = tk.Entry(form)
        name_entry.grid(row=0, column=1)

        tk.Label(form, text="Classification").grid(row=1, column=0)
        class_entry = tk.Entry(form)
        class_entry.grid(row=1, column=1)

        tk.Label(form, text="Start Date (YYYY-MM-DD)").grid(row=2, column=0)
        date_entry = tk.Entry(form)
        date_entry.grid(row=2, column=1)

        tk.Label(form, text="Pay").grid(row=3, column=0)
        pay_entry = tk.Entry(form)
        pay_entry.grid(row=3, column=1)

        def submit():
            try:
                start_date = date_entry.get()
                if start_date and not valid_date(start_date):
                    messagebox.showerror("Invalid date", "Date format must be a valid date and in the format YYYY-MM-DD")
                    return
                crud.add_driver(
                    driver_name=name_entry.get(),
                    driver_classification=class_entry.get(),
                    start_date=start_date,
                    pay=float(pay_entry.get())
                )
                form.destroy()
                self.load_drivers()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=4, columnspan=2)

    def update_driver(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Driver", "Please select a driver to update.")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        driver_id, name, classification, start_date, pay = values

        form = tk.Toplevel(self)
        form.title("Update Driver")

        tk.Label(form, text="Name").grid(row=0, column=0)
        name_entry = tk.Entry(form)
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=1)

        tk.Label(form, text="Classification").grid(row=1, column=0)
        class_entry = tk.Entry(form)
        class_entry.insert(0, classification)
        class_entry.grid(row=1, column=1)

        tk.Label(form, text="Start Date (YYYY-MM-DD)").grid(row=2, column=0)
        date_entry = tk.Entry(form)
        date_entry.insert(0, start_date)
        date_entry.grid(row=2, column=1)

        tk.Label(form, text="Pay").grid(row=3, column=0)
        pay_entry = tk.Entry(form)
        pay_entry.insert(0, pay)
        pay_entry.grid(row=3, column=1)

        def submit():
            try:
                start_date = date_entry.get()
                if start_date and not valid_date(start_date):
                    messagebox.showerror("Invalid date", "Date format must be a valid date and in the format YYYY-MM-DD")
                    return
                crud.update_driver(
                    driver_id,
                    driver_name=name_entry.get(),
                    driver_classification=class_entry.get(),
                    start_date=date_entry.get(),
                    pay=float(pay_entry.get())
                )
                form.destroy()
                self.load_drivers()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=4, columnspan=2)


    def delete_driver(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            driver_id = item['values'][0]
            try:
                crud.delete_driver(driver_id)
                self.load_drivers()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    ###############
    ## Route GUI ##
    ###############
    def load_routes(self):
        self.clear_main_panel()
        self.tree = ttk.Treeview(self.main_panel, columns=("ID", "Name", "Type"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        for route in crud.list_routes():
            self.tree.insert('', 'end', values=(route['route_id'], route['route_name'], route['route_type']))

        self.autosize_tree()


        self.button_frame = tk.Frame(self.main_panel)
        self.button_frame.pack(pady=10)

        tk.Button(self.button_frame, text="Add", command=self.add_route).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Update", command=self.update_route).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Delete", command=self.delete_route).pack(side='left', padx=5)

    def add_route(self):
        form = tk.Toplevel(self)
        form.title("Add Route")

        tk.Label(form, text="ID").grid(row=0, column=0)
        id_entry = tk.Entry(form)
        id_entry.grid(row=0, column=1)

        tk.Label(form, text="Name").grid(row=1, column=0)
        name_entry = tk.Entry(form)
        name_entry.grid(row=1, column=1)

        tk.Label(form, text="Type").grid(row=2, column=0)
        type_dropdown = ttk.Combobox(form, values=["bus", "metro"], state="readonly")
        type_dropdown.grid(row=2, column=1)

        def submit():
            try:
                route_id = int(id_entry.get())
                if crud.route_id_exists(route_id):
                    messagebox.showerror("Duplicate ID", f"Route ID {route_id} already exists.")
                    return

                route_name = name_entry.get()
                if crud.route_name_exists(route_name):
                    messagebox.showerror("Duplicate Name", f"Route name '{route_name}' already exists.")
                    return
                
                route_type = type_dropdown.get()
                if not route_type:
                    messagebox.showerror("Missing Type", "Please select a route type.")
                    return
                
                crud.add_route(route_id, route_name, route_type)
                form.destroy()
                self.load_routes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=3, columnspan=2)

    def update_route(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Route", "Please select a route to update.")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        route_id, name, route_type = values

        form = tk.Toplevel(self)
        form.title("Update Route")

        tk.Label(form, text="Name").grid(row=0, column=0)
        name_entry = tk.Entry(form)
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=1)

        tk.Label(form, text="Type").grid(row=1, column=0)
        type_dropdown = ttk.Combobox(form, values=["bus", "metro"], state="readonly")
        type_dropdown.insert(0, route_type)
        type_dropdown.grid(row=1, column=1)

        def submit():
            try:
                new_name = name_entry.get()
                new_type = type_dropdown.get()

                if not new_type:
                    messagebox.showerror("Missing Type", "Please select a route type.")
                    return

                try:
                    existing = crud.get_route(new_name)  # returns dict if found
                    if existing["route_id"] != route_id:
                        messagebox.showerror("Duplicate Name", f"Route name '{new_name}' already exists.")
                        return
                except Exception:
                    pass  # no conflict, name is free to use
                
                crud.update_route(
                    route_id,
                    route_name=new_name,
                    route_type=new_type
                )
                form.destroy()
                self.load_routes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=2, columnspan=2)

    def delete_route(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            route_id = item['values'][0]
            try:
                confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Route ID {route_id}?")
                if not confirm:
                    return
                crud.delete_route(route_id)
                self.load_routes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    #################
    ## Vehicle GUI ##
    #################
    def reset_vehicle_filters(self):
        self.vehicle_filters = {}
        self.populate_vehicle_table()

    def load_vehicles(self):
        self.clear_main_panel()
        # Filter button section
        self.vehicle_filter_frame = tk.LabelFrame(self.main_panel, text="Filter")
        self.vehicle_filter_frame.pack(pady=5, fill='x')

        # tree view 
        fields = ["ID", "Class", "Manufacturer", "Type", "Year", "Capacity"]
        for field in fields:
            tk.Button(
                self.vehicle_filter_frame,
                text=f"By {field}",
                command=lambda f=field: self.prompt_vehicle_filter(f)
            ).pack(side='left', padx=5)

        # reset filters
        tk.Button(self.vehicle_filter_frame, text="Show All", command=self.reset_vehicle_filters).pack(side='left', padx=10)

        #self.populate_vehicle_table()
        self.populate_vehicle_table()

    def prompt_vehicle_filter(self, field):
        form = tk.Toplevel(self)
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
                    self.vehicle_filters["vehicle_id"] = int(val)
                elif field == "Class" and val:
                    self.vehicle_filters["vehicle_class"] = val
                elif field == "Manufacturer" and val:
                    self.vehicle_filters["manufacturer"] = val
                elif field == "Type" and val:
                    self.vehicle_filters["vehicle_type"] = val
                elif field == "Year" and val:
                    self.vehicle_filters["manufacture_year"] = (operator_var.get(), int(val))
                elif field == "Capacity" and val:
                    self.vehicle_filters["capacity"] = (operator_var.get(), int(val))
                else:
                    messagebox.showinfo("No Input", "Please enter a valid value.")
                    return
                self.populate_vehicle_table(**self.vehicle_filters)
                form.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "ID must be an integer.")

        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_vehicle_table(self, **filters):
        if getattr(self, 'tree', None):
            self.tree.destroy()
        if hasattr(self, 'vehicle_tree_container') and self.vehicle_tree_container.winfo_exists():
            self.vehicle_tree_container.destroy()
        if getattr(self, 'button_frame', None):
            self.button_frame.destroy()

        self.vehicle_tree_container = tk.Frame(self.main_panel)
        self.vehicle_tree_container.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(
            self.vehicle_tree_container,
            columns=("ID", "Class", "Manufacturer", "Year", "Type", "Capacity"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        vehicles = crud.list_vehicles(**filters)
        for vehicle in vehicles:
            self.tree.insert('', 'end', values=(
                vehicle['vehicle_id'],
                vehicle['vehicle_class'],
                vehicle['manufacturer'],
                vehicle['manufacture_year'],
                vehicle['vehicle_type'],
                vehicle['capacity']
            ))

        self.autosize_tree()

        self.button_frame = tk.Frame(self.main_panel)
        self.button_frame.pack(pady=10)

        tk.Button(self.button_frame, text="Add", command=self.add_vehicle).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Update", command=self.update_vehicle).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Delete", command=self.delete_vehicle).pack(side='left', padx=5)

    def add_vehicle(self):
        form = tk.Toplevel(self)
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
                self.load_vehicles()
            except OperationalError as oe:
                messagebox.showerror("Permission Denied", "Permission Denied. Only Admins may manage vehicles.") 
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=len(labels), columnspan=2)

    def update_vehicle(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Vehicle", "Please select a vehicle to update.")
            return

        values = self.tree.item(selected[0])['values']
        vehicle_id, vclass, manufacturer, year, vtype, capacity = values

        form = tk.Toplevel(self)
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
                self.load_vehicles()
            except OperationalError as oe:
                messagebox.showerror("Permission Denied", "Permission Denied. Only Admins may manage vehicles.") 
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=len(fields), columnspan=2)

    def delete_vehicle(self):
        selected = self.tree.selection()
        if not selected:
            return
        vehicle_id = self.tree.item(selected[0])['values'][0]
        try:
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Vehicle ID {vehicle_id}?")
            if not confirm:
                return
            crud.delete_vehicle(vehicle_id)
            self.load_vehicles()
        except Exception as e:
            messagebox.showerror("Error", str(e))


    #####################
    ## Maintenance GUI ##
    #####################
    def load_maintenance(self):
        self.clear_main_panel()

        # filter butotn section
        filter_frame = tk.LabelFrame(self.main_panel, text="Filter")
        filter_frame.pack(pady=5, fill='x')
        fields = ["Vehicle ID", "Work Date"]
        for field in fields:
            tk.Button(
                filter_frame,
                text=f"By {field}",
                command=lambda f=field: self.prompt_maintenance_filter(f)
            ).pack(side='left', padx=5)

        # reset view
        tk.Button(filter_frame, text="View All", command=self.populate_maintenance_table).pack(side='left', padx=10)

        self.after_idle(self.populate_maintenance_table)

    def prompt_maintenance_filter(self, field):
        form = tk.Toplevel(self)
        form.title(f"Filter Maintenance by {field}")

        tk.Label(form, text=f"{field}:").pack(padx=10, pady=5)
        entry = tk.Entry(form)
        entry.pack(padx=10, pady=5)

        def apply():
            val = entry.get().strip()
            filters = {}
            try:
                if field == "Vehicle ID" and val:
                    filters["vehicle_id"] = int(val)
                elif field == "Work Date" and val:
                    try:
                        datetime.strptime(val, "%Y-%m-%d")
                        filters["work_date"] = val
                    except ValueError:
                        messagebox.showerror("Invalid Input", "Work Date must be in YYYY-MM-DD format.")
                        return
                else:
                    messagebox.showinfo("No Input", "Please enter a valid value.")
                    return

                self.populate_maintenance_table(**filters)
                form.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Vehicle ID must be an integer.")

        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_maintenance_table(self, **filters):
        print("Maintenance filters:", filters)

        if hasattr(self, 'maintenance_tree_container') and self.maintenance_tree_container.winfo_exists():
            self.maintenance_tree_container.destroy()

        self.maintenance_tree_container = tk.Frame(self.main_panel)
        self.maintenance_tree_container.pack(fill='both', expand=True)

        if getattr(self, 'button_frame', None):
            self.button_frame.destroy()

        self.tree = ttk.Treeview(
            self.maintenance_tree_container,
            columns=("ID", "Vehicle", "Date", "Work"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        records = crud.list_maintenance(**filters)
        for r in records:
            self.tree.insert('', 'end', values=(
                r['maintenance_id'],
                r['vehicle_id'],
                r['work_date'],
                r['work_performed']
            ))

        self.autosize_tree()

        self.button_frame = tk.Frame(self.main_panel)
        self.button_frame.pack(pady=10)

        tk.Button(self.button_frame, text="Add", command=self.add_maintenance).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Update", command=self.update_maintenance).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Delete", command=self.delete_maintenance).pack(side='left', padx=5)


    def add_maintenance(self):
        form = tk.Toplevel(self)
        form.title("Add Maintenance Record")

        tk.Label(form, text="Vehicle ID").grid(row=0, column=0)
        vehicle_entry = tk.Entry(form)
        vehicle_entry.grid(row=0, column=1)

        tk.Label(form, text="Work Date (YYYY-MM-DD)").grid(row=1, column=0)
        date_entry = tk.Entry(form)
        date_entry.grid(row=1, column=1)

        tk.Label(form, text="Work Performed").grid(row=2, column=0)
        work_entry = tk.Entry(form)
        work_entry.grid(row=2, column=1)

        def submit():
            try:
                crud.add_maintenance(
                    int(vehicle_entry.get()),
                    date_entry.get(),
                    work_entry.get()
                )
                form.destroy()
                self.load_maintenance()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=3, columnspan=2)

    def update_maintenance(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Please select a record to update.")
            return

        values = self.tree.item(selected[0])['values']
        m_id, v_id, date, work = values

        form = tk.Toplevel(self)
        form.title("Update Maintenance")

        tk.Label(form, text="Vehicle ID").grid(row=0, column=0)
        vehicle_entry = tk.Entry(form)
        vehicle_entry.insert(0, v_id)
        vehicle_entry.grid(row=0, column=1)

        tk.Label(form, text="Work Date (YYYY-MM-DD)").grid(row=1, column=0)
        date_entry = tk.Entry(form)
        date_entry.insert(0, date)
        date_entry.grid(row=1, column=1)

        tk.Label(form, text="Work Performed").grid(row=2, column=0)
        work_entry = tk.Entry(form)
        work_entry.insert(0, work)
        work_entry.grid(row=2, column=1)

        def submit():
            try:
                crud.update_maintenance(
                    maintenance_id=m_id,
                    vehicle_id=int(vehicle_entry.get()),
                    work_date=date_entry.get(),
                    work_performed=work_entry.get()
                )
                form.destroy()
                self.load_maintenance()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=3, columnspan=2)

    def delete_maintenance(self):
        selected = self.tree.selection()
        if not selected:
            return
        maintenance_id = self.tree.item(selected[0])['values'][0]
        try:
            crud.delete_maintenance(maintenance_id)
            self.load_maintenance()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ###############
    ## Stops GUI ##
    ###############
    def reset_stop_filters(self):
        self.stop_filters = {}
        self.populate_stop_table()

    def load_stops(self):
        self.clear_main_panel()

        filter_frame = tk.LabelFrame(self.main_panel, text="Filter")
        filter_frame.pack(pady=5, fill='x')

        fields = ["Stop ID", "Direction", "Street"]
        for field in fields:
            tk.Button(
                filter_frame,
                text=f"By {field}",
                command=lambda f=field: self.prompt_stop_filter(f)
            ).pack(side='left', padx=5)

        # reset filters
        tk.Button(filter_frame, text="View All", command=self.reset_stop_filters).pack(side='left', padx=10)

        self.populate_stop_table()
        self.autosize_tree()

    def prompt_stop_filter(self, field):
        form = tk.Toplevel(self)
        form.title(f"Filter Stops by {field}")

        tk.Label(form, text=f"{field}:").pack(padx=10, pady=5)
        entry = tk.Entry(form)
        entry.pack(padx=10, pady=5)

        def apply():
            val = entry.get().strip()
            filters = {}
            try:
                if field == "Stop ID" and val:
                    self.stop_filters["stop_id"] = int(val)
                elif field == "Direction" and val:
                    self.stop_filters["stop_direction"] = val
                elif field == "Street" and val:
                    self.stop_filters["street_name"] = val
                else:
                    messagebox.showinfo("No Input", "Please enter a valid value.")
                    return

                self.populate_stop_table(**self.stop_filters)
                form.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Stop ID must be an integer.")

        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_stop_table(self, **filters):
        if hasattr(self, 'stop_tree_container') and self.stop_tree_container.winfo_exists():
            self.stop_tree_container.destroy()

        self.stop_tree_container = tk.Frame(self.main_panel)
        self.stop_tree_container.pack(fill='both', expand=True)

        if getattr(self, 'button_frame', None):
            self.button_frame.destroy()

        self.tree = ttk.Treeview(
            self.stop_tree_container,
            columns=("ID", "Direction", "Street", "Cross Street", "Latitude", "Longitude"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)
        stops = crud.list_stops(**filters)
        self.tree.delete(*self.tree.get_children())
        for record in stops:
            self.tree.insert('', 'end', values=(
                record['stop_id'],
                record['stop_direction'],
                record['street_name'],
                record['cross_street'],
                record['latitude'],
                record['longitude']
            ))

        self.autosize_tree()
        self.button_frame = tk.Frame(self.main_panel)
        self.button_frame.pack(pady=10)
        tk.Button(self.button_frame, text="Add", command=self.add_stop).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Update", command=self.update_stop).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Delete", command=self.delete_stop).pack(side='left', padx=5)

    def add_stop(self):
        form = tk.Toplevel(self)
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
                self.load_stops()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=len(labels), columnspan=2)

    def update_stop(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Stop", "Please select a stop to update.")
            return

        values = self.tree.item(selected[0])['values']
        stop_id, direction, street, cross, lat, lon = values

        form = tk.Toplevel(self)
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
                self.load_stops()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=len(fields), columnspan=2)

    def delete_stop(self):
        selected = self.tree.selection()
        if not selected:
            return
        stop_id = self.tree.item(selected[0])['values'][0]
        try:
            crud.delete_stop(stop_id)
            self.load_stops()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ###############
    ## Trips GUI ##
    ###############
    def reset_trip_filters(self):
        self.trip_filters = {}
        self.populate_trip_table()

    def load_trips(self):
        self.clear_main_panel()

        # Filter button section
        filter_frame = tk.LabelFrame(self.main_panel, text="Filter")
        filter_frame.pack(pady=5, fill='x')

        fields = ["Trip ID", "Trip Date", "Route Name", "Route ID", "Driver Name", "Driver ID", "Vehicle ID",]
        for field in fields:
            tk.Button(
                filter_frame,
                text=f"By {field}",
                command=lambda f=field: self.prompt_trip_filter(f)
            ).pack(side='left', padx=5)

        # reset filters
        tk.Button(filter_frame, text="View All", command=self.reset_trip_filters).pack(side='left', padx=10)

        self.populate_trip_table()
        self.autosize_tree()

    def prompt_trip_filter(self, field):
        form = tk.Toplevel(self)
        form.title(f"Filter Trips by {field}")

        tk.Label(form, text=f"{field}:").pack(padx=10, pady=5)
        entry = tk.Entry(form)
        entry.pack(padx=10, pady=5)

        def apply():
            val = entry.get().strip()
            filters = {}

            try:
                if field == "Trip ID" and val:
                    self.trip_filters["trip_id"] = int(val)
                elif field == "Route ID" and val:
                    self.trip_filters["route_id"] = int(val)
                elif field == "Route Name" and val:
                    self.trip_filters["route_name"] = val
                elif field == "Driver ID" and val:
                    self.trip_filters["driver_id"] = int(val)
                elif field == "Driver Name" and val:
                    self.trip_filters["driver_name"] = val
                elif field == "Vehicle ID" and val:
                    self.trip_filters["vehicle_id"] = int(val)
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
                self.populate_trip_table(**self.trip_filters)
                form.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Numeric fields must be integers.")
        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_trip_table(self, **filters):
        print("Trip filters:", filters)

        # Destroy existing tree container if it exists
        if hasattr(self, 'trip_tree_container') and self.trip_tree_container.winfo_exists():
            self.trip_tree_container.destroy()

        self.trip_tree_container = tk.Frame(self.main_panel)
        self.trip_tree_container.pack(fill='both', expand=True)

        if getattr(self, 'button_frame', None):
            self.button_frame.destroy()

        self.tree = ttk.Treeview(
            self.trip_tree_container,
            columns=("ID", "Date", "Route Name", "Route ID", "Direction", "Driver Name", "Driver ID", "Vehicle ID"),
            show='headings'
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        trips = crud.list_trips(**filters)
        print(f"Trip results: {len(trips)} rows")
        self.tree.delete(*self.tree.get_children())

        for trip in trips:
            self.tree.insert('', 'end', values=(
                trip['trip_id'],
                trip['trip_date'],
                trip['route_name'],
                trip['route_id'],
                trip['trip_direction'],
                trip['driver_name'],
                trip['driver_id'],
                trip['vehicle_id']
            ))

        self.autosize_tree()

        self.button_frame = tk.Frame(self.main_panel)
        self.button_frame.pack(pady=10)

        tk.Button(self.button_frame, text="Add", command=self.add_trip).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Update", command=self.update_trip).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Delete", command=self.delete_trip).pack(side='left', padx=5)

    def add_trip(self):
        form = tk.Toplevel(self)
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
                self.load_trips()
            except OperationalError as oe:
                messagebox.showerror("Driver Conflict", f"Driver conflict, driver is already assigned to a differnt route on that day.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=len(labels), columnspan=2)

    def update_trip(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Trip", "Please select a trip to update.")
            return

        values = self.tree.item(selected[0])['values']
        trip_id, route_id, driver_id, vehicle_id, date, direction = values

        form = tk.Toplevel(self)
        form.title("Update Trip")

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
                self.load_trips()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=len(fields), columnspan=2)

    def delete_trip(self):
        selected = self.tree.selection()
        if not selected:
            return
        trip_id = self.tree.item(selected[0])['values'][0]
        try:
            crud.delete_trip(trip_id)
            self.load_trips()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ####################
    ## Route-Stop GUI ##
    ####################
    def reset_route_stop_filters(self):
        self.route_stop_filters = {}
        self.populate_route_stop_table()

    def load_route_stops(self):
        self.clear_main_panel()

        filter_frame = tk.LabelFrame(self.main_panel, text="Filter")
        filter_frame.pack(pady=5, fill='x')

        fields = ["Route ID", "Route Name", "Direction"]
        for field in fields:
            tk.Button(
                filter_frame,
                text=f"By {field}",
                command=lambda f=field: self.prompt_route_stop_filter(f)
            ).pack(side='left', padx=5)

        # reset filters
        tk.Button(filter_frame, text="View All", command=self.reset_route_stop_filters).pack(side='left', padx=10)

        self.populate_route_stop_table()

    def prompt_route_stop_filter(self, field):
        form = tk.Toplevel(self)
        form.title(f"Filter Route-Stops by {field}")

        tk.Label(form, text=f"{field}:").pack(padx=10, pady=5)
        entry = tk.Entry(form)
        entry.pack(padx=10, pady=5)

        def apply():
            val = entry.get().strip()
            filters = {}

            try:
                if field == "Route ID" and val:
                    self.route_stop_filters["route_id"] = int(val)
                elif field == "Direction" and val:
                    self.route_stop_filters["route_direction"] = val
                elif field == "Route Name" and val:
                    self.route_stop_filters["route_name"] = val
                else:
                    messagebox.showinfo("No Input", "Please enter a valid value.")
                    return

                self.populate_route_stop_table(**self.route_stop_filters)
                form.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Route ID must be an integer.")

        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_route_stop_table(self, **filters):
        if getattr(self, 'tree', None):
            self.tree.destroy()
        if hasattr(self, 'route_stop_tree_container') and self.route_stop_tree_container.winfo_exists():
            self.route_stop_tree_container.destroy()
        if getattr(self, 'button_frame', None):
            self.button_frame.destroy()

        self.route_stop_tree_container = tk.Frame(self.main_panel)
        self.route_stop_tree_container.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(
            self.route_stop_tree_container,
            columns=("Route ID", "Route Name", "Direction", "Stop ID", "Cross Street", "Stop Order"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        records = crud.list_route_stop(**filters)
        for record in records:
            self.tree.insert('', 'end', values=(
                record['route_id'],
                record['route_name'],
                record['route_direction'],
                record['stop_id'],
                record['cross_street'],
                record["stop_order"]
            ))

        self.autosize_tree()

        self.button_frame = tk.Frame(self.main_panel)
        self.button_frame.pack(pady=10)
        tk.Button(self.button_frame, text="Add", command=self.add_route_stop).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Update", command=self.update_route_stop).pack(side='left', padx=5)
        tk.Button(self.button_frame, text="Delete", command=self.delete_route_stop).pack(side='left', padx=5)

    def add_route_stop(self):
        form = tk.Toplevel(self)
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
                self.populate_route_stop_table()
                form.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Add", command=submit).grid(row=4, columnspan=2, pady=10)

    def update_route_stop(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a route-stop to update.")
            return

        current = self.tree.item(selected[0])['values']
        route_id, _, _, old_stop_id = current 

        form = tk.Toplevel(self)
        form.title("Update Route-Stop Link")

        tk.Label(form, text="New Stop ID:").grid(row=0, column=0)
        stop_entry = tk.Entry(form)
        stop_entry.insert(0, old_stop_id)
        stop_entry.grid(row=0, column=1)

        def submit():
            try:
                new_stop_id = int(stop_entry.get())
                if new_stop_id != old_stop_id:
                    crud.update_route_stop(route_id, old_stop_id, new_stop_id)
                self.populate_route_stop_table()
                form.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=1, columnspan=2, pady=10)

    def delete_route_stop(self):
        selected = self.tree.selection()
        if not selected:
            return
        route_id, _, _, stop_id = self.tree.item(selected[0])['values']
        try:
            crud.delete_route_stop(route_id, stop_id)
            self.populate_route_stop_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

###################
## Timetable GUI ##
################### 
    def reset_trip_stop_filters(self):
        self.trip_stop_filters = {}
        self.populate_trip_stop_table()

    def load_trip_stops(self):
        self.clear_main_panel()
        self.trip_stop_filters = {}

        self.trip_stop_filter_frame = tk.LabelFrame(self.main_panel, text="Filter")
        self.trip_stop_filter_frame.pack(pady=5, fill='x')

        fields = ["Route Name", "Direction"]
        for field in fields:
            tk.Button(
                self.trip_stop_filter_frame,
                text=f"By {field}",
                command=lambda f=field: self.prompt_trip_stop_filter(f)
            ).pack(side='left', padx=5)

        tk.Button(self.trip_stop_filter_frame, text="View All", command=self.reset_trip_stop_filters).pack(side='left', padx=10)

        self.populate_trip_stop_table()

    def prompt_trip_stop_filter(self, field):
        form = tk.Toplevel(self)
        form.title(f"Filter Trip-Stops by {field}")

        tk.Label(form, text=f"{field}:").pack(padx=10, pady=5)
        entry = tk.Entry(form)
        entry.pack(padx=10, pady=5)

        def apply():
            val = entry.get().strip()
            if field == "Route Name" and val:
                self.trip_stop_filters["route_name"] = val
            elif field == "Direction" and val:
                self.trip_stop_filters["trip_direction"] = val
            else:
                messagebox.showinfo("No Input", "Please enter a valid value.")
                return

            self.populate_trip_stop_table(**self.trip_stop_filters)
            form.destroy()

        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_trip_stop_table(self, **filters):
        if hasattr(self, 'trip_stop_tree_container') and self.trip_stop_tree_container.winfo_exists():
            self.trip_stop_tree_container.destroy()

        if getattr(self, 'button_frame', None):
            self.button_frame.destroy()

        self.trip_stop_tree_container = tk.Frame(self.main_panel)
        self.trip_stop_tree_container.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(
            self.trip_stop_tree_container,
            columns=("Route", "Direction", "Street", "Cross Street", "Arrival Time"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        rows = crud.list_trip_stop(**filters)
        for r in rows:
            self.tree.insert('', 'end', values=(
                r['route_name'],
                r['trip_direction'],
                r['street_name'],
                r['cross_street'],
                r['arrival_time']
            ))

        self.autosize_tree()

        self.button_frame = tk.Frame(self.main_panel)
        self.button_frame.pack(pady=10)

    ##################
    ## Analysis GUI ##
    ##################

    def load_analysis(self):
        self.clear_main_panel()

        # find all shared routes
        self.shared_all_frame = tk.LabelFrame(self.main_panel, text="Find shared stops among all Routes")
        self.shared_all_frame.pack(pady=5, fill='x')
        tk.Button(
            self.shared_all_frame,
            text="Search",
            command=self.run_stops_shared_by_all_routes
        ).pack(side='left', padx=10)

        # find shared stops between two routes 
        self.analysis_filter_frame = tk.LabelFrame(self.main_panel, text="Find shared routes among two routes")
        self.analysis_filter_frame.pack(pady=5, fill='x')
        # Route A input
        route_a_frame = tk.Frame(self.analysis_filter_frame)
        route_a_frame.pack(side='left', padx=5)
        tk.Label(route_a_frame, text="Route ID A:").pack(side='top')
        self.route_a_entry = tk.Entry(route_a_frame, width=8, bg='white', fg='black', insertbackground='black')
        self.route_a_entry.pack(side='top')
        self.route_a_entry.update_idletasks()
        # Route B input
        route_b_frame = tk.Frame(self.analysis_filter_frame)
        route_b_frame.pack(side='left', padx=5)
        tk.Label(route_b_frame, text="Route ID B:").pack(side='top')
        self.route_b_entry = tk.Entry(route_b_frame, width=8, bg='white', fg='black', insertbackground='black')
        self.route_b_entry.pack(side='top')
        self.route_b_entry.update_idletasks()
        # Submit button
        tk.Button(
            self.analysis_filter_frame,
            text="Find Shared Stops",
            command=self.run_shared_stops_analysis
        ).pack(side='left', padx=10)

        # find drivers with no assignment on a given day
        self.driver_avail_frame = tk.LabelFrame(self.main_panel, text="Driver Availability by Date")
        self.driver_avail_frame.pack(pady=5, fill='x')
        self.route_b_entry.update_idletasks()
        tk.Label(self.driver_avail_frame, text="Trip Date (YYYY-MM-DD):").pack(side='left', padx=5)
        self.driver_avail_entry = tk.Entry(self.driver_avail_frame, width=12)
        self.driver_avail_entry.pack(side='left', padx=5)
        tk.Button(
            self.driver_avail_frame,
            text="Find Available Drivers",
            command=self.run_driver_availability_analysis
        ).pack(side='left', padx=10)

        # calcculate vehicle load - total trips by each vehicle
        self.vehicle_usage_frame = tk.LabelFrame(self.main_panel, text="Determine Vehicle Utilization - Number of Trips by Vehicle")
        self.vehicle_usage_frame.pack(pady=5, fill='x')
        tk.Button(
            self.vehicle_usage_frame,
            text="Calculate",
            command=self.run_vehicle_trip_counts
        ).pack(side='left', padx=10)

        # rank drivers by trip count
        self.driver_rank_frame = tk.LabelFrame(self.main_panel, text="Driver Ranking")
        self.driver_rank_frame.pack(pady=5, fill='x')
        tk.Button(
            self.driver_rank_frame,
            text="Rank Drivers by Trip Count",
            command=self.run_driver_rank_analysis
        ).pack(side='left', padx=10)

        # average time between maintenance
        self.maint_avg_frame = tk.LabelFrame(self.main_panel, text="Vehicle Maintenance Interval Analysis - Average Days Between Maintenance")
        self.maint_avg_frame.pack(pady=5, fill='x')
        tk.Button(
            self.maint_avg_frame,
            text="Calculate",
            command=self.run_avg_maintenance_gap
        ).pack(side='left', padx=10)

        self.analysis_tree_container = tk.Frame(self.main_panel)
        self.analysis_tree_container.pack(fill='both', expand=True)

    def run_shared_stops_analysis(self):
        route_a = self.route_a_entry.get().strip()
        route_b = self.route_b_entry.get().strip()

        if not (route_a.isdigit() and route_b.isdigit()):
            messagebox.showerror("Invalid Input", "Please enter valid route IDs.")
            return

        route_a = int(route_a)
        route_b = int(route_b)

        results = crud.get_shared_stops(route_a, route_b)

        # Destroy previous tree if needed
        if getattr(self, 'tree', None):
            self.tree.destroy()

        self.tree = ttk.Treeview(
            self.analysis_tree_container,
            columns=("Stop ID", "Street", "Cross Street", "Lat", "Lon"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        for row in results:
            self.tree.insert('', 'end', values=(
                row["stop_id"],
                row["street_name"],
                row["cross_street"],
                row["latitude"],
                row["longitude"]
            ))

    def run_stops_shared_by_all_routes(self):
        results = crud.get_all_shared_stops()

        if getattr(self, 'tree', None):
            self.tree.destroy()

        self.tree = ttk.Treeview(
            self.analysis_tree_container,
            columns=("Stop ID", "Street", "Cross Street", "Lat", "Lon"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        for row in results:
            self.tree.insert('', 'end', values=(
                row["stop_id"],
                row["street_name"],
                row["cross_street"],
                row["latitude"],
                row["longitude"]
            ))

    def run_driver_availability_analysis(self):
        date = self.driver_avail_entry.get().strip()
        if not date:
            messagebox.showerror("Missing Date", "Please enter a valid trip date (YYYY-MM-DD).")
            return
        try:
            from datetime import datetime
            datetime.strptime(date, "%Y-%m-%d")  # basic format validation
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format.")
            return
        results = crud.get_available_drivers(date)
        if getattr(self, 'tree', None):
            self.tree.destroy()
        self.tree = ttk.Treeview(
            self.analysis_tree_container,
            columns=("Driver ID", "Name", "Classification", "Pay"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)
        for row in results:
            self.tree.insert('', 'end', values=(
                row["driver_id"],
                row["driver_name"],
                row["driver_classification"],
                row["pay"]
            ))

    def run_vehicle_trip_counts(self):
        results = crud.get_vehicle_trip_counts()

        if getattr(self, 'tree', None):
            self.tree.destroy()

        self.tree = ttk.Treeview(
            self.analysis_tree_container,
            columns=("Vehicle ID", "Trip Count", "Class", "Manufacturer", "Year", "Type", "Capacity"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        for row in results:
            self.tree.insert('', 'end', values=(
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
        for col in self.tree["columns"]:
            self.tree.column(col, width=column_widths.get(col, 100), anchor='center')

    def run_driver_rank_analysis(self):
        results = crud.get_driver_trip_ranks()
        if getattr(self, 'tree', None):
            self.tree.destroy()
        self.tree = ttk.Treeview(
            self.analysis_tree_container,
            columns=("Driver ID", "Name", "Trip Count", "Rank"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)
        for row in results:
            self.tree.insert('', 'end', values=(
                row["driver_id"],
                row["driver_name"],
                row["trip_count"],
                row["trip_rank"]
            ))

    def run_avg_maintenance_gap(self):
        results = crud.get_avg_days_between_maintenance()

        if getattr(self, 'tree', None):
            self.tree.destroy()

        self.tree = ttk.Treeview(
            self.analysis_tree_container,
            columns=("Vehicle ID", "Avg Days Between Maintenance"),
            show='headings'
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        for row in results:
            self.tree.insert('', 'end', values=(
                row["vehicle_id"],
                row["avg_days_between"]
            ))


if __name__ == "__main__":
    app = TransitApp()
    app.mainloop()
