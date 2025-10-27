from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from src.database import session_scope
import src.models as m

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