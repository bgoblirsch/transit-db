from src.database import session_scope
from sqlalchemy import text

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
    
