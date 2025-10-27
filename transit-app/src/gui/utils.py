from datetime import datetime
import tkinter as tk
import tkinter.font as tkFont

def valid_date(value: str) -> bool:
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.year > 1900
    except ValueError:
        return False
    
def valid_year(value: int) -> bool:
    return value > 1900 and value < 2030

def autosize_tree(tree):
    tree_font = tkFont.Font()

    for col_index, col in enumerate(tree["columns"]):
        max_width = tree_font.measure(col)
        for row in tree.get_children():
            val = tree.item(row)['values'][col_index]
            max_width = max(max_width, tree_font.measure(str(val)))
        tree.column(col, width=max_width + 20)

def clear_panel(panel):
    for widget in panel.winfo_children():
        widget.destroy()
