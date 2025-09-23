-- return the maintenance records for a given vehicle
SELECT * FROM maintenance_view
WHERE vehicle_id = 4;

-- return all maintenance records for vehicles matching a given manufacturer
SELECT * FROM maintenance_view
WHERE manufacturer = "Bombardier";

/* return vehicles that have more than x capacity and are not assigned any trips on a particular day. 
   Tool to help with scheduling when a route requires a high capacity vehicle. */
SELECT
    v.vehicle_id,
    v.capacity
FROM Vehicle v
LEFT JOIN Trip t
    ON v.vehicle_id = t.vehicle_id
    AND t.trip_date = "2025-1-1"
WHERE v.capacity > 45
  AND v.vehicle_class = "bus"
  AND t.vehicle_id IS NULL;

/* return the timetable for a given route
   useful for printing timetables at route stops and to be made available online */
SELECT * FROM timetable
WHERE route_name LIKE "22";

/* return the expected arrival times for a given route at a given stop
   supplemental table at route stops for quicker assesment of expected stop times at the specific stop */
SELECT * FROM timetable
WHERE 
    route_name LIKE "22" AND 
    cross_street LIKE "Granville Ave" AND
    trip_direction LIKE "S"
ORDER BY arrival_time ASC;

/* Calculate the total stops for each route and return routes with more than X stops 
   Could be used for identifying routes with potentially too many stops. */
SELECT
    r.route_id,
    r.route_name,
    COUNT(DISTINCT rs.stop_id) AS total_stops
FROM Route r
JOIN route_stop rs
    ON r.route_id = rs.route_id
GROUP BY
    r.route_id,
    r.route_name
HAVING COUNT(DISTINCT rs.stop_id) > 4;

/* return all stops that are utilized by more than one route.
   a useful query for admins to prioritize stops which could use amenity upgrades, benches, rain cover, etc. */
SELECT
    s.stop_id,
    s.stop_direction,
    s.street_name,
    s.cross_street,
    s.latitude,
    s.longitude,
    GROUP_CONCAT(DISTINCT r.route_name) AS route_names
FROM stop s
JOIN route_stop rs ON s.stop_id = rs.stop_id
JOIN route r ON rs.route_id = r.route_id
GROUP BY 
    s.stop_id,
    s.stop_direction,
    s.street_name,
    s.cross_street,
    s.latitude,
    s.longitude
HAVING COUNT(DISTINCT rs.route_id) > 1;

-- A query for admins to check which drivers are able to drive metro vehicles
SELECT driver_id, driver_name, driver_classification, pay FROM driver
WHERE driver_classification LIKE "Bus and Metro" 
OR driver_classification LIKE "Metro Only";

-- return all drivers that are making less than the average pay
SELECT
    driver_id,
    driver_name,
    driver_classification,
    pay
FROM driver
WHERE pay < (
    SELECT AVG(pay)
    FROM driver
);

-- use dense_rank to group employees into pay brackets
SELECT
    driver_id,
    driver_name,
    driver_classification,
    pay,
    dense_rank() OVER (ORDER BY pay DESC) as pay_rank
FROM driver;


/* return all stops for a given route in one of its directions
   helpful for admins to review the stops for a route */
SELECT
    s.stop_id,
    r.route_name,
    s.stop_direction,
    s.street_name,
    s.cross_street,
    s.latitude,
    s.longitude,
    rs.stop_order
FROM route r
JOIN route_stop rs ON r.route_id = rs.route_id
JOIN stop s ON rs.stop_id = s.stop_id
WHERE r.route_name LIKE "22" AND s.stop_direction = "N"
ORDER BY rs.stop_order ASC;

/* return the scheduled trips for a particular driver on a particular day so they know what route and vehicle they are assigned
   to be used as a daily report for driver's daily assignments
   In practice, this would utilize CURDATE() for the trip_date like commented query below;
   but for the mock date, manually select a date.

   SELECT * FROM driver_view
   WHERE d.driver_name LIKE "Adam Smith" AND d.trip_date = CURDATE(); */
SELECT * FROM driver_view
WHERE driver_name LIKE "Adam Smith" AND trip_date = "2025-01-02";


/* A more general query than the above one to print a driver's schedule so they know what to expect for their upcoming assignments
   again, in practice, you would use CURDATE() but we use a specific date for the mock data

   SELECT * FROM driver_view
   WHERE d.driver_name LIKE "John Doe" AND d.trip_date >= CURDATE(); */
SELECT * FROM driver_view
WHERE driver_name LIKE "John Doe" AND trip_date >= "2024-12-31";

/* A moving average example does not immediately present itself with this database. 
   However, a reasonably plausible business request could be to derive the moving average for total vehicle capacity impacted by all maintenance each day. 
   This would help administrators estimate how much of the fleet is out for maintenance at a given time. */
WITH daily_totals AS (
    SELECT
        work_date,
        SUM(capacity) AS daily_capacity_affected
    FROM maintenance_view
    GROUP BY work_date
)
SELECT
    work_date,
    daily_capacity_affected,
    AVG(daily_capacity_affected) OVER (
        ORDER BY work_date
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS "3 Day Average"
FROM daily_totals
ORDER BY work_date;

-- Similar to the previous query, but additionally breaks this metric down by vehicle class (bus vs metro)
WITH daily_totals AS (
    SELECT
        vehicle_class,
        work_date,
        SUM(capacity) AS daily_capacity_affected
    FROM maintenance_view
    GROUP BY
        vehicle_class,
        work_date
)
SELECT
    vehicle_class,
    work_date,
    daily_capacity_affected,
    AVG(daily_capacity_affected) OVER (
        PARTITION BY vehicle_class
        ORDER BY work_date
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS "3 Day Average"
FROM daily_totals
ORDER BY work_date;
