from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from src.database import session_scope
import src.models as m
import src.utils.utils as utils

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
            "arrival_hhmm": utils.min_to_24(trip_stop.arrival_time),
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

def list_trip_stop(trip_id: int | None = None,
                   route_name: str | None = None,
                   direction: str | None = None) -> list[dict]:
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
        if route_name is not None:
            statement = statement.where(m.Route.route_name == route_name)
        statement = statement.order_by(m.Route.route_name, m.Trip.trip_direction, m.TripStop.arrival_time)
        trip_stops = s.execute(statement).mappings().all()

        result = []

        for row in trip_stops:
            tripStop = row[m.TripStop]
            result.append({
                "trip_id": tripStop.trip_id,
                "stop_id": tripStop.stop_id,
                "arrival_time": tripStop.arrival_time,
                "arrival_hhmm": utils.min_to_24(tripStop.arrival_time),
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
            "arrival_hhmm": utils.min_to_24(trip_stop.arrival_time),
        }

def delete_trip_stop(trip_id: int, stop_id: int) -> dict:
    """Remove a stop from a trip."""
    with session_scope() as s:
        trip_stop = s.get(m.TripStop, (trip_id, stop_id))
        if not trip_stop:
            raise NoResultFound(f"TripStop {trip_id}-{stop_id} not found")
        s.delete(trip_stop)
        return True