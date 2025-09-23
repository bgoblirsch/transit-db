-- create DB
CREATE DATABASE transitDB;
use transitDB;

-- create users and set rights
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin';
CREATE USER 'maintenance'@'localhost' IDENTIFIED BY 'maintenance';
GRANT ALL PRIVILEGES ON transitDB.* TO 'admin'@'localhost';
GRANT SELECT, INSERT, UPDATE ON transitDB.maintenance TO 'maintenance'@'localhost';
GRANT SELECT ON transitDB.vehicle TO 'maintenance'@'localhost';
FLUSH PRIVILEGES;

-- create tables

CREATE TABLE route(
route_id int,
route_name varchar(25) not null,
route_type varchar(5) not null,
primary key (route_id)
);

CREATE TABLE vehicle(
vehicle_id int,
vehicle_class varchar(25) not null,
manufacturer varchar(25) not null,
manufacture_year int not null,
vehicle_type varchar(25) not null,
capacity int,
primary key (vehicle_id)
);

CREATE TABLE maintenance(
maintenance_id int AUTO_INCREMENT,
vehicle_id int,
work_date date not null,
work_performed varchar(200) not null,
primary key (maintenance_id),
foreign key (vehicle_id) references vehicle(vehicle_id)
);

CREATE TABLE stop(
stop_id int,
stop_direction varchar(1) not null,
street_name varchar(50) not null,
cross_street varchar(50) not null,
latitude float,
longitude float,
primary key (stop_id)
);

CREATE TABLE driver(
driver_id int AUTO_INCREMENT,
driver_name varchar(50) not null,
driver_classification varchar(25) not null,
start_date date,
pay decimal(10,2) not null,
primary key (driver_id)
);

CREATE TABLE trip(
trip_id int,
route_id int,
driver_id int,
vehicle_id int,
trip_date date not null,
trip_direction varchar(1) not null,
primary key (trip_id),
foreign key (route_id) references route(route_id),
foreign key (driver_id) references driver(driver_id),
foreign key (vehicle_id) references vehicle(vehicle_id)
);

CREATE TABLE route_stop(
route_id int,
stop_id int,
route_direction varchar(1) not null,
stop_order int,
primary key (route_id, stop_id, route_direction),
foreign key (route_id) references route(route_id),
foreign key (stop_id) references stop(stop_id)
);

-- NOTE: arrival_time is stored as a simple integer in number of minutes 0-1440 to simplify this field and it saves database space.
--       The conversion logic will be implemented in the later portions of the project so that the timetables are in a more readable format.
--       Input logic will also be handled so that administrators can enter a more human readable format instead of handling the conversion themselves.
CREATE TABLE trip_stop(
trip_id int,
stop_id int,
arrival_time int not null,
primary key (trip_id, stop_id),
foreign key (trip_id) references trip(trip_id),
foreign key (stop_id) references stop(stop_id)
);

-- load mock data

LOAD DATA LOCAL INFILE "/Users/brandongoblirsch/Documents/school2024/cs727/transitDB/mock-data/routes.csv"
INTO TABLE route
FIELDS TERMINATED BY ','
ENCLOSED BY ""
LINES TERMINATED BY "\n"
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE "/Users/brandongoblirsch/Documents/school2024/cs727/transitDB/mock-data/vehicles.csv"
INTO TABLE vehicle
FIELDS TERMINATED BY ','
ENCLOSED BY ""
LINES TERMINATED BY "\n"
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE "/Users/brandongoblirsch/Documents/school2024/cs727/transitDB/mock-data/maintenance.csv"
INTO TABLE maintenance
FIELDS TERMINATED BY ','
ENCLOSED BY ""
LINES TERMINATED BY "\n"
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE "/Users/brandongoblirsch/Documents/school2024/cs727/transitDB/mock-data/stops.csv"
INTO TABLE stop
FIELDS TERMINATED BY ','
ENCLOSED BY ""
LINES TERMINATED BY "\n"
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE "/Users/brandongoblirsch/Documents/school2024/cs727/transitDB/mock-data/drivers.csv"
INTO TABLE driver
FIELDS TERMINATED BY ','
ENCLOSED BY ""
LINES TERMINATED BY "\n"
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE "/Users/brandongoblirsch/Documents/school2024/cs727/transitDB/mock-data/trips.csv"
INTO TABLE trip
FIELDS TERMINATED BY ','
ENCLOSED BY ""
LINES TERMINATED BY "\n"
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE "/Users/brandongoblirsch/Documents/school2024/cs727/transitDB/mock-data/routes-stops.csv"
INTO TABLE route_stop
FIELDS TERMINATED BY ','
ENCLOSED BY ""
LINES TERMINATED BY "\n"
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE "/Users/brandongoblirsch/Documents/school2024/cs727/transitDB/mock-data/trips-stops.csv"
INTO TABLE trip_stop
FIELDS TERMINATED BY ','
ENCLOSED BY ""
LINES TERMINATED BY "\n"
IGNORE 1 ROWS;
