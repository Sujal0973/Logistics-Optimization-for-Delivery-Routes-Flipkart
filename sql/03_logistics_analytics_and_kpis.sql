-- =====================================================================
-- Project: Logistics Optimization for Delivery Routes - Flipkart
-- File: 03_logistics_analytics_and_kpis.sql
-- Description: Advanced SQL analytics, window functions, CTEs, ranking,
--              and KPI reporting queries for Flipkart delivery operations.
-- =====================================================================

USE flipkart_logistics;

-- =====================================================================
-- TASK 2: DELIVERY DELAY ANALYSIS
-- =====================================================================

-- 2.1 Calculate delivery delay (in days) for each order
-- Positive values denote delayed deliveries; 0 or negative denotes on-time / early.
SELECT 
    o.Order_ID,
    o.Warehouse_ID,
    o.Route_ID,
    o.Agent_ID,
    o.Expected_Delivery_Date,
    o.Actual_Delivery_Date,
    DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date) AS delivery_delay_days,
    CASE 
        WHEN DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date) > 0 THEN 'Delayed'
        WHEN DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date) = 0 THEN 'On Time'
        ELSE 'Early'
    END AS delivery_status
FROM flipkart_orders o
ORDER BY delivery_delay_days DESC;

-- 2.2 Top 10 delayed routes based on average delay days
-- Enhanced with route metadata (origin, destination, distance, traffic delay)
SELECT 
    r.Route_ID,
    r.Start_Location,
    r.End_Location,
    r.Distance_KM,
    r.Traffic_Delay_Min,
    COUNT(o.Order_ID) AS total_orders,
    ROUND(AVG(DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date)), 2) AS avg_delay_days,
    SUM(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN 1 ELSE 0 END) AS delayed_orders,
    ROUND(SUM(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS delayed_pct
FROM flipkart_orders o
JOIN flipkart_routes r ON o.Route_ID = r.Route_ID
GROUP BY r.Route_ID, r.Start_Location, r.End_Location, r.Distance_KM, r.Traffic_Delay_Min
ORDER BY avg_delay_days DESC, delayed_pct DESC
LIMIT 10;

-- 2.3 Rank all orders by delay within each warehouse using Window Functions
SELECT 
    o.Order_ID,
    o.Warehouse_ID,
    w.Warehouse_Name,
    w.City,
    DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date) AS delivery_delay_days,
    RANK() OVER (
        PARTITION BY o.Warehouse_ID 
        ORDER BY DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date) DESC
    ) AS warehouse_delay_rank,
    DENSE_RANK() OVER (
        PARTITION BY o.Warehouse_ID 
        ORDER BY DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date) DESC
    ) AS warehouse_dense_delay_rank
FROM flipkart_orders o
JOIN flipkart_warehouses w ON o.Warehouse_ID = w.Warehouse_ID
ORDER BY o.Warehouse_ID, warehouse_delay_rank ASC;


-- =====================================================================
-- TASK 3: ROUTE OPTIMIZATION INSIGHTS
-- =====================================================================

-- 3.1 Route Performance Metrics:
-- Turnaround Time, Traffic Delay, and Distance-to-Time Efficiency Ratio
SELECT 
    r.Route_ID,
    r.Start_Location,
    r.End_Location,
    r.Distance_KM,
    r.Average_Travel_Time_Min,
    r.Traffic_Delay_Min,
    ROUND(AVG(DATEDIFF(o.Actual_Delivery_Date, o.Order_Date)), 2) AS avg_delivery_turnaround_days,
    ROUND(r.Distance_KM / r.Average_Travel_Time_Min, 3) AS efficiency_ratio_km_per_min,
    ROUND((r.Distance_KM / r.Average_Travel_Time_Min) * 60, 2) AS effective_speed_kmph
FROM flipkart_routes r
LEFT JOIN flipkart_orders o ON r.Route_ID = o.Route_ID
GROUP BY r.Route_ID, r.Start_Location, r.End_Location, r.Distance_KM, r.Average_Travel_Time_Min, r.Traffic_Delay_Min
ORDER BY efficiency_ratio_km_per_min ASC;

-- 3.2 Identify 3 routes with the worst efficiency ratio
SELECT 
    Route_ID,
    Start_Location,
    End_Location,
    Distance_KM,
    Average_Travel_Time_Min,
    ROUND(Distance_KM / Average_Travel_Time_Min, 3) AS efficiency_ratio,
    ROUND((Distance_KM / Average_Travel_Time_Min) * 60, 2) AS speed_kmph
FROM flipkart_routes
ORDER BY efficiency_ratio ASC
LIMIT 3;

-- 3.3 Find routes with > 20% delayed shipments
SELECT 
    r.Route_ID,
    r.Start_Location,
    r.End_Location,
    COUNT(o.Order_ID) AS total_shipments,
    SUM(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN 1 ELSE 0 END) AS delayed_shipments,
    ROUND(SUM(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS delayed_shipment_pct
FROM flipkart_orders o
JOIN flipkart_routes r ON o.Route_ID = r.Route_ID
GROUP BY r.Route_ID, r.Start_Location, r.End_Location
HAVING delayed_shipment_pct > 20.00
ORDER BY delayed_shipment_pct DESC;


-- =====================================================================
-- TASK 4: WAREHOUSE PERFORMANCE
-- =====================================================================

-- 4.1 Top 3 warehouses with the highest average processing time
SELECT 
    Warehouse_ID,
    Warehouse_Name,
    City,
    Processing_Capacity,
    Average_Processing_Time_Min
FROM flipkart_warehouses
ORDER BY Average_Processing_Time_Min DESC
LIMIT 3;

-- 4.2 Total vs. Delayed vs. On-time Shipments per Warehouse
SELECT 
    w.Warehouse_ID,
    w.Warehouse_Name,
    w.City,
    COUNT(o.Order_ID) AS total_shipments,
    SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) AS on_time_shipments,
    SUM(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN 1 ELSE 0 END) AS delayed_shipments,
    ROUND(SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS on_time_percentage,
    ROUND(SUM(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS delay_percentage
FROM flipkart_warehouses w
LEFT JOIN flipkart_orders o ON w.Warehouse_ID = o.Warehouse_ID
GROUP BY w.Warehouse_ID, w.Warehouse_Name, w.City
ORDER BY delay_percentage DESC;

-- 4.3 CTE: Identify bottleneck warehouses where processing time > global average
WITH GlobalBenchmark AS (
    SELECT AVG(Average_Processing_Time_Min) AS global_avg_processing
    FROM flipkart_warehouses
)
SELECT 
    w.Warehouse_ID,
    w.Warehouse_Name,
    w.City,
    w.Processing_Capacity,
    w.Average_Processing_Time_Min,
    ROUND(b.global_avg_processing, 2) AS global_avg_processing_min,
    ROUND(w.Average_Processing_Time_Min - b.global_avg_processing, 2) AS excess_processing_min,
    ROUND(((w.Average_Processing_Time_Min - b.global_avg_processing) / b.global_avg_processing) * 100, 2) AS pct_above_benchmark
FROM flipkart_warehouses w
CROSS JOIN GlobalBenchmark b
WHERE w.Average_Processing_Time_Min > b.global_avg_processing
ORDER BY w.Average_Processing_Time_Min DESC;

-- 4.4 Rank warehouses based on on-time delivery percentage
SELECT 
    w.Warehouse_ID,
    w.Warehouse_Name,
    w.City,
    COUNT(o.Order_ID) AS total_orders,
    ROUND(SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS on_time_percentage,
    DENSE_RANK() OVER (
        ORDER BY (SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID)) DESC
    ) AS warehouse_on_time_rank
FROM flipkart_warehouses w
JOIN flipkart_orders o ON w.Warehouse_ID = o.Warehouse_ID
GROUP BY w.Warehouse_ID, w.Warehouse_Name, w.City
ORDER BY warehouse_on_time_rank ASC;


-- =====================================================================
-- TASK 5: DELIVERY AGENT PERFORMANCE
-- =====================================================================

-- 5.1 Rank agents (per route) by historical On-Time Delivery Percentage
SELECT 
    Agent_ID,
    Agent_Name,
    Route_ID,
    Avg_Speed_KMPH,
    On_Time_Delivery_Percentage,
    Experience_Years,
    DENSE_RANK() OVER (
        PARTITION BY Route_ID 
        ORDER BY On_Time_Delivery_Percentage DESC
    ) AS agent_route_rank
FROM flipkart_deliveryagents
ORDER BY Route_ID, agent_route_rank ASC;

-- 5.2 Find agents with empirical On-Time % < 80% calculated from actual orders
SELECT 
    a.Agent_ID,
    a.Agent_Name,
    a.Route_ID,
    a.Avg_Speed_KMPH,
    a.Experience_Years,
    COUNT(o.Order_ID) AS total_orders_assigned,
    SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) AS on_time_orders,
    ROUND(SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS actual_on_time_pct
FROM flipkart_deliveryagents a
JOIN flipkart_orders o ON a.Agent_ID = o.Agent_ID
GROUP BY a.Agent_ID, a.Agent_Name, a.Route_ID, a.Avg_Speed_KMPH, a.Experience_Years
HAVING actual_on_time_pct < 80.00
ORDER BY actual_on_time_pct ASC, total_orders_assigned DESC;

-- 5.3 Compare average speed of Top 5 vs Bottom 5 agents using CTEs and ROW_NUMBER
WITH AgentActualPerformance AS (
    SELECT 
        o.Agent_ID,
        COUNT(o.Order_ID) AS total_orders,
        ROUND(SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS on_time_pct
    FROM flipkart_orders o
    GROUP BY o.Agent_ID
),
RankedAgents AS (
    SELECT 
        p.Agent_ID,
        a.Agent_Name,
        a.Avg_Speed_KMPH,
        p.on_time_pct,
        p.total_orders,
        -- Deterministic top & bottom ranking using ROW_NUMBER with secondary tiebreakers
        ROW_NUMBER() OVER (ORDER BY p.on_time_pct DESC, p.total_orders DESC, a.Avg_Speed_KMPH DESC) AS top_rank,
        ROW_NUMBER() OVER (ORDER BY p.on_time_pct ASC, p.total_orders DESC, a.Avg_Speed_KMPH ASC) AS bottom_rank
    FROM AgentActualPerformance p
    JOIN flipkart_deliveryagents a ON p.Agent_ID = a.Agent_ID
)
SELECT 
    'Top 5 Agents' AS Cohort,
    ROUND(AVG(Avg_Speed_KMPH), 2) AS avg_speed_kmph,
    ROUND(AVG(on_time_pct), 2) AS avg_on_time_pct
FROM RankedAgents 
WHERE top_rank <= 5

UNION ALL

SELECT 
    'Bottom 5 Agents' AS Cohort,
    ROUND(AVG(Avg_Speed_KMPH), 2) AS avg_speed_kmph,
    ROUND(AVG(on_time_pct), 2) AS avg_on_time_pct
FROM RankedAgents 
WHERE bottom_rank <= 5;


-- =====================================================================
-- TASK 6: SHIPMENT TRACKING ANALYTICS
-- =====================================================================

-- 6.1 For each order, list the latest checkpoint and timestamp
-- Fix: Using Window Function ROW_NUMBER() on chronological DATETIME ensures
-- 100% accuracy (preventing alphabetical string comparison anomalies).
WITH LatestCheckpoints AS (
    SELECT 
        t.Order_ID,
        t.Tracking_ID,
        t.Checkpoint,
        t.Checkpoint_Time,
        t.Delay_Reason,
        t.Delay_Minutes,
        ROW_NUMBER() OVER (
            PARTITION BY t.Order_ID 
            ORDER BY t.Checkpoint_Time DESC
        ) AS rn
    FROM flipkart_shipmenttracking t
)
SELECT 
    Order_ID,
    Tracking_ID,
    Checkpoint AS latest_checkpoint,
    Checkpoint_Time AS latest_checkpoint_time,
    Delay_Reason,
    Delay_Minutes
FROM LatestCheckpoints
WHERE rn = 1
ORDER BY Order_ID ASC;

-- 6.2 Most common delay reasons (excluding 'None' / On-time checkpoints)
SELECT 
    Delay_Reason,
    COUNT(*) AS total_incidents,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS share_of_delayed_checkpoints,
    ROUND(AVG(Delay_Minutes), 1) AS avg_delay_minutes_per_incident,
    MAX(Delay_Minutes) AS max_delay_minutes
FROM flipkart_shipmenttracking
WHERE Delay_Reason IS NOT NULL AND Delay_Reason != 'None'
GROUP BY Delay_Reason
ORDER BY total_incidents DESC;

-- 6.3 Identify orders with > 2 delayed checkpoints
SELECT 
    t.Order_ID,
    o.Warehouse_ID,
    o.Route_ID,
    COUNT(*) AS delayed_checkpoint_count,
    SUM(t.Delay_Minutes) AS cumulative_delay_minutes
FROM flipkart_shipmenttracking t
JOIN flipkart_orders o ON t.Order_ID = o.Order_ID
WHERE t.Delay_Reason IS NOT NULL AND t.Delay_Reason != 'None'
GROUP BY t.Order_ID, o.Warehouse_ID, o.Route_ID
HAVING delayed_checkpoint_count > 2
ORDER BY delayed_checkpoint_count DESC, cumulative_delay_minutes DESC;


-- =====================================================================
-- TASK 7: ADVANCED KPI REPORTING & EXECUTIVE SCORECARD
-- =====================================================================

-- 7.1 Average delivery delay per Region (Start_Location)
SELECT 
    r.Start_Location AS region,
    COUNT(o.Order_ID) AS total_orders,
    ROUND(AVG(DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date)), 2) AS avg_delivery_delay_days,
    ROUND(SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS on_time_rate_pct
FROM flipkart_orders o
JOIN flipkart_routes r ON o.Route_ID = r.Route_ID
GROUP BY r.Start_Location
ORDER BY avg_delivery_delay_days DESC;

-- 7.2 Overall On-Time Delivery Percentage
SELECT 
    COUNT(*) AS total_deliveries,
    SUM(CASE WHEN Actual_Delivery_Date <= Expected_Delivery_Date THEN 1 ELSE 0 END) AS on_time_deliveries,
    SUM(CASE WHEN Actual_Delivery_Date > Expected_Delivery_Date THEN 1 ELSE 0 END) AS delayed_deliveries,
    ROUND(SUM(CASE WHEN Actual_Delivery_Date <= Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS on_time_percentage
FROM flipkart_orders;

-- 7.3 Average Traffic Delay per Route
SELECT 
    Route_ID,
    Start_Location,
    End_Location,
    Traffic_Delay_Min AS recorded_traffic_delay_min,
    ROUND(AVG(Traffic_Delay_Min), 2) AS avg_traffic_delay_min
FROM flipkart_routes
GROUP BY Route_ID, Start_Location, End_Location, Traffic_Delay_Min
ORDER BY Traffic_Delay_Min DESC;

-- 7.4 Executive KPI Scorecard
SELECT 
    COUNT(o.Order_ID) AS total_orders,
    ROUND(SUM(o.Order_Value), 2) AS total_order_value_inr,
    ROUND(AVG(o.Order_Value), 2) AS avg_order_value_inr,
    ROUND(AVG(DATEDIFF(o.Actual_Delivery_Date, o.Order_Date)), 2) AS avg_turnaround_days,
    ROUND(SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS overall_ontime_rate_pct,
    ROUND(SUM(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS overall_delayed_rate_pct,
    ROUND(AVG(DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date)), 2) AS avg_delay_days_all_orders,
    ROUND(AVG(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date) END), 2) AS avg_delay_when_late_days
FROM flipkart_orders o;
