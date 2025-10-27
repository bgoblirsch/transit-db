from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from src.database import session_scope
import src.models as m

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
                      old_stop_id: int,
                      old_route_direction: str,
                      stop_order: int | None = None,
                      new_stop_id: int | None = None,
                      new_route_direction: str | None = None) -> None:
    """Update the stop order for a route-stop entry."""
    with session_scope() as s:
        route_stop = s.get(m.RouteStop, (route_id, old_stop_id, old_route_direction))
        if not route_stop:
            raise NoResultFound(f"Route ID {route_id} & Stop ID {old_stop_id} not found for direction {old_route_direction}.")
        
        if route_id: route_stop.route_id = route_id
        if new_stop_id: route_stop.stop_id = new_stop_id
        if new_route_direction: route_stop.route_direction = new_route_direction
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