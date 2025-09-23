from __future__ import annotations

import datetime, decimal
from typing import List

from sqlalchemy import Integer, String, Date, Float, DECIMAL, ForeignKey, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Route(Base):
    __tablename__ = "route"

    route_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_name: Mapped[str] = mapped_column(String(25), nullable=False)
    route_type: Mapped[str] = mapped_column(String(5), nullable=False)

    # Relationships
    trips: Mapped[List["Trip"]] = relationship(back_populates="route", cascade="all, delete-orphan")
    route_stops: Mapped[List["RouteStop"]] = relationship(back_populates="route", cascade="all, delete-orphan")


class Vehicle(Base):
    __tablename__ = "vehicle"

    vehicle_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_class: Mapped[str] = mapped_column(String(25), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(25), nullable=False)
    manufacture_year: Mapped[int] = mapped_column(Integer, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(25), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer)

    # Relationships
    maintenances: Mapped[List["Maintenance"]] = relationship(back_populates="vehicle", cascade="all, delete-orphan")
    trips: Mapped[List["Trip"]] = relationship(back_populates="vehicle", cascade="all, delete-orphan")


class Maintenance(Base):
    __tablename__ = "maintenance"

    maintenance_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicle.vehicle_id"), nullable=False)
    work_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    work_performed: Mapped[str] = mapped_column(String(200), nullable=False)

    # Relationship
    vehicle: Mapped["Vehicle"] = relationship(back_populates="maintenances")


class Stop(Base):
    __tablename__ = "stop"

    stop_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stop_direction: Mapped[str] = mapped_column(String(1), nullable=False)
    street_name: Mapped[str] = mapped_column(String(50), nullable=False)
    cross_street: Mapped[str] = mapped_column(String(50), nullable=False)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    # Relationships
    route_stops: Mapped[List["RouteStop"]] = relationship(back_populates="stop", cascade="all, delete-orphan")
    trip_stops: Mapped[List["TripStop"]] = relationship(back_populates="stop", cascade="all, delete-orphan")


class Driver(Base):
    __tablename__ = "driver"

    driver_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    driver_name: Mapped[str] = mapped_column(String(50), nullable=False)
    driver_classification: Mapped[str] = mapped_column(String(25), nullable=False)
    start_date: Mapped[datetime.date | None] = mapped_column(Date)
    pay: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)

    # Relationships
    trips: Mapped[List["Trip"]] = relationship(back_populates="driver", cascade="all, delete-orphan")


class Trip(Base):
    __tablename__ = "trip"

    trip_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("route.route_id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("driver.driver_id"), nullable=False)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicle.vehicle_id"), nullable=False)
    trip_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    trip_direction: Mapped[str] = mapped_column(String(1), nullable=False)

    # Relationships
    route: Mapped["Route"] = relationship(back_populates="trips")
    driver: Mapped["Driver"] = relationship(back_populates="trips")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="trips")
    trip_stops: Mapped[List["TripStop"]] = relationship(back_populates="trip", cascade="all, delete-orphan")


class RouteStop(Base):
    __tablename__ = "route_stop"

    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("route.route_id"), primary_key=True)
    stop_id: Mapped[int] = mapped_column(Integer, ForeignKey("stop.stop_id"), primary_key=True)
    route_direction: Mapped[str] = mapped_column(String(1), primary_key=True)
    stop_order: Mapped[int] = mapped_column(Integer)

    # Relationships
    route: Mapped["Route"] = relationship(back_populates="route_stops")
    stop: Mapped["Stop"] = relationship(back_populates="route_stops")


class TripStop(Base):
    __tablename__ = "trip_stop"

    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("trip.trip_id"), primary_key=True)
    stop_id: Mapped[int] = mapped_column(Integer, ForeignKey("stop.stop_id"), primary_key=True)
    arrival_time: Mapped[int] = mapped_column(Integer, nullable=False)  # minutes 0‑1440

    # Relationships
    trip: Mapped["Trip"] = relationship(back_populates="trip_stops")
    stop: Mapped["Stop"] = relationship(back_populates="trip_stops")

class Timetable(Base):
    __tablename__ = "timetable"
    __table_args__ = {"info": {"view": True}}  # Optional, documents that it's a view

    route_name: Mapped[str] = mapped_column(String, primary_key=True)
    trip_direction: Mapped[str] = mapped_column(String, primary_key=True)
    street_name: Mapped[str] = mapped_column(String, primary_key=True)
    cross_street: Mapped[str] = mapped_column(String, primary_key=True)
    arrival_time: Mapped[str] = mapped_column(String, primary_key=True)