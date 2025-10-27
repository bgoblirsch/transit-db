import tkinter as tk
from tkinter import ttk, messagebox
from src.crud import routes as crud
from .utils import autosize_tree, clear_panel

def register_gui(app):
    def load_routes():
        clear_panel(app.main_panel)
        tree = ttk.Treeview(app.main_panel, columns=("ID", "Name", "Type"), show='headings')
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill='both', expand=True)

        for route in crud.list_routes():
            tree.insert('', 'end', values=(route['route_id'], route['route_name'], route['route_type']))

        autosize_tree(tree)


        button_frame = tk.Frame(app.main_panel)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add", command=lambda: route_add(app.main_panel)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Update", command=lambda: route_update(tree)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Delete", command=lambda: route_delete(tree)).pack(side='left', padx=5)

        return tree, button_frame

    def route_add(panel):
        form = tk.Toplevel(panel)
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
                load_routes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=3, columnspan=2)

    def route_update(tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Route", "Please select a route to update.")
            return

        item = tree.item(selected[0])
        values = item['values']
        route_id, name, route_type = values

        form = tk.Toplevel(app.main_panel)
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
                load_routes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=2, columnspan=2)

    def route_delete(tree):
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            route_id = item['values'][0]
            try:
                confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Route ID {route_id}?")
                if not confirm:
                    return
                crud.delete_route(route_id)
                load_routes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    app.load_routes = load_routes