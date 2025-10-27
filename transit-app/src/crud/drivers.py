from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from src.database import session_scope
import src.models as m
import datetime
import decimal

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