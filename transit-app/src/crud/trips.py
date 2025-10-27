from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from src.database import session_scope
import src.models as m
import datetime

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