from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from src.database import session_scope
import src.models as m

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
