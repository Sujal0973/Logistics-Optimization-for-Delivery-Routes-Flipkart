-- =====================================================================
-- PROJECT: Logistics Optimization for Delivery Routes – Flipkart
-- AUTHOR: Sujal Agrahari
-- DATABASE: MySQL 8.0+
-- FILE: Flipkart_Logistics_Optimization.sql
-- =====================================================================

CREATE DATABASE IF NOT EXISTS sqlproject;
USE sqlproject;

-- Initial Database Inspection
SELECT * FROM flipkart_deliveryagents LIMIT 5;
SELECT * FROM flipkart_orders LIMIT 5;
SELECT * FROM flipkart_routes LIMIT 5;
SELECT * FROM flipkart_shipmenttracking LIMIT 5;
SELECT * FROM flipkart_warehouses LIMIT 5;


-- =====================================================================
-- Task 1: Data Cleaning & Preparation (10 Marks)
-- =====================================================================

-- 1. Identify and delete duplicate Order_ID records.
-- Step 1.1: Identify duplicate records (Verification)
SELECT Order_ID, COUNT(*) AS count 
FROM flipkart_orders 
GROUP BY Order_ID 
HAVING COUNT(*) > 1;
-- Finding: No duplicate Order_ID values found as Order_ID acts as the unique Primary Key.

-- Step 1.2: Delete duplicate records query (Standard Safe Deletion using Window Function)
DELETE FROM flipkart_orders 
WHERE Order_ID IN (
    SELECT Order_ID FROM (
        SELECT Order_ID, ROW_NUMBER() OVER (PARTITION BY Order_ID ORDER BY Order_Date) AS row_num
        FROM flipkart_orders
    ) duplicates
    WHERE row_num > 1
);


-- 2. Replace null Traffic_Delay_Min with the average delay for that route.
SET SQL_SAFE_UPDATES = 0;

UPDATE flipkart_routes r 
JOIN (
    SELECT Route_ID, AVG(Traffic_Delay_Min) AS avg_delay 
    FROM flipkart_routes 
    GROUP BY Route_ID
) t ON r.Route_ID = t.Route_ID 
SET r.Traffic_Delay_Min = COALESCE(
    t.avg_delay, 
    (SELECT ROUND(AVG(Traffic_Delay_Min)) FROM (SELECT * FROM flipkart_routes) r2 WHERE r2.Traffic_Delay_Min IS NOT NULL)
)
WHERE r.Traffic_Delay_Min IS NULL;


-- 3. Convert all date columns into YYYY-MM-DD format using SQL functions.
-- Check sample date values before conversion
SELECT order_date, Expected_Delivery_Date, Actual_Delivery_Date FROM flipkart_orders LIMIT 5;
DESCRIBE flipkart_orders;

-- Standardize Date Columns in flipkart_orders
UPDATE flipkart_orders 
SET order_date = STR_TO_DATE(order_date, '%d-%m-%Y') 
WHERE order_date LIKE '__-__-____';

UPDATE flipkart_orders 
SET Expected_Delivery_Date = STR_TO_DATE(Expected_Delivery_Date, '%d-%m-%Y') 
WHERE Expected_Delivery_Date LIKE '__-__-____';

UPDATE flipkart_orders 
SET Actual_Delivery_Date = STR_TO_DATE(Actual_Delivery_Date, '%d-%m-%Y') 
WHERE Actual_Delivery_Date LIKE '__-__-____';

-- Standardize Checkpoint_Time in flipkart_shipmenttracking (ensures proper chronological ordering)
UPDATE flipkart_shipmenttracking 
SET Checkpoint_Time = STR_TO_DATE(Checkpoint_Time, '%d-%m-%Y %H:%i')
WHERE Checkpoint_Time LIKE '__-__-____ %';


-- 4. Ensure that no Actual_Delivery_Date is before Order_Date (flag such records).
SELECT 
    Order_ID,
    Order_Date,
    Actual_Delivery_Date,
    CASE 
        WHEN Actual_Delivery_Date < Order_Date THEN 'Invalid' 
        ELSE 'Valid' 
    END AS delivery_flag 
FROM flipkart_orders;
-- Finding: 100% of records are Valid (0 delivery anomalies detected).


-- =====================================================================
-- Task 2: Delivery Delay Analysis (10 Marks)
-- =====================================================================

-- 1. Calculate delivery delay (in days) for each order.
-- Positive delay indicates late delivery; 0 or negative indicates on-time / early delivery.
SELECT 
    Order_ID,
    Expected_Delivery_Date,
    Actual_Delivery_Date,
    DATEDIFF(Actual_Delivery_Date, Expected_Delivery_Date) AS delivery_delay 
FROM flipkart_orders;


-- 2. Find Top 10 delayed routes based on average delay days.
SELECT 
    Route_ID,
    ROUND(AVG(DATEDIFF(Actual_Delivery_Date, Expected_Delivery_Date)), 2) AS avg_delay 
FROM flipkart_orders 
GROUP BY Route_ID 
ORDER BY avg_delay DESC 
LIMIT 10;


-- 3. Use window functions to rank all orders by delay within each warehouse.
SELECT 
    Order_ID,
    Warehouse_ID,
    DATEDIFF(Actual_Delivery_Date, Expected_Delivery_Date) AS delivery_delay,
    RANK() OVER (
        PARTITION BY Warehouse_ID 
        ORDER BY DATEDIFF(Actual_Delivery_Date, Expected_Delivery_Date) DESC
    ) AS warehouse_rank 
FROM flipkart_orders;


-- =====================================================================
-- Task 3: Route Optimization Insights (20 Marks)
-- =====================================================================

-- 1. For each route, calculate:
--    - Average delivery time (in days)
--    - Average traffic delay
--    - Distance-to-time efficiency ratio: Distance_KM / Average_Travel_Time_Min
SELECT 
    r.Route_ID,
    ROUND(AVG(DATEDIFF(o.Actual_Delivery_Date, o.Order_Date)), 2) AS avg_delivery_time,
    ROUND(AVG(r.Traffic_Delay_Min), 2) AS avg_traffic_delay,
    ROUND(AVG(r.Distance_KM / r.Average_Travel_Time_Min), 3) AS efficiency_ratio 
FROM flipkart_orders o 
JOIN flipkart_routes r ON r.Route_ID = o.Route_ID 
GROUP BY r.Route_ID;


-- 2. Identify 3 routes with the worst efficiency ratio.
SELECT 
    Route_ID,
    ROUND(AVG(Distance_KM / Average_Travel_Time_Min), 3) AS efficiency_ratio 
FROM flipkart_routes 
GROUP BY Route_ID 
ORDER BY efficiency_ratio ASC 
LIMIT 3;


-- 3. Find routes with >20% delayed shipments.
SELECT 
    Route_ID,
    ROUND(COUNT(CASE WHEN Actual_Delivery_Date > Expected_Delivery_Date THEN 1 END) * 100.0 / COUNT(*), 2) AS Delayed_Shipments 
FROM flipkart_orders 
GROUP BY Route_ID 
HAVING Delayed_Shipments > 20
ORDER BY Delayed_Shipments DESC;


-- 4. Recommend potential routes for optimization.
/* 
ACTIONABLE ROUTE OPTIMIZATION RECOMMENDATIONS:
1. Optimize Low-Efficiency Routes:
   - Routes RT_13 (0.728 km/min), RT_14 (1.001 km/min), and RT_03 (1.130 km/min) display sluggish transit speeds.
   - For long-haul route RT_13 (Hyderabad -> Jaipur, 1078 km), establish staged relay hubs (e.g. via Nagpur/Bhopal) to prevent driver fatigue.
2. Manage High-Traffic Areas:
   - High traffic congestion in routes like RT_08 (90 min delay) and RT_09 (83 min delay) directly causes delivery delays.
   - Introduce off-peak dispatches (night windows between 10 PM - 5 AM) for trunk line freight.
3. Improve Route Planning Strategies:
   - 14 routes exhibit >20% delayed shipments, led by RT_13 (54.55% late) and RT_05 (40.00% late).
   - Dynamically recalculate Promised Delivery Dates (EDDs) to include realistic traffic buffers.
*/


-- =====================================================================
-- Task 4: Warehouse Performance (10 Marks)
-- =====================================================================

-- 1. Find the top 3 warehouses with the highest average processing time.
SELECT 
    Warehouse_ID,
    Warehouse_Name,
    Average_Processing_Time_Min 
FROM flipkart_warehouses 
ORDER BY Average_Processing_Time_Min DESC 
LIMIT 3;


-- 2. Calculate total vs. delayed shipments for each warehouse.
SELECT 
    Warehouse_ID,
    COUNT(*) AS Total_Shipments,
    COUNT(CASE WHEN Actual_Delivery_Date > Expected_Delivery_Date THEN 1 END) AS Delayed_Shipments 
FROM flipkart_orders 
GROUP BY Warehouse_ID;


-- 3. Use CTEs to find bottleneck warehouses where processing time > global average.
WITH Avg_Processing AS (
    SELECT AVG(Average_Processing_Time_Min) AS Global_Average 
    FROM flipkart_warehouses
)
SELECT 
    w.Warehouse_ID,
    w.Warehouse_Name,
    w.Average_Processing_Time_Min,
    ROUND(a.Global_Average, 2) AS Global_Average 
FROM flipkart_warehouses w, Avg_Processing a 
WHERE w.Average_Processing_Time_Min > a.Global_Average
ORDER BY w.Average_Processing_Time_Min DESC;


-- 4. Rank warehouses based on on-time delivery percentage.
SELECT 
    Warehouse_ID,
    ROUND((SUM(CASE WHEN Actual_Delivery_Date <= Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS on_time_percentage,
    RANK() OVER (
        ORDER BY (SUM(CASE WHEN Actual_Delivery_Date <= Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0) / COUNT(*) DESC
    ) AS warehouse_rank 
FROM flipkart_orders 
GROUP BY Warehouse_ID;


-- =====================================================================
-- Task 5: Delivery Agent Performance (10 Marks)
-- =====================================================================

-- 1. Rank agents (per route) by on-time delivery percentage.
SELECT 
    Agent_ID,
    Route_ID,
    On_Time_Delivery_Percentage,
    RANK() OVER (
        PARTITION BY Route_ID 
        ORDER BY On_Time_Delivery_Percentage DESC
    ) AS Agent_Rank 
FROM flipkart_deliveryagents;


-- 2. Find agents with on-time % < 80%.
SELECT 
    a.Agent_ID,
    a.Agent_Name,
    ROUND((SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS on_time_percentage 
FROM flipkart_orders o
INNER JOIN flipkart_deliveryagents a ON a.Agent_ID = o.Agent_ID 
GROUP BY a.Agent_ID, a.Agent_Name 
HAVING on_time_percentage < 80
ORDER BY on_time_percentage ASC;


-- 3. Compare average speed of top 5 vs bottom 5 agents using subqueries.
SELECT 'Top 5' AS Category, ROUND(AVG(Avg_Speed_KMPH), 2) AS avg_speed 
FROM (
    SELECT a.Agent_ID, a.Avg_Speed_KMPH
    FROM flipkart_orders o
    JOIN flipkart_deliveryagents a ON o.Agent_ID = a.Agent_ID
    GROUP BY a.Agent_ID, a.Avg_Speed_KMPH
    ORDER BY (SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) DESC
    LIMIT 5
) AS top_agents

UNION ALL

SELECT 'Bottom 5' AS Category, ROUND(AVG(Avg_Speed_KMPH), 2) AS avg_speed 
FROM (
    SELECT a.Agent_ID, a.Avg_Speed_KMPH
    FROM flipkart_orders o
    JOIN flipkart_deliveryagents a ON o.Agent_ID = a.Agent_ID
    GROUP BY a.Agent_ID, a.Avg_Speed_KMPH
    ORDER BY (SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) ASC
    LIMIT 5
) AS bottom_agents;


-- 4. Suggest training or workload balancing strategies for low performers.
/*
STRATEGIES FOR LOW PERFORMING AGENTS:
1. Driver Navigation & Time Management Coaching: Conduct refresher training on high-density urban route navigation and parcel sorting prior to dispatch.
2. Dynamic Workload Rebalancing: Avoid overloading agents assigned to high-congestion corridors; balance parcel counts based on traffic severity.
3. Micro-Routing & Real-Time Telematics: Integrate GPS dispatch apps that dynamically steer drivers away from localized traffic bottlenecks.
4. Early Intervention Monitoring: Implement supervisor alerting when an agent falls below 85% on-time completion within a rolling 7-day period.
5. Performance Incentive Programs: Provide tier-based monthly fuel or attendance bonuses for maintaining >90% on-time delivery.
*/


-- =====================================================================
-- Task 6: Shipment Tracking Analytics (10 Marks)
-- =====================================================================

-- 1. For each order, list the last checkpoint and time.
SELECT 
    t.Order_ID,
    t.Checkpoint,
    t.Checkpoint_Time AS last_checkpoint 
FROM flipkart_shipmenttracking t 
INNER JOIN (
    SELECT Order_ID, MAX(Checkpoint_Time) AS Last_Checkpoint 
    FROM flipkart_shipmenttracking 
    GROUP BY Order_ID
) m ON t.Order_ID = m.Order_ID AND t.Checkpoint_Time = m.Last_Checkpoint;


-- 2. Find the most common delay reasons (excluding None).
SELECT 
    Delay_Reason,
    COUNT(*) AS Frequency 
FROM flipkart_shipmenttracking 
WHERE Delay_Reason != 'None' AND Delay_Reason IS NOT NULL 
GROUP BY Delay_Reason 
ORDER BY Frequency DESC;


-- 3. Identify orders with >2 delayed checkpoints.
SELECT 
    Order_ID,
    COUNT(*) AS Delay_Frequency 
FROM flipkart_shipmenttracking 
WHERE Delay_Reason != 'None' AND Delay_Reason IS NOT NULL 
GROUP BY Order_ID 
HAVING Delay_Frequency > 2
ORDER BY Delay_Frequency DESC;


-- =====================================================================
-- Task 7: Advanced KPI Reporting (10 Marks)
-- =====================================================================

-- 1. Average Delivery Delay per Region (Start_Location).
SELECT 
    r.Start_Location,
    ROUND(AVG(DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date)), 2) AS avg_delay 
FROM flipkart_orders o 
INNER JOIN flipkart_routes r ON r.Route_ID = o.Route_ID 
GROUP BY r.Start_Location
ORDER BY avg_delay DESC;


-- 2. On-Time Delivery % = (Total On-Time Deliveries / Total Deliveries) * 100.
SELECT 
    ROUND((SUM(CASE WHEN Actual_Delivery_Date <= Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS On_Time_Percentage 
FROM flipkart_orders;


-- 3. Average Traffic Delay per Route.
SELECT 
    Route_ID,
    ROUND(AVG(Traffic_Delay_Min), 2) AS Average_Traffic_Delay 
FROM flipkart_routes 
GROUP BY Route_ID
ORDER BY Average_Traffic_Delay DESC;