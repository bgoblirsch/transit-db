# Transit Management System

A desktop GUI application for managing and analyzing a basic public transit database using MySQL and Tkinter.

## Features

- Manage core entities: Drivers, Vehicles, Trips, Stops, Routes, Maintenance
- Custom filters for necessary tables
- Role-based login with restricted access (maintenance user)
- Analysis tab with advanced SQL examples.
- gui.py contains the tkinter logic for the GUI
- crud.py handles the crud operations as the link between the database and the UI.

## Requirements

- Python 3.10+
- MySQL 8.x
- Dependencies:
  - `sqlalchemy`
  - `pymysql`
  - `tkinter` (included with most Python installations)

Install dependencies:

```bash
pip install sqlalchemy pymysql
```

Create database and load mock data
```
mysql -u root < createDB-load.sql
```

Create indices and views
```
mysql -u root < index-views.sql
```

Setup triggers
```
mysql -u root < temp-trigger-storedProc-func.sql
```

Launch GUI
```
python src/gui.py
```

Login with:
- admin/admin
- maintenance/maintenance