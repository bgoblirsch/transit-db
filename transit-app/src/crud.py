from contextlib import contextmanager
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select, text
import models as m

Session = sessionmaker()

def configure_engine(engine):
    """Set the SQLAlchemy engine after login."""
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
    """Insert a new route."""
    with session_scope() as s:
        route = m.Route(route_id=route_id, route_name=route_name, route_type=route_type)
        s.add(route)
        s.flush()
        return {"route_id": route.route_id, "route_name": route.route_name, "route_type": route.route_type}

def get_route(route_name: str) -> dict:
    """Fetch a single route by name."""
    with session_scope() as s:
        route = s.scalar(select(m.Route).where(m.Route.route_name == route_name))
        if not route:
            raise NoResultFound(f"Route {route_name} not found")

        return {
            "route_id": route.route_id,
            "route_name": route.route_name,
            "route_type": route.route_type
        }

def list_routes() -> list[dict]:
    """List all routes."""
    with session_scope() as s:
        routes = s.scalars(select(m.Route)).all()
        return [
            {"route_id": record.route_id, "route_name": record.route_name, "route_type": record.route_type}
            for record in routes
        ]

def update_route(route_id: int, route_name: str | None = None, route_type: str | None = None) -> dict:
    """Update a route's information."""
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
            "route_type": route.route_type
        }

def delete_route(route_id: int) -> bool:
    """Delete a route by ID."""
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

def add_vehicle(vehicle_id: int, vehicle_class: str, manufacturer: str, year: int, vtype: str, capacity: int | None = None) -> dict:
    """Insert a new vehicle."""
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
    """Fetch a single vehicle by ID."""
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
                  capacity: tuple[str, int] | None = None  ) -> list[dict]:
    """List all vehicles. Optionally filter by ID, vehicle class, or manufacturer."""
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
            operation, val = manufacture_year
            if operation == '=':
                statement = statement.where(m.Vehicle.manufacture_year == val)
            elif operation == '<':
                statement = statement.where(m.Vehicle.manufacture_year < val)
            elif operation == '>':
                statement = statement.where(m.Vehicle.manufacture_year > val)
        if capacity:
            operation, val = capacity
            if operation == '=':
                statement = statement.where(m.Vehicle.capacity == val)
            elif operation == '<':
                statement = statement.where(m.Vehicle.capacity < val)
            elif operation == '>':
                statement = statement.where(m.Vehicle.capacity > val)
        vehicles = s.scalars(statement).all()
        return [
            {
                "vehicle_id": record.vehicle_id,
                "vehicle_class": record.vehicle_class,
                "manufacturer": record.manufacturer,
                "manufacture_year": record.manufacture_year,
                "vehicle_type": record.vehicle_type,
                "capacity": record.capacity
            }
            for record in vehicles
        ]

def update_vehicle(vehicle_id: int, vclass: str | None = None, manufacturer: str | None = None,
                   year: int | None = None, vtype: str | None = None, capacity: int | None = None) -> dict:
    """Update a vehicle's information."""
    with session_scope() as s:
        vehicle = s.get(m.Vehicle, vehicle_id)
        if not vehicle:
            raise NoResultFound(f"Vehicle {vehicle_id} not found")
        if vclass:
            vehicle.vehicle_class = vclass
        if manufacturer:
            vehicle.manufacturer = manufacturer
        if year is not None:
            vehicle.manufacture_year = year
        if vtype:
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
    """Delete a vehicle by ID."""
    with session_scope() as s:
        vehicle = s.get(m.Vehicle, vehicle_id)
        if not vehicle:
            raise NoResultFound(f"Vehicle {vehicle_id} not found")

        s.delete(vehicle)
        return True

#################
## Driver CRUD ##
#################

def add_driver(driver_name: str, driver_classification: str, start_date: str, pay: float) -> dict:
    """Insert a new driver."""
    with session_scope() as s:
        driver = m.Driver(
            driver_name=driver_name,
            driver_classification=driver_classification,
            start_date=start_date,
            pay=pay
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
    """Fetch a single driver by ID."""
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
    """List all drivers."""
    with session_scope() as s:
        drivers = s.scalars(select(m.Driver)).all()
        return [
            {
                "driver_id": record.driver_id,
                "driver_name": record.driver_name,
                "driver_classification": record.driver_classification,
                "start_date": record.start_date,
                "pay": record.pay
            }
            for record in drivers
        ]

def update_driver(driver_id: int, driver_name: str | None = None, driver_classification: str | None = None, start_date: str | None = None, pay: float | None = None) -> dict:
    """Update a driver's information."""
    with session_scope() as s:
        driver = s.get(m.Driver, driver_id)
        if not driver:
            raise NoResultFound(f"Driver {driver_id} not found")
        if driver_name:
            driver.driver_name = driver_name
        if driver_classification:
            driver.driver_classification = driver_classification
        if start_date:
            driver.start_date = start_date
        if pay is not None:
            driver.pay = pay
        return {
            "driver_id": driver.driver_id,
            "driver_name": driver.driver_name,
            "driver_classification": driver.driver_classification,
            "start_date": driver.start_date,
            "pay": driver.pay
        }

def delete_driver(driver_id: int) -> bool:
    """Delete a driver by ID."""
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
    """Add a new maintenance record."""
    date_obj = datetime.date.fromisoformat(work_date)
    with session_scope() as s:
        vehicle = s.get(m.Vehicle, vehicle_id)
        if not vehicle:
            raise NoResultFound(f"Vehicle {vehicle_id} does not exist.")
        mnt = m.Maintenance(
            vehicle_id=vehicle_id,
            work_date=date_obj,
            work_performed=work_performed,
        )
        s.add(mnt)
        s.flush()
        return {
            "maintenance_id": mnt.maintenance_id,
            "vehicle_id": mnt.vehicle_id,
            "work_date": mnt.work_date,
            "work_performed": mnt.work_performed
        }

def get_maintenance(maintenance_id: int) -> dict:
    """Fetch a maintenance record by ID."""
    with session_scope() as s:
        record = s.get(m.Maintenance, maintenance_id)
        if not record:
            raise NoResultFound(f"Maintenance {maintenance_id} not found")
        return {
            "maintenance_id": record.maintenance_id,
            "vehicle_id": record.vehicle_id,
            "work_date": record.work_date,
            "work_performed": record.work_performed
        }

def list_maintenance(
    vehicle_id: int | None = None,
    work_date: str | None = None) -> list[dict]:
    """List all maintenance records. Optionally filter by vehicle ID and exact work date."""
    with session_scope() as s:
        statement = select(m.Maintenance)
        if vehicle_id is not None:
            statement = statement.where(m.Maintenance.vehicle_id == vehicle_id)
        if work_date:
            statement = statement.where(m.Maintenance.work_date == work_date)
        records = s.scalars(statement).all()
        return [
            {
                "maintenance_id": record.maintenance_id,
                "vehicle_id": record.vehicle_id,
                "work_date": record.work_date,
                "work_performed": record.work_performed
            }
            for record in records
        ]

def update_maintenance(maintenance_id: int,
                       vehicle_id: int | None = None,
                       work_date: str | None = None,
                       work_performed: str | None = None) -> dict:
    """Update a maintenance record."""
    with session_scope() as s:
        mnt = s.get(m.Maintenance, maintenance_id)
        if not mnt:
            raise NoResultFound(f"Maintenance {maintenance_id} not found")

        if vehicle_id is not None:
            mnt.vehicle_id = vehicle_id
        if work_date is not None:
            mnt.work_date = datetime.date.fromisoformat(work_date)
        if work_performed is not None:
            mnt.work_performed = work_performed

        return {
            "maintenance_id": mnt.maintenance_id,
            "vehicle_id": mnt.vehicle_id,
            "work_date": mnt.work_date,
            "work_performed": mnt.work_performed
        }

def delete_maintenance(maintenance_id: int) -> bool:
    """Delete a maintenance record."""
    with session_scope() as s:
        mnt = s.get(m.Maintenance, maintenance_id)
        if not mnt:
            raise NoResultFound(f"Maintenance {maintenance_id} not found")
        s.delete(mnt)
        return True

###############
## Stop CRUD ##
###############

def add_stop(stop_id: int, stop_direction: str, street_name: str, cross_street: str,
             latitude: float | None = None, longitude: float | None = None) -> dict:
    """Insert a new stop."""
    with session_scope() as s:
        stop = m.Stop(
            stop_id=stop_id,
            stop_direction=stop_direction,
            street_name=street_name,
            cross_street=cross_street,
            latitude=latitude,
            longitude=longitude
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
    """Fetch a stop by ID."""
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
    
def list_stops(
    stop_id: int | None = None,
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
                "stop_id": record.stop_id,
                "stop_direction": record.stop_direction,
                "street_name": record.street_name,
                "cross_street": record.cross_street,
                "latitude": record.latitude,
                "longitude": record.longitude
            }
            for record in stops
        ]

def update_stop(stop_id: int,
                stop_direction: str | None = None,
                street_name: str | None = None,
                cross_street: str | None = None,
                latitude: float | None = None,
                longitude: float | None = None) -> dict:
    """Update stop information."""
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
    """Delete a stop."""
    with session_scope() as s:
        stop = s.get(m.Stop, stop_id)
        if not stop:
            raise NoResultFound(f"Stop {stop_id} not found")
        s.delete(stop)
        return True

###############
## Trip CRUD ##
###############

def add_trip(trip_id:int, 
             route_id: int, 
             driver_id: int, 
             vehicle_id: int, 
             trip_date: str, 
             trip_direction: str) -> dict:
    """Insert a new trip."""
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
            "trip_direction": trip.trip_direction
        }

def list_trips(
    trip_id: int | None = None,
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
                m.Trip.vehicle_id
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
            statement = statement.where(m.Trip.trip_date == trip_date)

        rows = s.execute(statement).all()

        return [
            {
                "trip_id": record.trip_id,
                "trip_date": record.trip_date,
                "trip_direction": record.trip_direction,
                "route_id": record.route_id,
                "route_name": record.route_name,
                "driver_id": record.driver_id,
                "driver_name": record.driver_name,
                "vehicle_id": record.vehicle_id
            }
            for record in rows
        ]

def update_trip(trip_id: int,
                route_id: int | None = None,
                driver_id: int | None = None,
                vehicle_id: int | None = None,
                trip_date: str | None = None,
                trip_direction: str | None = None) -> dict:
    """Update a trip's information."""
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
            "trip_direction": trip.trip_direction
        }

def delete_trip(trip_id: int) -> bool:
    """Delete a trip by ID."""
    with session_scope() as s:
        trip = s.get(m.Trip, trip_id)
        if not trip:
            raise NoResultFound(f"Trip {trip_id} not found")

        s.delete(trip)
        return True



#####################
## Route-Stop CRUD ##
#####################

def add_route_stop(route_id: int, stop_id: int, route_direction: str, stop_order: int) -> dict:
    """Insert a route-stop association."""
    with session_scope() as s:
        link = m.RouteStop(route_id=route_id, stop_id=stop_id, route_direction=route_direction, stop_order=stop_order)
        s.add(link)
        s.flush()
        return {
            "route_id": link.route_id,
            "stop_id": link.stop_id,
            "route_direction": link.route_direction,
            "stop_order": link.stop_order
        }

def list_route_stops(route_id: int | None = None,
                     route_name: str | None = None,
                     route_direction: str | None = None) -> list[dict]:
    with session_scope() as s:
        statement = (
            select(
                m.RouteStop.route_id,
                m.Route.route_name,
                m.RouteStop.route_direction,
                m.RouteStop.stop_id,
                m.Stop.cross_street,
                m.RouteStop.stop_order
            )
            .join(m.Route, m.RouteStop.route_id == m.Route.route_id)
            .join(m.Stop, m.RouteStop.stop_id == m.Stop.stop_id)
            .order_by(
                m.RouteStop.route_id,
                m.RouteStop.route_direction,
                m.RouteStop.stop_order
            )
        )
        if route_id is not None:
            statement = statement.where(m.RouteStop.route_id == route_id)
        if route_direction:
            statement = statement.where(m.RouteStop.route_direction == route_direction)
        if route_name:
            statement = statement.where(m.Route.route_name.ilike(f"%{route_name}%"))
        results = s.execute(statement).all()
        return [
            {
                "route_id": record.route_id,
                "route_name": record.route_name,
                "route_direction": record.route_direction,
                "stop_id": record.stop_id,
                "cross_street": record.cross_street,
                "stop_order": record.stop_order
            }
            for record in results
        ]

def update_route_stop(route_id: int, old_stop_id: int, new_stop_id: int) -> dict:
    """Update a stop in a route-stop association."""
    with session_scope() as s:
        link = s.scalar(
            select(m.RouteStop).where(
                (m.RouteStop.route_id == route_id) & (m.RouteStop.stop_id == old_stop_id)
            )
        )
        if not link:
            raise NoResultFound("Route-Stop association not found")

        link.stop_id = new_stop_id
        return {
            "route_id": link.route_id,
            "stop_id": link.stop_id
        }
    
def delete_route_stop(route_id: int, stop_id: int) -> bool:
    """Delete a route-stop association."""
    with session_scope() as s:
        link = s.scalar(
            select(m.RouteStop).where(
                (m.RouteStop.route_id == route_id) & (m.RouteStop.stop_id == stop_id)
            )
        )
        if not link:
            raise NoResultFound("Route-Stop association not found")

        s.delete(link)
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

def add_trip_stop_minutes(trip_id: int, stop_id: int, arrival_time: int) -> None:
    """Add a trip-stop using raw minutes format."""
    with session_scope() as s:
        s.add(m.TripStop(
            trip_id=trip_id,
            stop_id=stop_id,
            arrival_time=arrival_time,
        ))

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

def list_timetable(
    route_name: str | None = None,
    trip_direction: str | None = None
) -> list[dict]:
    with session_scope() as s:
        statement = select(m.Timetable)
        if route_name:
            statement = statement.where(m.Timetable.route_name.ilike(f"%{route_name}%"))
        if trip_direction:
            statement = statement.where(m.Timetable.trip_direction == trip_direction)
        records = s.scalars(statement).all()
        return [
            {
                "route_name": record.route_name,
                "trip_direction": record.trip_direction,
                "street_name": record.street_name,
                "cross_street": record.cross_street,
                "arrival_time": min_to_24(record.arrival_time)
            }
            for record in records
        ]

def list_trip_stops(trip_id: int) -> list[dict]:
    """List all stops for a specific trip."""
    with session_scope() as s:
        stops = s.scalars(select(m.TripStop).where(m.TripStop.trip_id == trip_id)).all()
        return [
            {
                "route_id": record.trip_id,
                "stop_id": record.stop_id,
                "arrival_time": record.arrival_time
            }
            for record in stops
        ]

def update_trip_stop(trip_id: int, stop_id: int, stop_time: str) -> dict:
    """Update stop time for a trip-stop association."""
    with session_scope() as s:
        link = s.scalar(
            select(m.TripStop).where(
                (m.TripStop.trip_id == trip_id) & (m.TripStop.stop_id == stop_id)
            )
        )
        if not link:
            raise NoResultFound("Trip-Stop association not found")

        link.stop_time = stop_time
        return {
            "trip_id": link.trip_id,
            "stop_id": link.stop_id,
            "stop_time": link.stop_time
        }

def delete_trip_stop(trip_id: int, stop_id: int) -> bool:
    """Delete a trip-stop association."""
    with session_scope() as s:
        link = s.scalar(
            select(m.TripStop).where(
                (m.TripStop.trip_id == trip_id) & (m.TripStop.stop_id == stop_id)
            )
        )
        if not link:
            raise NoResultFound("Trip-Stop association not found")

        s.delete(link)
        return True

###################
## Analysis CRUD ##
###################

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
    
