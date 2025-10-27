import tkinter as tk
from tkinter import ttk, messagebox
from src.crud import drivers as crud
from .utils import autosize_tree, clear_panel, valid_date


def register_gui(app):
    def load_drivers():
        """
        Load driver table into the provided main_panel frame.
        Returns the treeview and button frame references.
        """
        clear_panel(app.main_panel)

        tree = ttk.Treeview(app.main_panel, columns=("ID", "Name", "Class", "Start", "Pay"), show='headings')
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill='both', expand=True)

        for driver in crud.list_drivers():
            tree.insert('', 'end', values=(
                driver['driver_id'],
                driver['driver_name'],
                driver['driver_classification'],
                driver['start_date'].isoformat() if driver['start_date'] else "—",
                f"{driver['pay']:.2f}"
            ))

        autosize_tree(tree)

        button_frame = tk.Frame(app.main_panel)
        button_frame.pack(pady=10)

        # Event handlers
        tk.Button(button_frame, text="Add", command=lambda: driver_add(app.main_panel)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Update", command=lambda: driver_update(tree)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Delete", command=lambda: driver_delete(tree)).pack(side='left', padx=5)

        return tree, button_frame


    def driver_add(panel):
        form = tk.Toplevel(panel)
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
                    messagebox.showerror("Invalid date", "Date must be YYYY-MM-DD and valid")
                    return
                crud.add_driver(
                    driver_name=name_entry.get(),
                    driver_classification=class_entry.get(),
                    start_date=start_date,
                    pay=float(pay_entry.get())
                )
                form.destroy()
                load_drivers()  # reload table
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Submit", command=submit).grid(row=4, columnspan=2)


    def driver_update(tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Driver", "Please select a driver to update.")
            return

        item = tree.item(selected[0])
        driver_id, name, classification, start_date, pay = item['values']

        form = tk.Toplevel(app.main_panel)
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
                start_date_val = date_entry.get()
                if start_date_val and not valid_date(start_date_val):
                    messagebox.showerror("Invalid date", "Date must be YYYY-MM-DD and valid")
                    return
                crud.update_driver(
                    driver_id,
                    driver_name=name_entry.get(),
                    driver_classification=class_entry.get(),
                    start_date=start_date_val,
                    pay=float(pay_entry.get())
                )
                form.destroy()
                load_drivers()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Update", command=submit).grid(row=4, columnspan=2)


    def driver_delete(tree):
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        driver_id = item['values'][0]
        try:
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this driver?")
            if not confirm:
                return
            crud.delete_driver(driver_id)
            load_drivers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    app.load_drivers = load_drivers