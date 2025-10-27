from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from src.database import session_scope
import src.models as m

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