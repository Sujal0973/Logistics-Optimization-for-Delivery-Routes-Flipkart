-- =====================================================================
-- Project: Logistics Optimization for Delivery Routes - Flipkart
-- File: 01_schema_and_load.sql
-- Description: Database schema creation, table definitions with constraints,
--              indexes for performance, and data import instructions.
-- =====================================================================

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS flipkart_logistics;
USE flipkart_logistics;

-- Step 2: Drop Tables if they exist (in reverse foreign key dependency order)
DROP TABLE IF EXISTS flipkart_shipmenttracking;
DROP TABLE IF EXISTS flipkart_orders;
DROP TABLE IF EXISTS flipkart_deliveryagents;
DROP TABLE IF EXISTS flipkart_routes;
DROP TABLE IF EXISTS flipkart_warehouses;

-- Step 3: Create Tables with Constraints

-- 3.1 Warehouses Table
CREATE TABLE flipkart_warehouses (
    Warehouse_ID VARCHAR(10) NOT NULL PRIMARY KEY,
    Warehouse_Name VARCHAR(100) NOT NULL,
    City VARCHAR(50) NOT NULL,
    Processing_Capacity INT NOT NULL,
    Average_Processing_Time_Min INT NOT NULL,
    CONSTRAINT chk_proc_time CHECK (Average_Processing_Time_Min >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3.2 Routes Table
CREATE TABLE flipkart_routes (
    Route_ID VARCHAR(10) NOT NULL PRIMARY KEY,
    Start_Location VARCHAR(50) NOT NULL,
    End_Location VARCHAR(50) NOT NULL,
    Distance_KM INT NOT NULL,
    Average_Travel_Time_Min INT NOT NULL,
    Traffic_Delay_Min INT DEFAULT NULL,
    CONSTRAINT chk_dist CHECK (Distance_KM > 0),
    CONSTRAINT chk_travel_time CHECK (Average_Travel_Time_Min > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3.3 Delivery Agents Table
CREATE TABLE flipkart_deliveryagents (
    Agent_ID VARCHAR(10) NOT NULL PRIMARY KEY,
    Agent_Name VARCHAR(100) NOT NULL,
    Route_ID VARCHAR(10) NOT NULL,
    Avg_Speed_KMPH DECIMAL(5,2) NOT NULL,
    On_Time_Delivery_Percentage DECIMAL(5,2) NOT NULL,
    Experience_Years DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (Route_ID) REFERENCES flipkart_routes(Route_ID) ON UPDATE CASCADE,
    CONSTRAINT chk_agent_speed CHECK (Avg_Speed_KMPH > 0),
    CONSTRAINT chk_agent_ontime CHECK (On_Time_Delivery_Percentage BETWEEN 0 AND 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3.4 Orders Table
CREATE TABLE flipkart_orders (
    Order_ID VARCHAR(20) NOT NULL PRIMARY KEY,
    Warehouse_ID VARCHAR(10) NOT NULL,
    Route_ID VARCHAR(10) NOT NULL,
    Agent_ID VARCHAR(10) NOT NULL,
    Order_Date DATE NOT NULL,
    Expected_Delivery_Date DATE NOT NULL,
    Actual_Delivery_Date DATE NOT NULL,
    Status VARCHAR(50) NOT NULL DEFAULT 'Delivered',
    Order_Value DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (Warehouse_ID) REFERENCES flipkart_warehouses(Warehouse_ID) ON UPDATE CASCADE,
    FOREIGN KEY (Route_ID) REFERENCES flipkart_routes(Route_ID) ON UPDATE CASCADE,
    FOREIGN KEY (Agent_ID) REFERENCES flipkart_deliveryagents(Agent_ID) ON UPDATE CASCADE,
    CONSTRAINT chk_delivery_order CHECK (Actual_Delivery_Date >= Order_Date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3.5 Shipment Tracking Table
CREATE TABLE flipkart_shipmenttracking (
    Tracking_ID VARCHAR(10) NOT NULL PRIMARY KEY,
    Order_ID VARCHAR(20) NOT NULL,
    Checkpoint VARCHAR(100) NOT NULL,
    Checkpoint_Time DATETIME NOT NULL,
    Delay_Reason VARCHAR(50) DEFAULT 'None',
    Delay_Minutes INT NOT NULL DEFAULT 0,
    FOREIGN KEY (Order_ID) REFERENCES flipkart_orders(Order_ID) ON UPDATE CASCADE,
    CONSTRAINT chk_delay_min CHECK (Delay_Minutes >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Step 4: Optimization Indexes
CREATE INDEX idx_orders_warehouse ON flipkart_orders(Warehouse_ID);
CREATE INDEX idx_orders_route ON flipkart_orders(Route_ID);
CREATE INDEX idx_orders_agent ON flipkart_orders(Agent_ID);
CREATE INDEX idx_orders_dates ON flipkart_orders(Expected_Delivery_Date, Actual_Delivery_Date);
CREATE INDEX idx_tracking_order ON flipkart_shipmenttracking(Order_ID);
CREATE INDEX idx_tracking_time ON flipkart_shipmenttracking(Checkpoint_Time);

-- =====================================================================
-- Step 5: Data Loading Instructions (MySQL LOAD DATA INFILE)
-- Note: Replace '/path/to/datasets/' with the absolute path on your system.
-- If local-infile is disabled, enable it: SET GLOBAL local_infile = 1;
-- =====================================================================

/*
-- 5.1 Load Warehouses
LOAD DATA LOCAL INFILE '/path/to/datasets/Flipkart_Warehouses.csv'
INTO TABLE flipkart_warehouses
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Warehouse_ID, Warehouse_Name, City, Processing_Capacity, Average_Processing_Time_Min);

-- 5.2 Load Routes
LOAD DATA LOCAL INFILE '/path/to/datasets/Flipkart_Routes.csv'
INTO TABLE flipkart_routes
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Route_ID, Start_Location, End_Location, Distance_KM, Average_Travel_Time_Min, Traffic_Delay_Min);

-- 5.3 Load Delivery Agents
LOAD DATA LOCAL INFILE '/path/to/datasets/Flipkart_DeliveryAgents.csv'
INTO TABLE flipkart_deliveryagents
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Agent_ID, Agent_Name, Route_ID, Avg_Speed_KMPH, On_Time_Delivery_Percentage, Experience_Years);

-- 5.4 Load Orders (Standardizing DD-MM-YYYY dates during import)
LOAD DATA LOCAL INFILE '/path/to/datasets/Flipkart_Orders.csv'
INTO TABLE flipkart_orders
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Order_ID, Warehouse_ID, Route_ID, Agent_ID, @order_date, @exp_date, @act_date, Status, Order_Value)
SET Order_Date = STR_TO_DATE(@order_date, '%d-%m-%Y'),
    Expected_Delivery_Date = STR_TO_DATE(@exp_date, '%d-%m-%Y'),
    Actual_Delivery_Date = STR_TO_DATE(@act_date, '%d-%m-%Y');

-- 5.5 Load Shipment Tracking (Standardizing DD-MM-YYYY HH:MI timestamp)
LOAD DATA LOCAL INFILE '/path/to/datasets/Flipkart_ShipmentTracking.csv'
INTO TABLE flipkart_shipmenttracking
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Tracking_ID, Order_ID, Checkpoint, @chk_time, @delay_reason, Delay_Minutes)
SET Checkpoint_Time = STR_TO_DATE(@chk_time, '%d-%m-%Y %H:%i'),
    Delay_Reason = NULLIF(@delay_reason, '');
*/
