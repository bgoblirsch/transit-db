from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from src.database import session_scope
import src.models as m
import datetime

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