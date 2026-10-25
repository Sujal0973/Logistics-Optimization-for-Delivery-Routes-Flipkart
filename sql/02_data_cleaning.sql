-- =====================================================================
-- Project: Logistics Optimization for Delivery Routes - Flipkart
-- File: 02_data_cleaning.sql
-- Description: Data cleaning, missing value handling, date standardization,
--              and business rule validation queries.
-- =====================================================================

USE flipkart_logistics;

-- ---------------------------------------------------------------------
-- 1. Check Primary Key Uniqueness & Identify Duplicates
-- ---------------------------------------------------------------------

-- 1.1 Check duplicate Order IDs
SELECT 
    Order_ID, 
    COUNT(*) AS duplicate_count 
FROM flipkart_orders 
GROUP BY Order_ID 
HAVING COUNT(*) > 1;
-- Finding: 0 duplicates found. Order_ID is strictly unique (Primary Key).

-- 1.2 Check duplicate Tracking IDs
SELECT 
    Tracking_ID, 
    COUNT(*) AS duplicate_count 
FROM flipkart_shipmenttracking 
GROUP BY Tracking_ID 
HAVING COUNT(*) > 1;
-- Finding: 0 duplicates found. Tracking_ID is unique.

-- ---------------------------------------------------------------------
-- 2. Missing Value Imputation (Traffic_Delay_Min)
-- ---------------------------------------------------------------------

-- Check if any Route has NULL Traffic_Delay_Min
SELECT 
    Route_ID, 
    Start_Location, 
    End_Location, 
    Traffic_Delay_Min 
FROM flipkart_routes 
WHERE Traffic_Delay_Min IS NULL;

-- Safe Imputation Query:
-- If Traffic_Delay_Min is NULL, impute with the global average traffic delay
-- across all routes (or region average).
SET SQL_SAFE_UPDATES = 0;

UPDATE flipkart_routes
SET Traffic_Delay_Min = (
    SELECT ROUND(AVG(r_sub.Traffic_Delay_Min))
    FROM (SELECT Traffic_Delay_Min FROM flipkart_routes WHERE Traffic_Delay_Min IS NOT NULL) r_sub
)
WHERE Traffic_Delay_Min IS NULL;

SET SQL_SAFE_UPDATES = 1;

-- ---------------------------------------------------------------------
-- 3. Date Standardization & Parsing
-- ---------------------------------------------------------------------

-- If data was imported as VARCHAR/TEXT, standardize to MySQL DATE / DATETIME:
-- 3.1 Standardize flipkart_orders date columns
SET SQL_SAFE_UPDATES = 0;

UPDATE flipkart_orders 
SET Order_Date = STR_TO_DATE(Order_Date, '%d-%m-%Y')
WHERE Order_Date LIKE '__-__-____';

UPDATE flipkart_orders 
SET Expected_Delivery_Date = STR_TO_DATE(Expected_Delivery_Date, '%d-%m-%Y')
WHERE Expected_Delivery_Date LIKE '__-__-____';

UPDATE flipkart_orders 
SET Actual_Delivery_Date = STR_TO_DATE(Actual_Delivery_Date, '%d-%m-%Y')
WHERE Actual_Delivery_Date LIKE '__-__-____';

-- 3.2 Standardize flipkart_shipmenttracking Checkpoint_Time (CRITICAL FIX)
-- Note: Leaving Checkpoint_Time as VARCHAR causes chronological ordering bugs
-- in MAX(Checkpoint_Time) because '24-07-2025' > '22-08-2025' alphabetically!
UPDATE flipkart_shipmenttracking
SET Checkpoint_Time = STR_TO_DATE(Checkpoint_Time, '%d-%m-%Y %H:%i')
WHERE Checkpoint_Time LIKE '__-__-____ %';

SET SQL_SAFE_UPDATES = 1;

-- ---------------------------------------------------------------------
-- 4. Logical Validation & Business Constraints
-- ---------------------------------------------------------------------

-- 4.1 Validate delivery timeline: Actual_Delivery_Date must not precede Order_Date
SELECT 
    Order_ID,
    Order_Date,
    Expected_Delivery_Date,
    Actual_Delivery_Date,
    DATEDIFF(Actual_Delivery_Date, Order_Date) AS turnaround_days,
    CASE 
        WHEN Actual_Delivery_Date < Order_Date THEN 'Invalid (Anomaly)' 
        ELSE 'Valid' 
    END AS delivery_status_flag
FROM flipkart_orders
ORDER BY turnaround_days ASC;
-- Finding: 100% of records are valid (0 anomalies detected).

-- 4.2 Validate Foreign Key Referential Integrity
-- Orders with non-existent warehouses
SELECT o.Order_ID, o.Warehouse_ID 
FROM flipkart_orders o 
LEFT JOIN flipkart_warehouses w ON o.Warehouse_ID = w.Warehouse_ID 
WHERE w.Warehouse_ID IS NULL;

-- Orders with non-existent routes
SELECT o.Order_ID, o.Route_ID 
FROM flipkart_orders o 
LEFT JOIN flipkart_routes r ON o.Route_ID = r.Route_ID 
WHERE r.Route_ID IS NULL;

-- Orders with non-existent agents
SELECT o.Order_ID, o.Agent_ID 
FROM flipkart_orders o 
LEFT JOIN flipkart_deliveryagents a ON o.Agent_ID = a.Agent_ID 
WHERE a.Agent_ID IS NULL;
-- Finding: Referential integrity is 100% maintained across all tables.

-- ---------------------------------------------------------------------
-- 5. Standardize Categorical Values in Shipment Tracking
-- ---------------------------------------------------------------------

-- Standardize empty or 'None' strings in Delay_Reason
SET SQL_SAFE_UPDATES = 0;
UPDATE flipkart_shipmenttracking
SET Delay_Reason = 'None'
WHERE Delay_Reason IS NULL OR TRIM(Delay_Reason) = '';
SET SQL_SAFE_UPDATES = 1;

-- Verify distinct delay reasons
SELECT 
    Delay_Reason, 
    COUNT(*) AS total_occurrences,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM flipkart_shipmenttracking), 2) AS percentage
FROM flipkart_shipmenttracking
GROUP BY Delay_Reason
ORDER BY total_occurrences DESC;
