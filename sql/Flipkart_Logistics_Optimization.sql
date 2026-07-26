use sqlproject;
select * from flipkart_deliveryagents;
select * from flipkart_orders;
select * from flipkart_routes;
select * from flipkart_shipmenttracking;
select * from flipkart_warehouses;



-- Task 1: Data Cleaning & Preparation
-- Identify and delete duplicate Order_ID records.
SELECT Order_ID, COUNT(*) AS count FROM flipkart_orders GROUP BY Order_ID HAVING COUNT(*) > 1; #No Duplicate values found as Order_id is working as a Primary Key.

-- Replace null Traffic_Delay_Min with the average delay for that route.
SET SQL_SAFE_UPDATES = 0;
UPDATE flipkart_routes r JOIN (SELECT Route_ID,AVG(Traffic_Delay_Min) AS avg_delay FROM flipkart_routes GROUP BY Route_ID) t ON r.Route_ID = t.Route_ID SET r.Traffic_Delay_Min = t.avg_delay
WHERE r.Traffic_Delay_Min IS NULL;

-- Convert all date columns into YYYY-MM-DD format using SQL functions.
SELECT order_date FROM flipkart_orders LIMIT 5;
describe flipkart_orders;
UPDATE flipkart_orders SET order_date = STR_TO_DATE(order_date, '%d-%m-%Y');
UPDATE flipkart_orders SET Expected_Delivery_Date = STR_TO_DATE(Expected_Delivery_Date, '%d-%m-%Y');
UPDATE flipkart_orders SET Actual_Delivery_Date = STR_TO_DATE(Actual_Delivery_Date, '%d-%m-%Y');

-- Ensure that no Actual_Delivery_Date is before Order_Date (flag such records).
SELECT *,CASE WHEN Actual_Delivery_Date < Order_Date THEN 'Invalid' ELSE 'Valid' END AS delivery_flag FROM flipkart_orders;



-- Task 2: Delivery Delay Analysis
-- Calculate delivery delay (in days) for each order
select Order_ID,datediff(Actual_Delivery_Date,Expected_Delivery_Date) as delivery_delay from flipkart_orders;

-- Find Top 10 delayed routes based on average delay days.
SELECT Route_ID,AVG(DATEDIFF(Actual_Delivery_Date,Expected_Delivery_Date)) AS avg_delay FROM flipkart_orders GROUP BY Route_ID ORDER BY avg_delay DESC LIMIT 10;

-- Use window functions to rank all orders by delay within each warehouse.
select Order_ID,Warehouse_ID,DATEDIFF(Actual_Delivery_Date,Expected_Delivery_Date) as delivery_delay,rank() over 
(partition by Warehouse_ID order by DATEDIFF(Actual_Delivery_Date,Expected_Delivery_Date) DESC) as Warehouse_rank from flipkart_orders;



-- Task 3: Route Optimization Insights
-- For each route, calculate: Average delivery time (in days), Average traffic delay, Distance-to-time efficiency ratio: Distance_KM / Average_Travel_Time_Min.
SELECT r.Route_ID,AVG(DATEDIFF(o.Actual_Delivery_Date, o.Order_Date)) AS avg_delivery_time,AVG(r.Traffic_Delay_Min) AS avg_traffic_delay,
AVG(r.Distance_KM / r.Average_Travel_Time_Min) AS efficiency_ratio FROM flipkart_orders o JOIN flipkart_routes r ON r.Route_ID = o.Route_ID GROUP BY r.Route_ID;

-- Identify 3 routes with the worst efficiency ratio.
select Route_ID,avg(Distance_KM/Average_Travel_Time_Min) AS efficiency_ratio from flipkart_routes group by Route_ID order by efficiency_ratio ASC limit 3;

-- Find routes with >20% delayed shipments.
select Route_ID,count(CASE WHEN Actual_Delivery_Date>Expected_Delivery_Date Then 1 END)*100/count(*) as Delayed_Shipments from flipkart_orders group by Route_ID having 
Delayed_Shipments > 20;

-- Recommend potential routes for optimization.
/* 
1. Optimize Low-efficiency Routes : Routes with lower distance-to-time ratio depict slower movement in those areas.
2. Manages High-Traffic Areas : Areas with higher Traffic delay impact negatively towards the delivery time.
3. Improve Route Planning Strategies : High delay percent indicates inadequete delivery route planning
-> Routes exhibiting a combination of low efficiency ratios, high traffic delays, and elevated delayed shipment percentages were identified as critical bottlenecks. These 
   Routes should be focused on more to be optimized more.    
*/



-- Task 4: Warehouse Performance
-- Find the top 3 warehouses with the highest average processing time.
select Warehouse_ID,Warehouse_Name,Average_Processing_Time_Min from flipkart_Warehouses order by Average_Processing_Time_Min DESC limit 3;

-- Calculate total vs. delayed shipments for each warehouse.
select Warehouse_ID,count(*) as Total_Shipments,count(CASE WHEN Actual_Delivery_Date>Expected_Delivery_Date Then 1 END) as Delayed_Shipments from flipkart_orders group by 
Warehouse_ID;

-- Use CTEs to find bottleneck warehouses where processing time > global average.
with Avg_Processing as (select avg(Average_Processing_Time_Min) as Global_Average from flipkart_warehouses)
select Warehouse_ID,Average_Processing_Time_Min from flipkart_warehouses, Avg_Processing where Average_Processing_Time_Min>Global_Average;

-- Rank warehouses based on on-time delivery percentage.
SELECT Warehouse_ID,(SUM(CASE WHEN Actual_Delivery_Date <= Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0) / COUNT(*) AS on_time_percentage,RANK() OVER 
(ORDER BY (SUM(CASE WHEN Actual_Delivery_Date <= Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0) / COUNT(*) DESC) AS warehouse_rank FROM flipkart_orders GROUP BY Warehouse_ID;



-- Task 5: Delivery Agent Performance
-- Rank agents (per route) by on-time delivery percentage
select Agent_ID,Route_ID,On_Time_Delivery_Percentage,rank() over (partition by route_ID order by On_Time_Delivery_Percentage DESC) as Agent_Rank 
from flipkart_deliveryagents;

-- Find agents with on-time % < 80%.
select a.Agent_ID,a.Agent_name,(SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0) / COUNT(*) AS on_time_percentage from flipkart_orders o
inner join flipkart_deliveryagents a on a.Agent_ID = o.Agent_ID group by a.Agent_ID,a.Agent_name having on_time_percentage<80;

-- Compare average speed of top 5 vs bottom 5 agents using subqueries.
with agent_performance as (select o.Agent_ID,ROUND(SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as on_time_pct 
from flipkart_orders o group by o.Agent_ID),ranked as (select p.Agent_ID,a.Avg_Speed_KMPH,p.on_time_pct,rank() over (order by p.on_time_pct DESC) as top_rank,rank() 
over (order by p.on_time_pct ASC) as bottom_rank from agent_performance p inner join flipkart_deliveryagents a on p.Agent_ID = a.Agent_ID)

select 'Top 5' as Category,ROUND(avg(Avg_Speed_KMPH), 2) as avg_speed from ranked where top_rank <= 5 #TOP 5
union all
select 'Bottom 5',ROUND(avg(Avg_Speed_KMPH), 2) from ranked where bottom_rank <= 5; #BOTTOM 5

-- Suggest training or workload balancing strategies for low performers
/*
1.Agents with low performance can be trained to do proper time management to improve scheduling and prioritisation.
2.Uneven workload distribution can impact agent performance. balancing delivery assignments across agents(based on their performance and workload) can reduce delays and 
improve overall efficiency.
3.Route optimisation of the delivery route can increase the performance of the low performing agents and also improve the high performing agents as well.
4.Continous performance monitoring can help identify the low performing agents early on leading to early actions taken to solve the problem.
5.Implementing performance based incentive bonuses can cause more motivation to perform high among the agents.
*/



-- Task 6: Shipment Tracking Analytics
-- For each order, list the last checkpoint and time.
select t.Order_ID,t.Checkpoint,t.Checkpoint_Time as last_checkpoint from flipkart_shipmenttracking t inner join (select Order_ID,max(Checkpoint_Time) as Last_Checkpoint from
flipkart_shipmenttracking group by Order_ID) m on t.Order_ID = m.Order_ID and t.Checkpoint_Time = m.Last_Checkpoint;

-- Find the most common delay reasons (excluding None).
select Delay_Reason,count(*) as Frequency from flipkart_shipmenttracking where Delay_Reason != 'None' group by Delay_Reason order by Frequency DESC;

-- Identify orders with >2 delayed checkpoints
select Order_ID,Count(*) as Delay_Frequency from flipkart_shipmenttracking where delay_reason != 'None' group by Order_ID having Delay_Frequency>2;


-- Task 7: Advanced KPI Reporting
-- Calculate KPIs using SQL queries:
-- Average Delivery Delay per Region (Start_Location).
select r.Start_Location,Avg(datediff(o.Actual_Delivery_Date,o.Expected_Delivery_Date)) as avg_delay from flipkart_orders o inner join flipkart_routes r on r.Route_ID = o.Route_ID
group by r.Start_Location;

-- On-Time Delivery % = (Total On-Time Deliveries / Total Deliveries) * 100.
select (SUM(CASE WHEN Actual_Delivery_Date <= Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as On_Time_Percentage from flipkart_orders;

-- Average Traffic Delay per Route.
select Route_ID,avg(Traffic_Delay_Min) as Average_Traffic_Delay from flipkart_routes group by Route_ID;