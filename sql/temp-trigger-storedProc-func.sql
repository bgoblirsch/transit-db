-- temporary table for assessing and manipulating driver pay to try and identify driver pay adjustments for drivers that have been employed for a long time but are being underpaid
CREATE TEMPORARY TABLE temp_drivers(
    driver_id int primary key, 
    driver_name varchar(50),
    driver_classification varchar(25),
    start_date date,
    pay decimal(10,2)
);

INSERT INTO temp_drivers(driver_id, driver_name, driver_classification, start_date, pay) -- then inserted data based on a query result
SELECT *
FROM driver;

-- temporary table to inspect the maintenance records of old vehicles and identify ones that may need to be replaced soon and how it would affect fleet rider capacity if they break down or are removed from the fleet without replacement
CREATE TEMPORARY TABLE temp_vehicles (
vehicle_id INT PRIMARY KEY,
vehicle_class VARCHAR(25) NOT NULL,
manufacturer VARCHAR(25) NOT NULL,
manufacture_year INT NOT NULL,
vehicle_type VARCHAR(25) NOT NULL,
capacity INT,
maintenance_id INT,
work_date DATE,
work_performed VARCHAR(255)
);

INSERT INTO temp_vehicles (
vehicle_id, vehicle_class, manufacturer, manufacture_year, vehicle_type, 
capacity, maintenance_id, work_date, work_performed
)
SELECT 
v.vehicle_id,
v.vehicle_class,
v.manufacturer,
v.manufacture_year,
v.vehicle_type,
v.capacity,
m.maintenance_id,
m.work_date,
m.work_performed
FROM vehicle v
JOIN maintenance m 
ON v.vehicle_id = m.vehicle_id
WHERE v.manufacture_year < 1985;

-- Trigger to ensure that drivers cannot be assigned to two different routes on the same day. A driver can and should be assigned multiple trips on the same day (for return trips), but only for the same route.

DELIMITER //

CREATE TRIGGER enforce_same_route
BEFORE INSERT ON trip
FOR EACH ROW
BEGIN
    DECLARE conflicting_trips int;
    SELECT COUNT(*)
    INTO conflicting_trips
    FROM trip
    WHERE driver_id  = NEW.driver_id
      AND trip_date  = NEW.trip_date
      AND route_id <> NEW.route_id;

    IF conflicting_trips > 0 THEN
        SIGNAL SQLSTATE "45000"
        SET MESSAGE_TEXT = "Driver is already assigned to a different route that day. Must retain the same route.";
    END IF;
END //
DELIMITER ;

-- also trigger for updating a trip
DELIMITER //

CREATE TRIGGER enforce_same_route_per_day_upd
BEFORE UPDATE ON trip
FOR EACH ROW
BEGIN
    DECLARE conflicting_trips INT;
    IF (NEW.driver_id  <> OLD.driver_id)
       OR (NEW.trip_date <> OLD.trip_date)
       OR (NEW.route_id  <> OLD.route_id)
    THEN
        SELECT COUNT(*)
          INTO conflicting_trips
          FROM trip
         WHERE driver_id = NEW.driver_id
           AND trip_date = NEW.trip_date
           AND route_id <> NEW.route_id
           AND trip_id <> OLD.trip_id; 

        IF conflicting_trips > 0 THEN
            SIGNAL SQLSTATE "45000"
            SET MESSAGE_TEXT = "Driver is already assigned to a different route that day. Must retain the same route.";
        END IF;
    END IF;
END //
DELIMITER ;

-- stored procedure to identify dates for a given vehicle that it is not assigned to any trips. This would be plan scheduled maintenance for the vehicle.
DELIMITER //
CREATE PROCEDURE find_vehicle_availability(
    IN proc_vehicle_id INT,
    IN proc_start_date DATE,
    IN proc_end_date   DATE,
    IN proc_max_days   INT
)
BEGIN
    DECLARE cur_date DATE;
    DECLARE trip_count INT;
    DECLARE found_days INT DEFAULT 0;

    CREATE TEMPORARY TABLE IF NOT EXISTS temp_free_days (
      free_date DATE PRIMARY KEY
    );
    TRUNCATE temp_free_days;

    SET cur_date = proc_start_date;
    
    free_days_loop: WHILE cur_date <= proc_end_date DO

        SELECT COUNT(*)
          INTO trip_count
          FROM trip
         WHERE vehicle_id = proc_vehicle_id
           AND trip_date  = cur_date;

        IF trip_count = 0 THEN
            INSERT INTO temp_free_days(free_date)
            VALUES (cur_date);

            SET found_days = found_days + 1;
            IF found_days >= proc_max_days THEN
                LEAVE free_days_loop;
            END IF;
        END IF;

        SET cur_date = DATE_ADD(cur_date, INTERVAL 1 DAY);
    END WHILE free_days_loop;

    SELECT free_date AS available_day
    FROM temp_free_days
    ORDER BY free_date;
END //
DELIMITER ;

CALL find_vehicle_availability(3, "2025/01/01", "2025/01/05", 3);

-- function to determine the total capacity for a given route on a given day based on the assigned vehicles' capacities
DELIMITER //
CREATE FUNCTION daily_route_capacity(
    p_route_id int,
    p_trip_date date
)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_capacity int DEFAULT 0;

    SELECT IFNULL(SUM(v.capacity), 0)
      INTO v_capacity
      FROM trip t
      JOIN vehicle v ON t.vehicle_id = v.vehicle_id
     WHERE t.route_id  = p_route_id
       AND t.trip_date = p_trip_date;

    RETURN v_capacity;
END //
DELIMITER ;

SELECT daily_route_capacity(1,"2025/01/01") AS total_trip_capacity;