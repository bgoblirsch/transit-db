-- route index
CREATE INDEX route_name ON route(route_name); -- to help with searching 

-- vehicle indices
CREATE INDEX vehicle_class ON vehicle(vehicle_class); -- to help with searching 
CREATE INDEX vehicle_type ON vehicle(vehicle_type); -- to help with searching 
CREATE INDEX manufacturer ON vehicle(manufacturer); -- to help with searching 
CREATE INDEX manufacture_year ON vehicle(manufacture_year); -- to help with data analysis on vehicle age

-- trip indices
CREATE INDEX route_id ON trip(route_id); -- to help with joins
CREATE INDEX driver_id ON trip(driver_id); -- to help with joins
CREATE INDEX vehicle_id ON trip(vehicle_id); -- to help with joins
CREATE INDEX trip_date ON trip(trip_date); -- to help with data analysis on specific date ranges

-- stop indices
CREATE INDEX street_name ON stop(street_name); -- to help with searching 
CREATE INDEX cross_steet ON stop(cross_street); -- to help with searching 

-- driver index
CREATE INDEX driver_name ON driver(driver_name); -- to help with searching 

-- route_stop index
CREATE INDEX stop_order ON route_stop(stop_order); -- to help with sorting query results by stop order

-- trip_stop index
CREATE INDEX arrival_time ON trip_stop(arrival_time); -- to help with sorting trip stops by arrival time

-- maintenance indices not required

-- view for maintenance workers that allows for viewing vehicle information along with previous maintenance records
CREATE VIEW maintenance_view as
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
    JOIN maintenance m ON v.vehicle_id = m.vehicle_id;

-- view for drivers to lookup which drivers are assigned to which routes and on what days
CREATE VIEW driver_view as
    SELECT 
        d.driver_id,
        d.driver_name, 
        t.trip_date, 
        r.route_name, 
        t.trip_direction, 
        t.vehicle_id
    FROM driver d
    JOIN trip t ON d.driver_id = t.driver_id
    JOIN route r ON t.route_id = r.route_id;

SELECT * FROM driver_view;
    
-- view for the general public to lookup arrival times for trips at their desired stop location
CREATE VIEW timetable as
    SELECT 
        r.route_name,
        t.trip_direction,
        s.street_name, 
        s.cross_street,
        ts.arrival_time
    FROM route r
    JOIN trip t ON r.route_id = t.route_id
    JOIN trip_stop ts ON t.trip_id = ts.trip_id
    JOIN stop s ON ts.stop_id = s.stop_id
    JOIN route_stop rs ON (rs.route_id = r.route_id AND rs.stop_id = s.stop_id)
    ORDER BY route_name, trip_direction, arrival_time;

SELECT * FROM timetable;