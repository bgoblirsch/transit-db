import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.crud import maintenance as crud
from .utils import autosize_tree, clear_panel

def register_gui(app):
    def load_maintenance():
        clear_panel(app.main_panel)

        # filter butotn section
        filter_frame = tk.LabelFrame(app.main_panel, text="Filter")
        filter_frame.pack(pady=5, fill='x')
        fields = ["Vehicle ID", "Work Date"]
        for field in fields:
            tk.Button(
                filter_frame,
                text=f"By {field}",
                command=lambda f=field: prompt_maintenance_filter(f)
            ).pack(side='left', padx=5)

        # reset view
        tk.Button(filter_frame, text="Reset Filters", command=populate_maintenance_table).pack(side='left', padx=10)

        #after_idle(populate_maintenance_table)
        populate_maintenance_table()

    def prompt_maintenance_filter(field):
        form = tk.Toplevel(app)
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

                populate_maintenance_table(**filters)
                form.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Vehicle ID must be an integer.")

        tk.Button(form, text="Apply Filter", command=apply).pack(pady=10)

    def populate_maintenance_table(**filters):
        if hasattr(app, 'maintenance_tree_container') and app.maintenance_tree_container.winfo_exists():
            app.maintenance_tree_container.destroy()
        if hasattr(app, 'maintenance_button_frame') and app.maintenance_button_frame.winfo_exists():
            app.maintenance_button_frame.destroy()

        app.maintenance_tree_container = tk.Frame(app.main_panel)
        app.maintenance_tree_container.pack(fill='both', expand=True)

        tree = ttk.Treeview(
            app.maintenance_tree_container,
            columns=("ID", "Vehicle", "Date", "Work"),
            show='headings'
        )
        
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill='both', expand=True)
        app.maintenance_tree = tree

        records = crud.list_maintenance(**filters)
        for record in records:
            tree.insert('', 'end', values=(
                record['maintenance_id'],
                record['vehicle_id'],
                record['work_date'],
                record['work_performed']
            ))

        autosize_tree(tree)

        app.maintenance_button_frame = tk.Frame(app.main_panel)
        app.maintenance_button_frame.pack(pady=10)
        tk.Button(app.maintenance_button_frame, 
                  text="Add", 
                  command=lambda: maintenance_add(app.main_panel)).pack(side='left', padx=5)
        tk.Button(app.maintenance_button_frame, 
                  text="Update", 
                  command=lambda: maintenance_update(tree)).pack(side='left', padx=5)
        tk.Button(app.maintenance_button_frame, 
                  text="Delete", 
                  command=lambda: maintenance_delete(tree)).pack(side='left', padx=5)


    def maintenance_add(panel):
        form = tk.Toplevel(panel)
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
                load_maintenance()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=3, columnspan=2)

    def maintenance_update(tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Please select a record to update.")
            return

        values = tree.item(selected[0])['values']
        m_id, v_id, date, work = values

        form = tk.Toplevel(app.main_panel)
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
                load_maintenance()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=3, columnspan=2)

    def maintenance_delete(tree):
        selected = tree.selection()
        if not selected:
            return
        maintenance_id = tree.item(selected[0])['values'][0]
        try:
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this maintenance record?")
            if not confirm:
                return
            crud.delete_maintenance(maintenance_id)
            load_maintenance()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    app.load_maintenance = load_maintenance