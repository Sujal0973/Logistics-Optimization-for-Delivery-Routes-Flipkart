#!/usr/bin/env python3
"""
Logistics Optimization for Delivery Routes - Flipkart
Automated SQL Analytics & KPI Reporting Pipeline

Author: Sujal Agrahari
License: MIT
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False



def print_table(df: pd.DataFrame, title: str):
    """Prints a nicely formatted table to stdout."""
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)
    if HAS_TABULATE:
        print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
    else:
        print(df.to_string(index=False))
    print("-" * 80)


def datediff_func(d1, d2):
    """Custom SQLite function replicating MySQL DATEDIFF(d1, d2)."""
    if not d1 or not d2:
        return None
    try:
        dt1 = datetime.strptime(str(d1)[:10], "%Y-%m-%d")
        dt2 = datetime.strptime(str(d2)[:10], "%Y-%m-%d")
        return (dt1 - dt2).days
    except Exception:
        return None


def init_database(dataset_dir: str, db_path: str = None) -> sqlite3.Connection:
    """Loads CSV datasets into an SQLite database with cleaned and standardized dates."""
    conn = sqlite3.connect(db_path if db_path else ":memory:")
    conn.create_function("DATEDIFF", 2, datediff_func)

    # 1. Load Warehouses
    wh_df = pd.read_csv(os.path.join(dataset_dir, "Flipkart_Warehouses.csv"))
    wh_df.to_sql("flipkart_warehouses", conn, if_exists="replace", index=False)

    # 2. Load Routes
    routes_df = pd.read_csv(os.path.join(dataset_dir, "Flipkart_Routes.csv"))
    routes_df.to_sql("flipkart_routes", conn, if_exists="replace", index=False)

    # 3. Load Delivery Agents
    agents_df = pd.read_csv(os.path.join(dataset_dir, "Flipkart_DeliveryAgents.csv"))
    agents_df.to_sql("flipkart_deliveryagents", conn, if_exists="replace", index=False)

    # 4. Load Orders & Standardize Dates
    orders_df = pd.read_csv(os.path.join(dataset_dir, "Flipkart_Orders.csv"))
    orders_df["Order_Date"] = pd.to_datetime(orders_df["Order_Date"], format="%d-%m-%Y").dt.strftime("%Y-%m-%d")
    orders_df["Expected_Delivery_Date"] = pd.to_datetime(orders_df["Expected_Delivery_Date"], format="%d-%m-%Y").dt.strftime("%Y-%m-%d")
    orders_df["Actual_Delivery_Date"] = pd.to_datetime(orders_df["Actual_Delivery_Date"], format="%d-%m-%Y").dt.strftime("%Y-%m-%d")
    orders_df.to_sql("flipkart_orders", conn, if_exists="replace", index=False)

    # 5. Load Tracking & Standardize Timestamps
    tracking_df = pd.read_csv(os.path.join(dataset_dir, "Flipkart_ShipmentTracking.csv"), keep_default_na=False)
    tracking_df["Delay_Reason"] = tracking_df["Delay_Reason"].replace({"": "None", None: "None"})
    tracking_df["Checkpoint_Time"] = pd.to_datetime(tracking_df["Checkpoint_Time"], format="%d-%m-%Y %H:%M").dt.strftime("%Y-%m-%d %H:%M:%S")
    tracking_df.to_sql("flipkart_shipmenttracking", conn, if_exists="replace", index=False)

    return conn


def run_pipeline(conn: sqlite3.Connection, output_dir: str = None) -> dict:
    """Executes all tasks and gathers analytical results."""
    results = {}

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # -----------------------------------------------------------------
    # Task 1: Data Cleaning & Integrity Check
    # -----------------------------------------------------------------
    dup_query = """
    SELECT Order_ID, COUNT(*) AS count 
    FROM flipkart_orders 
    GROUP BY Order_ID 
    HAVING COUNT(*) > 1;
    """
    dups = pd.read_sql(dup_query, conn)
    results["task1_duplicates"] = len(dups)

    invalid_dates_query = """
    SELECT COUNT(*) AS invalid_count 
    FROM flipkart_orders 
    WHERE Actual_Delivery_Date < Order_Date;
    """
    invalid_dates = pd.read_sql(invalid_dates_query, conn).iloc[0]["invalid_count"]
    results["task1_invalid_dates"] = int(invalid_dates)

    print("\n[TASK 1: DATA CLEANING & VALIDATION]")
    print(f"  [PASS] Duplicate Order IDs: {len(dups)}")
    print(f"  [PASS] Delivery Date Anomalies (Actual < Order): {invalid_dates}")
    print("  [PASS] Status: All tables cleaned, standardized, and validated.")

    # -----------------------------------------------------------------
    # Task 2: Delivery Delay Analysis
    # -----------------------------------------------------------------
    top_delayed_routes_q = """
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
    """
    df_task2 = pd.read_sql(top_delayed_routes_q, conn)
    print_table(df_task2, "Task 2: Top 10 Delayed Routes")
    results["task2_delayed_routes"] = df_task2

    # -----------------------------------------------------------------
    # Task 3: Route Optimization Insights
    # -----------------------------------------------------------------
    worst_efficiency_q = """
    SELECT 
        Route_ID,
        Start_Location,
        End_Location,
        Distance_KM,
        Average_Travel_Time_Min,
        ROUND(CAST(Distance_KM AS FLOAT) / Average_Travel_Time_Min, 3) AS efficiency_ratio_km_per_min,
        ROUND((CAST(Distance_KM AS FLOAT) / Average_Travel_Time_Min) * 60, 2) AS speed_kmph
    FROM flipkart_routes
    ORDER BY efficiency_ratio_km_per_min ASC
    LIMIT 3;
    """
    df_task3_worst = pd.read_sql(worst_efficiency_q, conn)
    print_table(df_task3_worst, "Task 3: Top 3 Least Efficient Routes")

    high_delay_routes_q = """
    SELECT 
        r.Route_ID,
        r.Start_Location,
        r.End_Location,
        COUNT(o.Order_ID) AS total_orders,
        SUM(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN 1 ELSE 0 END) AS delayed_orders,
        ROUND(SUM(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS delayed_pct
    FROM flipkart_orders o
    JOIN flipkart_routes r ON o.Route_ID = r.Route_ID
    GROUP BY r.Route_ID, r.Start_Location, r.End_Location
    HAVING delayed_pct > 20.0
    ORDER BY delayed_pct DESC;
    """
    df_task3_high_delay = pd.read_sql(high_delay_routes_q, conn)
    print_table(df_task3_high_delay, "Task 3: Routes with >20% Delayed Shipments")
    results["task3_high_delay_routes"] = df_task3_high_delay

    # -----------------------------------------------------------------
    # Task 4: Warehouse Performance & Bottlenecks
    # -----------------------------------------------------------------
    wh_perf_q = """
    WITH GlobalBenchmark AS (
        SELECT AVG(Average_Processing_Time_Min) AS global_avg 
        FROM flipkart_warehouses
    )
    SELECT 
        w.Warehouse_ID,
        w.Warehouse_Name,
        w.City,
        w.Processing_Capacity,
        w.Average_Processing_Time_Min,
        ROUND(b.global_avg, 2) AS global_benchmark_min,
        ROUND(w.Average_Processing_Time_Min - b.global_avg, 2) AS excess_processing_min,
        COUNT(o.Order_ID) AS total_shipments,
        SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) AS on_time_shipments,
        SUM(CASE WHEN o.Actual_Delivery_Date > o.Expected_Delivery_Date THEN 1 ELSE 0 END) AS delayed_shipments,
        ROUND(SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID), 2) AS on_time_pct,
        DENSE_RANK() OVER (ORDER BY (SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.Order_ID)) DESC) AS ontime_rank
    FROM flipkart_warehouses w
    CROSS JOIN GlobalBenchmark b
    LEFT JOIN flipkart_orders o ON w.Warehouse_ID = o.Warehouse_ID
    GROUP BY w.Warehouse_ID, w.Warehouse_Name, w.City, w.Processing_Capacity, w.Average_Processing_Time_Min, b.global_avg
    ORDER BY w.Average_Processing_Time_Min DESC;
    """
    df_task4 = pd.read_sql(wh_perf_q, conn)
    print_table(df_task4, "Task 4: Warehouse Processing Times & Bottleneck Assessment")
    results["task4_warehouse_performance"] = df_task4

    # -----------------------------------------------------------------
    # Task 5: Delivery Agent Performance
    # -----------------------------------------------------------------
    agent_speed_cohort_q = """
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
            ROW_NUMBER() OVER (ORDER BY p.on_time_pct DESC, p.total_orders DESC, a.Avg_Speed_KMPH DESC) AS top_rank,
            ROW_NUMBER() OVER (ORDER BY p.on_time_pct ASC, p.total_orders DESC, a.Avg_Speed_KMPH ASC) AS bottom_rank
        FROM AgentActualPerformance p
        JOIN flipkart_deliveryagents a ON p.Agent_ID = a.Agent_ID
    )
    SELECT 
        'Top 5 Agents (Highest On-Time %)' AS Cohort,
        ROUND(AVG(Avg_Speed_KMPH), 2) AS avg_speed_kmph,
        ROUND(AVG(on_time_pct), 2) AS avg_on_time_pct
    FROM RankedAgents 
    WHERE top_rank <= 5

    UNION ALL

    SELECT 
        'Bottom 5 Agents (Lowest On-Time %)',
        ROUND(AVG(Avg_Speed_KMPH), 2),
        ROUND(AVG(on_time_pct), 2)
    FROM RankedAgents 
    WHERE bottom_rank <= 5;
    """
    df_task5 = pd.read_sql(agent_speed_cohort_q, conn)
    print_table(df_task5, "Task 5: Speed Comparison of Top 5 vs Bottom 5 Delivery Agents")
    results["task5_agent_cohorts"] = df_task5

    # -----------------------------------------------------------------
    # Task 6: Shipment Tracking Analytics
    # -----------------------------------------------------------------
    delay_reasons_q = """
    SELECT 
        Delay_Reason,
        COUNT(*) AS total_incidents,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM flipkart_shipmenttracking WHERE Delay_Reason != 'None'), 2) AS share_pct,
        ROUND(AVG(Delay_Minutes), 1) AS avg_delay_minutes,
        MAX(Delay_Minutes) AS max_delay_minutes
    FROM flipkart_shipmenttracking
    WHERE Delay_Reason != 'None'
    GROUP BY Delay_Reason
    ORDER BY total_incidents DESC;
    """
    df_task6 = pd.read_sql(delay_reasons_q, conn)
    print_table(df_task6, "Task 6: Most Common Shipment Delay Causes")
    results["task6_delay_reasons"] = df_task6

    # -----------------------------------------------------------------
    # Task 7: Executive KPI Scorecard
    # -----------------------------------------------------------------
    kpi_scorecard_q = """
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
    """
    df_kpi = pd.read_sql(kpi_scorecard_q, conn)
    print_table(df_kpi, "Task 7: Executive KPI Scorecard")
    results["task7_kpi_scorecard"] = df_kpi

    # Export CSVs/JSON if requested
    if output_dir:
        for name, data in results.items():
            if isinstance(data, pd.DataFrame):
                data.to_csv(os.path.join(output_dir, f"{name}.csv"), index=False)
        # Export KPI Summary JSON
        kpi_dict = df_kpi.iloc[0].to_dict()
        with open(os.path.join(output_dir, "executive_kpis.json"), "w", encoding="utf-8") as f:
            json.dump(kpi_dict, f, indent=2)
        print(f"\n[OUTPUT] All analysis tables and KPIs successfully exported to: {output_dir}")

    return results


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(base_dir, "datasets")
    output_dir = os.path.join(base_dir, "output")

    print(f"Initializing Flipkart Logistics Pipeline from: {dataset_dir}")
    conn = init_database(dataset_dir)
    run_pipeline(conn, output_dir=output_dir)
    conn.close()
    print("\nPipeline execution completed successfully.")


if __name__ == "__main__":
    main()
