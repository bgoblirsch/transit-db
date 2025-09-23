from contextlib import contextmanager
import datetime
import decimal
from typing import Optional
from rich.table import Table
from rich.console import Console
from sqlalchemy import select, update, delete
from sqlalchemy.exc import NoResultFound
from database import SessionLocal
import models as m
from enum import Enum

class DriverKey(str, Enum):
    id = "id"
    name = "name"

console = Console()

@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

################
## Route CRUD ##
################

def add_route(route_id: int, 
              name: str, 
              rtype: str):
    """Add a route"""
    with session_scope() as s:
        s.add(m.Route(route_id=route_id, route_name=name, route_type=rtype))
        console.print(f"Added route {name}")

def get_route(route_name: str) -> None:
    """Fetch and print a single route by name."""
    with session_scope() as s:
        route = s.scalar(select(m.Route).where(m.Route.route_name == route_name))
        if not route:
            raise NoResultFound(f"Route {route_name} not found")

        table = Table(title=f"Route {route.route_name}")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("route_id", str(route.route_id))
        table.add_row("route_name", route.route_name)
        table.add_row("route_type", route.route_type)
        console.print(table)

def list_routes():
    with session_scope() as s:
        rows = s.scalars(select(m.Route)).all()
        table = Table(title="Routes", show_lines=True)
        for col in ("ID", "Name", "Type"):
            table.add_column(col)
        for r in rows:
            table.add_row(str(r.route_id), r.route_name, r.route_type)
        console.print(table)

def update_route(route_id: int, name: str, rtype: str) -> None:
    with session_scope() as s:
        statement = update(m.Route).where(m.Route.route_id == route_id)
        if name:
            statement = statement.values(route_name=name)
        if rtype:
            statement = statement.values(route_type=rtype)
        result = s.execute(statement)
        if result.rowcount == 0:
            raise NoResultFound(f"Route {route_id} not found")
    console.print(f"Updated route {route_id}")


def delete_route(route_id: int) -> None:
    with session_scope() as s:
        result = s.execute(delete(m.Route).where(m.Route.route_id == route_id))
        if result.rowcount == 0:
            raise NoResultFound(f"Route {route_id} not found")
    console.print(f"Deleted route {route_id}")

##################
## Vehicle CRUD ##
##################

def add_vehicle(vehicle_id: int,
                vclass: str,
                manufacturer: str,
                year: int,
                vtype: str,
                capacity: int | None) -> None:
    with session_scope() as s:
        s.add(m.Vehicle(
            vehicle_id     = vehicle_id,
            vehicle_class  = vclass,
            manufacturer   = manufacturer,
            manufacture_year = year,
            vehicle_type   = vtype,
            capacity       = capacity,
        ))
    console.print(f"Added vehicle {vehicle_id}")

def get_vehicle(vehicle_id: int) -> None:
    with session_scope() as s:
        v = s.scalar(select(m.Vehicle).where(m.Vehicle.vehicle_id == vehicle_id))
        if not v:
            raise NoResultFound(f"Vehicle {vehicle_id} not found")
        table = Table(title=f"Vehicle {vehicle_id}")
        table.add_column("Field")
        table.add_column("Value")
        for field in ("vehicle_id", "vehicle_class", "manufacturer",
                    "manufacture_year", "vehicle_type", "capacity"):
            table.add_row(field, str(getattr(v, field)))
        console.print(table)

def list_vehicles():
    with session_scope() as s:
        statement = select(m.Vehicle)
        rows = s.scalars(statement).all()
        table = Table(title="Vehicles")
        for col in ("ID", "Class", "Mfr", "Year", "Type", "Cap"):
            table.add_column(col)
        for v in rows:
            table.add_row(str(v.vehicle_id), v.vehicle_class, v.manufacturer,
                        str(v.manufacture_year), v.vehicle_type,
                        str(v.capacity) if v.capacity is not None else "—")
        console.print(table)

def update_vehicle(vehicle_id: int,
                   vclass: str | None = None,
                   manufacturer: str | None = None,
                   year: int | None = None,
                   vtype: str | None = None,
                   capacity: int | None = None) -> None:
    with session_scope() as s:
        statement = update(m.Vehicle).where(m.Vehicle.vehicle_id == vehicle_id)
        if vclass is not None:       statement = statement.values(vehicle_class=vclass)
        if manufacturer is not None: statement = statement.values(manufacturer=manufacturer)
        if year is not None:         statement = statement.values(manufacture_year=year)
        if vtype is not None:        statement = statement.values(vehicle_type=vtype)
        if capacity is not None:     statement = statement.values(capacity=capacity)
        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"Vehicle {vehicle_id} not found")
    console.print(f"Updated vehicle {vehicle_id}")

def delete_vehicle(vehicle_id: int) -> None:
    with session_scope() as s:
        if s.execute(delete(m.Vehicle).where(m.Vehicle.vehicle_id == vehicle_id)).rowcount == 0:
            raise NoResultFound(f"Vehicle {vehicle_id} not found")
    console.print(f"Deleted vehicle {vehicle_id}")

#################
## Driver CRUD ##
#################

def add_driver(driver_name: str,
               driver_classification: str,
               start_date: Optional[str],
               pay: float) -> None:
    """Insert a new driver."""
    # parse date and pay
    start = datetime.date.fromisoformat(start_date) if start_date else None
    pay_decimal = decimal.Decimal(str(pay))

    with session_scope() as s:
        s.add(m.Driver(
            driver_name=driver_name,
            driver_classification=driver_classification,
            start_date=start,
            pay=pay_decimal,
        ))
    console.print(f"Added driver {driver_name}")

def get_driver(key: str, by: DriverKey = DriverKey.id) -> None:
    """Fetch a driver by name or ID."""
    with session_scope() as s:
        if by == DriverKey.id:
            driver = s.scalar(
                select(m.Driver).where(m.Driver.driver_id == int(key))
            )
        else: 
            driver = s.scalar(
                select(m.Driver).where(m.Driver.driver_name == key)
            )
        if not driver:
            raise NoResultFound(f"Driver '{key}' not found using {by.value}")

        table = Table(title=f"Driver {driver.driver_name}")
        table.add_column("Field")
        table.add_column("Value")
        for field in ("driver_id", "driver_name", "driver_classification",
                    "start_date", "pay"):
            table.add_row(field, str(getattr(driver, field)))
        console.print(table)

def list_drivers():
    """List all drivers."""
    with session_scope() as s:
        statement = select(m.Driver)
        rows = s.scalars(statement).all()

        table = Table(title="Drivers")
        for col in ("ID", "Name", "Class", "Start Date", "Pay"):
            table.add_column(col)
        for d in rows:
            table.add_row(
                str(d.driver_id),
                d.driver_name,
                d.driver_classification,
                d.start_date.isoformat() if d.start_date else "—",
                f"{d.pay:.2f}",
            )
        console.print(table)

def update_driver(driver_id: int,
                  driver_name: str | None = None,
                  driver_classification: str | None = None,
                  start_date: str | None = None,
                  pay: float | None = None) -> None:
    """Update a driver."""
    with session_scope() as s:
        statement = update(m.Driver).where(m.Driver.driver_id == driver_id)
        if driver_name is not None:
            statement = statement.values(driver_name=driver_name)
        if driver_classification is not None:
            statement = statement.values(
                driver_classification=driver_classification
            )
        if start_date is not None:
            statement = statement.values(
                start_date=datetime.date.fromisoformat(start_date)
            )
        if pay is not None:
            statement = statement.values(pay=decimal.Decimal(str(pay)))

        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"Driver {driver_id} not found")
    console.print(f"Updated driver {driver_id}")

def delete_driver(driver_id: int) -> None:
    """Remove a driver."""
    with session_scope() as s:
        statement = delete(m.Driver).where(m.Driver.driver_id == driver_id)
        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"Driver {driver_id} not found")
    console.print(f"Deleted driver {driver_id}")

######################
## Maintenance CRUD ##
######################

def add_maintenance(vehicle_id: int,
                    work_date: str,
                    work_performed: str) -> None:
    """Add a new maintenance record."""
    date_obj = datetime.date.fromisoformat(work_date)

    with session_scope() as s:
        vehicle = s.scalar(
            select(m.Vehicle).where(m.Vehicle.vehicle_id == vehicle_id)
        )
        if not vehicle:
            raise NoResultFound(f"Vehicle {vehicle_id} does not exist.")
        s.add(m.Maintenance(
            vehicle_id=vehicle_id,
            work_date=date_obj,
            work_performed=work_performed,
        ))
    console.print(f"Added maintenance record for vehicle {vehicle_id}")

def get_maintenance(maintenance_id: int) -> None:
    """Fetch and print a maintenance record by ID."""
    with session_scope() as s:
        mnt = s.scalar(
            select(m.Maintenance).where(
                m.Maintenance.maintenance_id == maintenance_id
            )
        )
        if not mnt:
            raise NoResultFound(f"Maintenance {maintenance_id} not found")

        table = Table(title=f"Maintenance {maintenance_id}")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        for field in ("maintenance_id", "vehicle_id",
                      "work_date", "work_performed"):
            table.add_row(field, str(getattr(mnt, field)))
        console.print(table)

def list_maintenance(vehicle_id: int | None = None) -> None:
    """List maintenance records."""
    with session_scope() as s:
        base = select(m.Maintenance)
        if vehicle_id is not None:
            base = base.where(m.Maintenance.vehicle_id == vehicle_id)
        rows = s.scalars(base).all()
        table = Table(title="Maintenance")
        for col in ("ID", "Vehicle", "Date", "Work Performed"):
            table.add_column(col)
        for mnt in rows:
            table.add_row(
                str(mnt.maintenance_id),
                str(mnt.vehicle_id),
                mnt.work_date.isoformat(),
                mnt.work_performed,
            )
        console.print(table)

def update_maintenance(maintenance_id: int,
                       vehicle_id: int | None = None,
                       work_date: str | None = None,
                       work_performed: str | None = None) -> None:
    """Update fields on a maintenance record."""
    with session_scope() as s:
        statement = update(m.Maintenance).where(
            m.Maintenance.maintenance_id == maintenance_id
        )
        if vehicle_id is not None:
            statement = statement.values(vehicle_id=vehicle_id)
        if work_date is not None:
            statement = statement.values(
                work_date=datetime.date.fromisoformat(work_date)
            )
        if work_performed is not None:
            statement = statement.values(work_performed=work_performed)

        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"Maintenance {maintenance_id} not found")
    console.print(f"Updated maintenance {maintenance_id}")

def delete_maintenance(maintenance_id: int) -> None:
    """Delete a maintenance record."""
    with session_scope() as s:
        statement = delete(m.Maintenance).where(
            m.Maintenance.maintenance_id == maintenance_id
        )
        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"Maintenance {maintenance_id} not found")
    console.print(f"Deleted maintenance {maintenance_id}")

###############
## Stop CRUD ##
###############

def add_stop(stop_id: int,
             stop_direction: str,
             street_name: str,
             cross_street: str,
             latitude: float | None,
             longitude: float | None) -> None:
    """Insert a new stop."""
    with session_scope() as s:
        s.add(m.Stop(
            stop_id=stop_id,
            stop_direction=stop_direction,
            street_name=street_name,
            cross_street=cross_street,
            latitude=latitude,
            longitude=longitude,
        ))
    console.print(f"Added stop {stop_id} at {street_name} and {cross_street} ({stop_direction} bound).")

def get_stop(stop_id: int) -> None:
    """Fetch and print a stop by ID."""
    with session_scope() as s:
        stop = s.scalar(
            select(m.Stop).where(m.Stop.stop_id == stop_id)
        )
        if not stop:
            raise NoResultFound(f"Stop {stop_id} not found")

        table = Table(title=f"Stop {stop_id}")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        for fld in ("stop_id", "stop_direction", "street_name",
                    "cross_street", "latitude", "longitude"):
            val = getattr(stop, fld)
            table.add_row(fld, "—" if val is None else str(val))
        console.print(table)

def list_stops(street_name: str | None = None) -> None:
    """List stops."""
    with session_scope() as s:
        base = select(m.Stop)
        if street_name:
            base = base.where(func.lower(m.Stop.street_name) == street_name.lower())
        rows = s.scalars(base).all()

        table = Table(title="Stops")
        for col in ("ID", "Dir", "Street", "Cross", "Lat", "Lon"):
            table.add_column(col)
        for st in rows:
            table.add_row(
                str(st.stop_id),
                st.stop_direction,
                st.street_name,
                st.cross_street,
                f"{st.latitude:.6f}"   if st.latitude  is not None else "—",
                f"{st.longitude:.6f}"  if st.longitude is not None else "—",
            )
        console.print(table)

def update_stop(stop_id: int,
                stop_direction: str | None = None,
                street_name: str | None = None,
                cross_street: str | None = None,
                latitude: float | None = None,
                longitude: float | None = None) -> None:
    """Update fields on a stop."""
    with session_scope() as s:
        statement = update(m.Stop).where(m.Stop.stop_id == stop_id)
        if stop_direction is not None:
            statement = statement.values(stop_direction=stop_direction)
        if street_name is not None:
            statement = statement.values(street_name=street_name)
        if cross_street is not None:
            statement = statement.values(cross_street=cross_street)
        if latitude is not None:
            statement = statement.values(latitude=latitude)
        if longitude is not None:
            statement = statement.values(longitude=longitude)

        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"Stop {stop_id} not found")
    console.print(f"Updated stop {stop_id}")

def delete_stop(stop_id: int) -> None:
    """Delete a stop."""
    with session_scope() as s:
        statement = delete(m.Stop).where(m.Stop.stop_id == stop_id)
        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"Stop {stop_id} not found")
    console.print(f"Deleted stop {stop_id}")

###############
## Trip CRUD ##
###############

def add_trip(trip_id: int,
             route_id: int,
             driver_id: int,
             vehicle_id: int,
             trip_date: str,
             trip_direction: str) -> None:
    """Insert a new trip."""
    date_obj = datetime.date.fromisoformat(trip_date)
    with session_scope() as s:
        s.add(m.Trip(
            trip_id=trip_id,
            route_id=route_id,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            trip_date=date_obj,
            trip_direction=trip_direction,
        ))
    console.print(f"Added trip {trip_id}")

def get_trip(trip_id: int) -> None:
    """Fetch and print a trip by ID."""
    with session_scope() as s:
        trip = s.scalar(
            select(m.Trip).where(m.Trip.trip_id == trip_id)
        )
        if not trip:
            raise NoResultFound(f"Trip {trip_id} not found")

        table = Table(title=f"Trip {trip_id}")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        for field in ("trip_id", "route_id", "driver_id", "vehicle_id",
                      "trip_date", "trip_direction"):
            table.add_row(field, str(getattr(trip, field)))
        console.print(table)

def list_trips(route_id: int | None = None) -> None:
    """List trips (optionally filtered by route)."""
    with session_scope() as s:
        base = select(m.Trip)
        if route_id is not None:
            base = base.where(m.Trip.route_id == route_id)
        rows = s.scalars(base).all()

        title = f"Trips for route ID {route_id}" if route_id else "Trips"
        table = Table(title=title)
        for col in ("ID", "Route", "Driver", "Vehicle", "Date", "Dir"):
            table.add_column(col)
        for t in rows:
            table.add_row(
                str(t.trip_id), str(t.route_id), str(t.driver_id),
                str(t.vehicle_id), t.trip_date.isoformat(), t.trip_direction
            )
        console.print(table)

def update_trip(trip_id: int,
                route_id: int | None = None,
                driver_id: int | None = None,
                vehicle_id: int | None = None,
                trip_date: str | None = None,
                trip_direction: str | None = None) -> None:
    """Update fields on a trip."""
    with session_scope() as s:
        statement = update(m.Trip).where(m.Trip.trip_id == trip_id)
        if route_id is not None:
            statement = statement.values(route_id=route_id)
        if driver_id is not None:
            statement = statement.values(driver_id=driver_id)
        if vehicle_id is not None:
            statement = statement.values(vehicle_id=vehicle_id)
        if trip_date is not None:
            statement = statement.values(trip_date=datetime.date.fromisoformat(trip_date))
        if trip_direction is not None:
            statement = statement.values(trip_direction=trip_direction)

        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"Trip {trip_id} not found")
    console.print(f"Updated trip {trip_id}")

def delete_trip(trip_id: int) -> None:
    """Delete a trip."""
    with session_scope() as s:
        statement = delete(m.Trip).where(m.Trip.trip_id == trip_id)
        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"Trip {trip_id} not found")
    console.print(f"Deleted trip {trip_id}")

#####################
## Route-Stop CRUD ##
#####################

def add_route_stop(route_id: int,
                   stop_id: int,
                   route_direction: str,
                   stop_order: int) -> None:
    """Add a stop to a route with direction and order."""
    with session_scope() as s:
        s.add(m.RouteStop(
            route_id=route_id,
            stop_id=stop_id,
            route_direction=route_direction,
            stop_order=stop_order,
        ))
    console.print(f"Added stop {stop_id} to route {route_id} ({route_direction})")

def list_route_stops(route_id: int, route_direction: str) -> list[m.RouteStop]:
    """Return list of stops for a route in a given direction, ordered."""
    with session_scope() as s:
        statement = (
            select(m.RouteStop)
            .where(
                m.RouteStop.route_id == route_id,
                m.RouteStop.route_direction == route_direction,
            )
            .order_by(m.RouteStop.stop_order)
        )
        return s.scalars(statement).all()
    
def update_route_stop(route_id: int,
                      stop_id: int,
                      route_direction: str,
                      stop_order: int) -> None:
    """Update the stop order for a route-stop entry."""
    with session_scope() as s:
        statement = (
            update(m.RouteStop)
            .where(
                m.RouteStop.route_id == route_id,
                m.RouteStop.stop_id == stop_id,
                m.RouteStop.route_direction == route_direction,
            )
            .values(stop_order=stop_order)
        )
        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"RouteStop not found for route {route_id}, stop {stop_id}, direction {route_direction}")
    console.print(f"Updated stop_order to {stop_order} for route {route_id}, stop {stop_id}, dir {route_direction}")

    
def delete_route_stop(route_id: int, stop_id: int, route_direction: str) -> None:
    """Remove a stop from a route."""
    with session_scope() as s:
        statement = delete(m.RouteStop).where(
            m.RouteStop.route_id == route_id,
            m.RouteStop.stop_id == stop_id,
            m.RouteStop.route_direction == route_direction,
        )
        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"RouteStop not found for route {route_id}, stop {stop_id}, direction {route_direction}")
    console.print(f"Deleted stop {stop_id} from route {route_id} ({route_direction})")

####################
## Trip-Stop CRUD ##
####################

def min_to_24(minutes: int) -> str:
    """Convert minutes (0–1440) to 24-hour time string 'HH:MM'."""
    if not (0 <= minutes <= 1440):
        raise ValueError("Minutes must be between 0 and 1440")
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02}:{mins:02}"


def add_trip_stop_minutes(trip_id: int, stop_id: int, arrival_time: int) -> None:
    """Add a trip-stop using raw minutes format."""
    with session_scope() as s:
        s.add(m.TripStop(
            trip_id=trip_id,
            stop_id=stop_id,
            arrival_time=arrival_time,
        ))
    console.print(f"Added stop {stop_id} to trip {trip_id} (arrival: {min_to_24(arrival_time)})")

def add_trip_stop(trip_id: int, stop_id: int, time_str: str) -> None:
    """Add a trip-stop using 24-hour time format (HH:MM)."""
    try:
        hour, minute = map(int, time_str.split(":"))
        arrival_minutes = hour * 60 + minute
        if not (0 <= arrival_minutes <= 1440):
            raise ValueError
    except Exception:
        raise ValueError(f"Invalid time format: '{time_str}'. Use HH:MM in 24-hour format.")

    add_trip_stop(trip_id, stop_id, arrival_minutes)



def list_trip_stops(trip_id: int) -> list[m.TripStop]:
    """Return list of stops for a trip ordered by scheduled arrival_time."""
    with session_scope() as s:
        statement = (
            select(m.TripStop)
            .where(m.TripStop.trip_id == trip_id)
            .order_by(m.TripStop.arrival_time)
        )
        return s.scalars(statement).all()

def update_trip_stop(trip_id: int, stop_id: int, arrival_time: int) -> None:
    """Update the arrival time of a stop on a trip."""
    with session_scope() as s:
        statement = (
            update(m.TripStop)
            .where(
                m.TripStop.trip_id == trip_id,
                m.TripStop.stop_id == stop_id,
            )
            .values(arrival_time=arrival_time)
        )
        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"TripStop {trip_id}-{stop_id} not found")
    console.print(f"Updated trip-stop {trip_id}-{stop_id} to {arrival_time} minutes")

def delete_trip_stop(trip_id: int, stop_id: int) -> None:
    """Remove a stop from a trip."""
    with session_scope() as s:
        statement = delete(m.TripStop).where(
            m.TripStop.trip_id == trip_id,
            m.TripStop.stop_id == stop_id,
        )
        if s.execute(statement).rowcount == 0:
            raise NoResultFound(f"TripStop {trip_id}-{stop_id} not found")
    console.print(f"Deleted trip-stop {trip_id}-{stop_id}")