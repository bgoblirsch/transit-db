from contextlib import contextmanager
from sqlalchemy import select, text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from database import SessionLocal
import datetime
import decimal
import models as m

''' CLI Connection
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
        session.close() '''


''' !!! Database Connection for GUI !!! '''
Session = sessionmaker()

def configure_engine(engine):
    """Set the SQLAlchemy engine after login (GUI use case)."""
    Session.configure(bind=engine)


@contextmanager
def session_scope():
    session = Session()
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

def route_id_exists(route_id: int) -> bool:
    with session_scope() as s:
        return s.scalar(select(m.Route).where(m.Route.route_id == route_id)) is not None


def route_name_exists(route_name: str) -> bool:
    with session_scope() as s:
        return s.scalar(select(m.Route).where(m.Route.route_name == route_name)) is not None


def add_route(route_id: int, route_name: str, route_type: str) -> dict:
    with session_scope() as s:
        route = m.Route(route_id=route_id, route_name=route_name, route_type=route_type)
        s.add(route)
        s.flush()
        return {
            "route_id": route.route_id,
            "route_name": route.route_name,
            "route_type": route.route_type,
        }


def get_route(route_name: str) -> dict:
    with session_scope() as s:
        route = s.scalar(select(m.Route).where(m.Route.route_name == route_name))
        if not route:
            raise NoResultFound(f"Route {route_name} not found")
        return {
            "route_id": route.route_id,
            "route_name": route.route_name,
            "route_type": route.route_type,
        }


def list_routes() -> list[dict]:
    with session_scope() as s:
        routes = s.scalars(select(m.Route)).all()
        return [
            {"route_id": r.route_id, "route_name": r.route_name, "route_type": r.route_type}
            for r in routes
        ]


def update_route(route_id: int, route_name: str | None = None, route_type: str | None = None) -> dict:
    with session_scope() as s:
        route = s.get(m.Route, route_id)
        if not route:
            raise NoResultFound(f"Route {route_id} not found")

        if route_name:
            route.route_name = route_name
        if route_type:
            route.route_type = route_type

        return {
            "route_id": route.route_id,
            "route_name": route.route_name,
            "route_type": route.route_type,
        }

def delete_route(route_id: int) -> bool:
    with session_scope() as s:
        route = s.get(m.Route, route_id)
        if not route:
            raise NoResultFound(f"Route {route_id} not found")
        s.delete(route)
        return True
    
##################
## Vehicle CRUD ##
##################

def vehicle_id_exists(vehicle_id: int) -> bool:
    with session_scope() as s:
        return s.scalar(select(m.Vehicle).where(m.Vehicle.vehicle_id == vehicle_id)) is not None


def add_vehicle(vehicle_id: int, vehicle_class: str, manufacturer: str, year: int,
                vtype: str, capacity: int | None = None) -> dict:
    with session_scope() as s:
        vehicle = m.Vehicle(
            vehicle_id=vehicle_id,
            vehicle_class=vehicle_class,
            manufacturer=manufacturer,
            manufacture_year=year,
            vehicle_type=vtype,
            capacity=capacity
        )
        s.add(vehicle)
        s.flush()
        return {
            "vehicle_id": vehicle.vehicle_id,
            "vehicle_class": vehicle.vehicle_class,
            "manufacturer": vehicle.manufacturer,
            "manufacture_year": vehicle.manufacture_year,
            "vehicle_type": vehicle.vehicle_type,
            "capacity": vehicle.capacity
        }


def get_vehicle(vehicle_id: int) -> dict:
    with session_scope() as s:
        vehicle = s.get(m.Vehicle, vehicle_id)
        if not vehicle:
            raise NoResultFound(f"Vehicle {vehicle_id} not found")
        return {
            "vehicle_id": vehicle.vehicle_id,
            "vehicle_class": vehicle.vehicle_class,
            "manufacturer": vehicle.manufacturer,
            "manufacture_year": vehicle.manufacture_year,
            "vehicle_type": vehicle.vehicle_type,
            "capacity": vehicle.capacity
        }


def list_vehicles(vehicle_id: int | None = None,
                  vehicle_class: str | None = None,
                  manufacturer: str | None = None,
                  manufacture_year: tuple[str, int] | None = None,
                  vehicle_type: str | None = None,
                  capacity: tuple[str, int] | None = None) -> list[dict]:
    with session_scope() as s:
        statement = select(m.Vehicle)
        if vehicle_id is not None:
            statement = statement.where(m.Vehicle.vehicle_id == vehicle_id)
        if vehicle_class:
            statement = statement.where(m.Vehicle.vehicle_class == vehicle_class)
        if manufacturer:
            statement = statement.where(m.Vehicle.manufacturer.ilike(f"%{manufacturer}%"))
        if vehicle_type:
            statement = statement.where(m.Vehicle.vehicle_type.ilike(f"%{vehicle_type}%"))
        if manufacture_year:
            op, val = manufacture_year
            if op == "=":
                statement = statement.where(m.Vehicle.manufacture_year == val)
            elif op == "<":
                statement = statement.where(m.Vehicle.manufacture_year < val)
            elif op == ">":
                statement = statement.where(m.Vehicle.manufacture_year > val)
        if capacity:
            op, val = capacity
            if op == "=":
                statement = statement.where(m.Vehicle.capacity == val)
            elif op == "<":
                statement = statement.where(m.Vehicle.capacity < val)
            elif op == ">":
                statement = statement.where(m.Vehicle.capacity > val)

        vehicles = s.scalars(statement).all()
        return [
            {
                "vehicle_id": vehicle.vehicle_id,
                "vehicle_class": vehicle.vehicle_class,
                "manufacturer": vehicle.manufacturer,
                "manufacture_year": vehicle.manufacture_year,
                "vehicle_type": vehicle.vehicle_type,
                "capacity": vehicle.capacity
            }
            for vehicle in vehicles
        ]


def update_vehicle(vehicle_id: int, vclass: str | None = None, manufacturer: str | None = None,
                   year: int | None = None, vtype: str | None = None, capacity: int | None = None) -> dict:
    """Update a vehicle and return its updated data."""
    with session_scope() as s:
        vehicle = s.get(m.Vehicle, vehicle_id)
        if not vehicle:
            raise NoResultFound(f"Vehicle {vehicle_id} not found")

        if vclass is not None:
            vehicle.vehicle_class = vclass
        if manufacturer is not None:
            vehicle.manufacturer = manufacturer
        if year is not None:
            vehicle.manufacture_year = year
        if vtype is not None:
            vehicle.vehicle_type = vtype
        if capacity is not None:
            vehicle.capacity = capacity

        return {
            "vehicle_id": vehicle.vehicle_id,
            "vehicle_class": vehicle.vehicle_class,
            "manufacturer": vehicle.manufacturer,
            "manufacture_year": vehicle.manufacture_year,
            "vehicle_type": vehicle.vehicle_type,
            "capacity": vehicle.capacity
        }


def delete_vehicle(vehicle_id: int) -> bool:
    with session_scope() as s:
        vehicle = s.get(m.Vehicle, vehicle_id)
        if not vehicle:
            raise NoResultFound(f"Vehicle {vehicle_id} not found")
        s.delete(vehicle)
        return True

#################
## Driver CRUD ##
#################

def add_driver(driver_name: str,
               driver_classification: str,
               start_date: str | None,
               pay: float) -> dict:
    start = datetime.date.fromisoformat(start_date) if start_date else None
    pay_decimal = decimal.Decimal(str(pay))

    with session_scope() as s:
        driver = m.Driver(
            driver_name=driver_name,
            driver_classification=driver_classification,
            start_date=start,
            pay=pay_decimal
        )
        s.add(driver)
        s.flush()
        return {
            "driver_id": driver.driver_id,
            "driver_name": driver.driver_name,
            "driver_classification": driver.driver_classification,
            "start_date": driver.start_date,
            "pay": driver.pay
        }


def get_driver(driver_id: int) -> dict:
    with session_scope() as s:
        driver = s.get(m.Driver, driver_id)
        if not driver:
            raise NoResultFound(f"Driver {driver_id} not found")
        return {
            "driver_id": driver.driver_id,
            "driver_name": driver.driver_name,
            "driver_classification": driver.driver_classification,
            "start_date": driver.start_date,
            "pay": driver.pay
        }


def list_drivers() -> list[dict]:
    with session_scope() as s:
        drivers = s.scalars(select(m.Driver)).all()
        return [
            {
                "driver_id": driver.driver_id,
                "driver_name": driver.driver_name,
                "driver_classification": driver.driver_classification,
                "start_date": driver.start_date,
                "pay": driver.pay
            }
            for driver in drivers
        ]


def update_driver(driver_id: int,
                  driver_name: str | None = None,
                  driver_classification: str | None = None,
                  start_date: str | None = None,
                  pay: float | None = None) -> dict:
    with session_scope() as s:
        driver = s.get(m.Driver, driver_id)
        if not driver:
            raise NoResultFound(f"Driver {driver_id} not found")
        if driver_name is not None:
            driver.driver_name = driver_name
        if driver_classification is not None:
            driver.driver_classification = driver_classification
        if start_date is not None:
            driver.start_date = datetime.date.fromisoformat(start_date)
        if pay is not None:
            driver.pay = decimal.Decimal(str(pay))
        return {
            "driver_id": driver.driver_id,
            "driver_name": driver.driver_name,
            "driver_classification": driver.driver_classification,
            "start_date": driver.start_date,
            "pay": driver.pay
        }


def delete_driver(driver_id: int) -> bool:
    with session_scope() as s:
        driver = s.get(m.Driver, driver_id)
        if not driver:
            raise NoResultFound(f"Driver {driver_id} not found")
        s.delete(driver)
        return True

######################
## Maintenance CRUD ##
######################

def add_maintenance(vehicle_id: int, work_date: str, work_performed: str) -> dict:
    date_obj = datetime.date.fromisoformat(work_date)
    with session_scope() as s:
        vehicle = s.get(m.Vehicle, vehicle_id)
        if not vehicle:
            raise NoResultFound(f"Vehicle {vehicle_id} does not exist.")
        maint = m.Maintenance(
            vehicle_id=vehicle_id,
            work_date=date_obj,
            work_performed=work_performed,
        )
        s.add(maint)
        s.flush()
        return {
            "maintenance_id": maint.maintenance_id,
            "vehicle_id": maint.vehicle_id,
            "work_date": maint.work_date,
            "work_performed": maint.work_performed
        }

def get_maintenance(maintenance_id: int) -> dict:
    with session_scope() as s:
        maint = s.get(m.Maintenance, maintenance_id)
        if not maint:
            raise NoResultFound(f"Maintenance {maintenance_id} not found")
        return {
            "maintenance_id": maint.maintenance_id,
            "vehicle_id": maint.vehicle_id,
            "work_date": maint.work_date,
            "work_performed": maint.work_performed
        }

def list_maintenance(vehicle_id: int | None = None, work_date: str | None = None) -> list[dict]:
    with session_scope() as s:
        stmt = select(m.Maintenance)
        if vehicle_id is not None:
            stmt = stmt.where(m.Maintenance.vehicle_id == vehicle_id)
        if work_date:
            stmt = stmt.where(m.Maintenance.work_date == datetime.date.fromisoformat(work_date))
        records = s.scalars(stmt).all()
        return [
            {
                "maintenance_id": record.maintenance_id,
                "vehicle_id": record.vehicle_id,
                "work_date": record.work_date,
                "work_performed": record.work_performed
            } for record in records
        ]

def update_maintenance(maintenance_id: int, vehicle_id: int | None = None,
                       work_date: str | None = None, work_performed: str | None = None) -> dict:
    with session_scope() as s:
        maint = s.get(m.Maintenance, maintenance_id)
        if not maint:
            raise NoResultFound(f"Maintenance {maintenance_id} not found")
        if vehicle_id is not None:
            maint.vehicle_id = vehicle_id
        if work_date is not None:
            maint.work_date = datetime.date.fromisoformat(work_date)
        if work_performed is not None:
            maint.work_performed = work_performed
        return {
            "maintenance_id": maint.maintenance_id,
            "vehicle_id": maint.vehicle_id,
            "work_date": maint.work_date,
            "work_performed": maint.work_performed
        }

def delete_maintenance(maintenance_id: int) -> bool:
    with session_scope() as s:
        maint = s.get(m.Maintenance, maintenance_id)
        if not maint:
            raise NoResultFound(f"Maintenance {maintenance_id} not found")
        s.delete(maint)
        return True


###############
## Stop CRUD ##
###############

def add_stop(stop_id: int,
             stop_direction: str,
             street_name: str,
             cross_street: str,
             latitude: float | None = None,
             longitude: float | None = None) -> dict:
    with session_scope() as s:
        stop = m.Stop(
            stop_id=stop_id,
            stop_direction=stop_direction,
            street_name=street_name,
            cross_street=cross_street,
            latitude=latitude,
            longitude=longitude,
        )
        s.add(stop)
        s.flush()
        return {
            "stop_id": stop.stop_id,
            "stop_direction": stop.stop_direction,
            "street_name": stop.street_name,
            "cross_street": stop.cross_street,
            "latitude": stop.latitude,
            "longitude": stop.longitude
        }

def get_stop(stop_id: int) -> dict:
    with session_scope() as s:
        stop = s.get(m.Stop, stop_id)
        if not stop:
            raise NoResultFound(f"Stop {stop_id} not found")
        return {
            "stop_id": stop.stop_id,
            "stop_direction": stop.stop_direction,
            "street_name": stop.street_name,
            "cross_street": stop.cross_street,
            "latitude": stop.latitude,
            "longitude": stop.longitude
        }

def list_stops(stop_id: int | None = None,
               stop_direction: str | None = None,
               street_name: str | None = None) -> list[dict]:
    with session_scope() as s:
        statement = select(m.Stop)
        if stop_id is not None:
            statement = statement.where(m.Stop.stop_id == stop_id)
        if stop_direction:
            statement = statement.where(m.Stop.stop_direction == stop_direction)
        if street_name:
            statement = statement.where(m.Stop.street_name.ilike(f"%{street_name}%"))
        stops = s.scalars(statement).all()
        return [
            {
                "stop_id": stop.stop_id,
                "stop_direction": stop.stop_direction,
                "street_name": stop.street_name,
                "cross_street": stop.cross_street,
                "latitude": stop.latitude,
                "longitude": stop.longitude
            }
            for stop in stops
        ]

def update_stop(stop_id: int,
                stop_direction: str | None = None,
                street_name: str | None = None,
                cross_street: str | None = None,
                latitude: float | None = None,
                longitude: float | None = None) -> dict:
    with session_scope() as s:
        stop = s.get(m.Stop, stop_id)
        if not stop:
            raise NoResultFound(f"Stop {stop_id} not found")
        if stop_direction: stop.stop_direction = stop_direction
        if street_name: stop.street_name = street_name
        if cross_street: stop.cross_street = cross_street
        if latitude is not None: stop.latitude = latitude
        if longitude is not None: stop.longitude = longitude
        return {
            "stop_id": stop.stop_id,
            "stop_direction": stop.stop_direction,
            "street_name": stop.street_name,
            "cross_street": stop.cross_street,
            "latitude": stop.latitude,
            "longitude": stop.longitude
        }

def delete_stop(stop_id: int) -> bool:
    with session_scope() as s:
        stop = s.get(m.Stop, stop_id)
        if not stop:
            raise NoResultFound(f"Stop {stop_id} not found")
        s.delete(stop)
        return True

###############
## Trip CRUD ##
###############

def add_trip(trip_id: int,
             route_id: int,
             driver_id: int,
             vehicle_id: int,
             trip_date: str,
             trip_direction: str) -> dict:
    date_obj = datetime.date.fromisoformat(trip_date)
    with session_scope() as s:
        trip = m.Trip(
            trip_id=trip_id,
            route_id=route_id,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            trip_date=date_obj,
            trip_direction=trip_direction,
        )
        s.add(trip)
        s.flush()
        return {
            "trip_id": trip.trip_id,
            "route_id": trip.route_id,
            "driver_id": trip.driver_id,
            "vehicle_id": trip.vehicle_id,
            "trip_date": trip.trip_date,
            "trip_direction": trip.trip_direction,
        }


def get_trip(trip_id: int) -> dict:
    with session_scope() as s:
        trip = (
            s.query(m.Trip, m.Route, m.Driver)
            .join(m.Route, m.Trip.route_id == m.Route.route_id)
            .join(m.Driver, m.Trip.driver_id == m.Driver.driver_id)
            .filter(m.Trip.trip_id == trip_id)
            .first()
        )
        if not trip:
            raise NoResultFound(f"Trip {trip_id} not found")

        t, route, driver = trip
        return {
            "trip_id": t.trip_id,
            "trip_date": t.trip_date,
            "trip_direction": t.trip_direction,
            "route_id": route.route_id,
            "route_name": route.route_name,
            "driver_id": driver.driver_id,
            "driver_name": driver.driver_name,
            "vehicle_id": t.vehicle_id,
        }


def list_trips(trip_id: int | None = None,
               route_id: int | None = None,
               route_name: str | None = None,
               driver_id: int | None = None,
               driver_name: str | None = None,
               vehicle_id: int | None = None,
               trip_date: str | None = None) -> list[dict]:
    with session_scope() as s:
        statement = (
            select(
                m.Trip.trip_id,
                m.Trip.trip_date,
                m.Trip.trip_direction,
                m.Route.route_id,
                m.Route.route_name,
                m.Driver.driver_id,
                m.Driver.driver_name,
                m.Trip.vehicle_id,
            )
            .join(m.Route, m.Trip.route_id == m.Route.route_id)
            .join(m.Driver, m.Trip.driver_id == m.Driver.driver_id)
        )

        if trip_id is not None:
            statement = statement.where(m.Trip.trip_id == trip_id)
        if route_id is not None:
            statement = statement.where(m.Trip.route_id == route_id)
        if route_name:
            statement = statement.where(m.Route.route_name.ilike(f"%{route_name}%"))
        if driver_id is not None:
            statement = statement.where(m.Trip.driver_id == driver_id)
        if driver_name:
            statement = statement.where(m.Driver.driver_name.ilike(f"%{driver_name}%"))
        if vehicle_id is not None:
            statement = statement.where(m.Trip.vehicle_id == vehicle_id)
        if trip_date:
            statement = statement.where(m.Trip.trip_date == datetime.date.fromisoformat(trip_date))

        rows = s.execute(statement).all()
        return [
            {
                "trip_id": row.trip_id,
                "trip_date": row.trip_date,
                "trip_direction": row.trip_direction,
                "route_id": row.route_id,
                "route_name": row.route_name,
                "driver_id": row.driver_id,
                "driver_name": row.driver_name,
                "vehicle_id": row.vehicle_id,
            }
            for row in rows
        ]


def update_trip(trip_id: int,
                route_id: int | None = None,
                driver_id: int | None = None,
                vehicle_id: int | None = None,
                trip_date: str | None = None,
                trip_direction: str | None = None) -> dict:
    with session_scope() as s:
        trip = s.get(m.Trip, trip_id)
        if not trip:
            raise NoResultFound(f"Trip {trip_id} not found")

        if route_id is not None:
            trip.route_id = route_id
        if driver_id is not None:
            trip.driver_id = driver_id
        if vehicle_id is not None:
            trip.vehicle_id = vehicle_id
        if trip_date is not None:
            trip.trip_date = datetime.date.fromisoformat(trip_date)
        if trip_direction is not None:
            trip.trip_direction = trip_direction

        return {
            "trip_id": trip.trip_id,
            "route_id": trip.route_id,
            "driver_id": trip.driver_id,
            "vehicle_id": trip.vehicle_id,
            "trip_date": trip.trip_date,
            "trip_direction": trip.trip_direction,
        }


def delete_trip(trip_id: int) -> bool:
    """Delete a trip by ID."""
    with session_scope() as s:
        trip = s.get(m.Trip, trip_id)
        if not trip:
            raise NoResultFound(f"Trip {trip_id} not found")
        s.delete(trip)
        return True

#######################
## Routes-Stops CRUD ##
#######################

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
    return {
        "route_id": route_id,
        "stop_id": stop_id,
        "route_direction": route_direction,
        "stop_order": stop_order
    }

def list_route_stop(route_id: int = None, route_direction: str = None) -> list[m.RouteStop]:
    """Return list of stops for a route in a given direction, ordered."""
    with session_scope() as s:
        statement = (
            select(
                m.RouteStop.route_id,
                m.RouteStop.stop_id,
                m.RouteStop.route_direction,
                m.RouteStop.stop_order,
                m.Route.route_name,
                m.Stop.cross_street
            )
            .join(m.Route, m.Route.route_id == m.RouteStop.route_id)
            .join(m.Stop, m.Stop.stop_id == m.RouteStop.stop_id)
        )

        if route_id:
            statement = statement.where(m.RouteStop.route_id == route_id)
        if route_direction:
            statement = statement.where(m.RouteStop.route_direction == route_direction)

        rows = s.execute(statement).all()
        return [
            {
                "route_id": row.route_id,
                "route_name": row.route_name,
                "route_direction": row.route_direction,
                "stop_id": row.stop_id,
                "cross_street": row.cross_street,
                "stop_order": row.stop_order
            }
            for row in rows
        ]

def update_route_stop(route_id: int,
                      stop_id: int,
                      route_direction: str | None = None,
                      stop_order: int | None = None) -> None:
    """Update the stop order for a route-stop entry."""
    with session_scope() as s:
        route_stop = s.get(m.RouteStop, (route_id, stop_id, route_direction))
        if not route_stop:
            raise NoResultFound(f"Route ID {route_id} & Stop ID {stop_id} not found for direction {route_direction}.")
        
        if route_id: route_stop.route_id = route_id
        if stop_id: route_stop.stop_id = stop_id
        if route_direction: route_stop.route_direction = route_direction
        if stop_order: route_stop.stop_order = stop_order

        return {
            "route_id": route_stop.route_id,
            "stop_id": route_stop.stop_id,
            "route_direction": route_stop.route_direction,
            "stop_order": route_stop.stop_order
        }
    
def delete_route_stop(route_id: int, stop_id: int, route_direction: str) -> None:
    """Remove a stop from a route."""
    with session_scope() as s:
        route_stop = s.get(m.RouteStop, (route_id, stop_id, route_direction))
        if not route_stop:
            raise NoResultFound(f"Route ID {route_id} & Stop ID {stop_id} not found for direction {route_direction}.")
        s.delete(route_stop)
        return True
    
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

def add_trip_stop_minutes(trip_id: int, stop_id: int, arrival_time: int) -> dict:
    """Add a trip-stop using raw minutes format."""
    with session_scope() as s:
        trip_stop = m.TripStop(
            trip_id=trip_id,
            stop_id=stop_id,
            arrival_time=arrival_time,
        )
        s.add(trip_stop)
        s.flush()  # ensures PKs and relationships are populated

        return {
            "trip_id": trip_stop.trip_id,
            "stop_id": trip_stop.stop_id,
            "arrival_time": trip_stop.arrival_time,
            "arrival_hhmm": min_to_24(trip_stop.arrival_time),
        }

def add_trip_stop(trip_id: int, stop_id: int, time_str: str) -> dict:
    """Add a trip-stop using 24-hour time format (HH:MM)."""
    try:
        hour, minute = map(int, time_str.split(":"))
        arrival_minutes = hour * 60 + minute
        if not (0 <= arrival_minutes <= 1440):
            raise ValueError
    except Exception:
        raise ValueError(f"Invalid time format: '{time_str}'. Use HH:MM in 24-hour format.")

    return add_trip_stop_minutes(trip_id, stop_id, arrival_minutes)

def list_trip_stop(trip_id: int | None = None) -> list[dict]:
    """Return list of stops for a trip ordered by scheduled arrival_time."""
    with session_scope() as s:
        statement = (
            select(m.TripStop, 
                           m.Route.route_name,
                           m.Trip.trip_direction,
                           m.Stop.street_name, 
                           m.Stop.cross_street)
            .select_from(m.TripStop)
            .join(m.Trip, m.TripStop.trip_id == m.Trip.trip_id)
            .join(m.Route, m.Trip.route_id == m.Route.route_id)
            .join(m.Stop, m.TripStop.stop_id == m.Stop.stop_id)
        )
        if trip_id is not None:
            statement = statement.where(m.TripStop.trip_id == trip_id) 
        statement = statement.order_by(m.TripStop.trip_id, m.TripStop.arrival_time)
        trip_stops = s.execute(statement).mappings().all()
        #trip_stops = s.scalars(statement).all()

        result = []

        for row in trip_stops:
            tripStop = row[m.TripStop]
            result.append({
                "trip_id": tripStop.trip_id,
                "stop_id": tripStop.stop_id,
                "arrival_time": tripStop.arrival_time,
                "arrival_hhmm": min_to_24(tripStop.arrival_time),
                "route_name": row["route_name"],
                "trip_direction": row["trip_direction"],
                "street_name": row["street_name"],
                "cross_street": row["cross_street"],
            })

        return result

def update_trip_stop(trip_id: int, stop_id: int, arrival_time: int) -> dict:
    """Update the arrival time of a stop on a trip."""
    with session_scope() as s:
        trip_stop = s.get(m.TripStop, (trip_id, stop_id))
        if not trip_stop:
            raise NoResultFound(f"TripStop {trip_id}-{stop_id} not found")

        trip_stop.arrival_time = arrival_time
        s.flush()

        return {
            "trip_id": trip_stop.trip_id,
            "stop_id": trip_stop.stop_id,
            "arrival_time": trip_stop.arrival_time,
            "arrival_hhmm": min_to_24(trip_stop.arrival_time),
        }

def delete_trip_stop(trip_id: int, stop_id: int) -> dict:
    """Remove a stop from a trip."""
    with session_scope() as s:
        trip_stop = s.get(m.TripStop, (trip_id, stop_id))
        if not trip_stop:
            raise NoResultFound(f"TripStop {trip_id}-{stop_id} not found")
        s.delete(trip_stop)
        return True
    
########################
## Analysis Functions ##
########################

# Set Operation example
def get_shared_stops(route_a: int, route_b: int) -> list[int]:
    with session_scope() as s:
        query = text("""
            SELECT s.stop_id, s.street_name, s.cross_street, s.latitude, s.longitude
            FROM stop s
            WHERE s.stop_id IN (
                SELECT stop_id FROM route_stop WHERE route_id = :a
                INTERSECT
                SELECT stop_id FROM route_stop WHERE route_id = :b
            )
        """)
        result = s.execute(query, {"a": route_a, "b": route_b}).mappings()
        return list(result)

# Simple Aggregate function example
def get_all_shared_stops() -> list[int]:
    with session_scope() as s:
        query = text("""
            SELECT s.stop_id, s.street_name, s.cross_street, s.latitude, s.longitude
            FROM stop s
            JOIN (
                SELECT stop_id
                FROM route_stop
                GROUP BY stop_id
                HAVING COUNT(DISTINCT route_id) > 1
            ) AS shared ON shared.stop_id = s.stop_id
        """)
        result = s.execute(query).mappings()
        return list(result)

# Set Membership example
def get_available_drivers(date: str) -> list[dict]:
    with session_scope() as s:
        query = text("""
            SELECT driver_id, driver_name, driver_classification, pay
            FROM driver
            WHERE driver_id NOT IN (
                SELECT driver_id FROM trip WHERE trip_date = :date
            )
        """)
        result = s.execute(query, {"date": date}).mappings()
        return list(result)
    
# WITH clause subquery
def get_vehicle_trip_counts() -> list[dict]:
    with session_scope() as s:
        query = text("""
            WITH trip_counts AS (
                SELECT vehicle_id, COUNT(*) AS trip_count
                FROM trip
                GROUP BY vehicle_id
            )
            SELECT v.vehicle_id, v.vehicle_class, v.manufacturer, v.manufacture_year, v.vehicle_type, v.capacity, tc.trip_count
            FROM trip_counts tc
            JOIN vehicle v ON v.vehicle_id = tc.vehicle_id
            ORDER BY tc.trip_count DESC;
        """)
        result = s.execute(query).mappings()
        return list(result)
    
# OLAP Advanced aggregate function example - dense_rank
def get_driver_trip_ranks() -> list[dict]:
    with session_scope() as s:
        query = text("""
            SELECT *
            FROM (
                SELECT
                    d.driver_id,
                    d.driver_name,
                    COUNT(t.trip_id) AS trip_count,
                    DENSE_RANK() OVER (ORDER BY COUNT(t.trip_id) DESC) AS trip_rank
                FROM driver d
                LEFT JOIN trip t ON d.driver_id = t.driver_id
                GROUP BY d.driver_id, d.driver_name
            ) AS ranked
            ORDER BY trip_rank;
        """)
        result = s.execute(query).mappings()
        return list(result)
    
# OLAP advanced aggregate function example - average time between maintenance
def get_avg_days_between_maintenance() -> list[dict]:
    with session_scope() as s:
        query = text("""
            WITH dated AS (
                SELECT
                    vehicle_id,
                    work_date,
                    LAG(work_date) OVER (PARTITION BY vehicle_id ORDER BY work_date) AS prev_date
                FROM maintenance
            )
            SELECT
                vehicle_id,
                ROUND(AVG(DATEDIFF(work_date, prev_date)), 1) AS avg_days_between
            FROM dated
            WHERE prev_date IS NOT NULL
            GROUP BY vehicle_id
            ORDER BY avg_days_between;
        """)
        result = s.execute(query).mappings()
        return list(result)
    
