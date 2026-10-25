"""
Unit & Data Integrity Tests for Flipkart Logistics Optimization

Author: Sujal Agrahari
License: MIT
"""

import os
import sys
import pytest
import pandas as pd
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from run_analysis import init_database, run_pipeline


@pytest.fixture(scope="module")
def dataset_paths():
    data_dir = os.path.join(BASE_DIR, "datasets")
    return {
        "orders": os.path.join(data_dir, "Flipkart_Orders.csv"),
        "routes": os.path.join(data_dir, "Flipkart_Routes.csv"),
        "warehouses": os.path.join(data_dir, "Flipkart_Warehouses.csv"),
        "agents": os.path.join(data_dir, "Flipkart_DeliveryAgents.csv"),
        "tracking": os.path.join(data_dir, "Flipkart_ShipmentTracking.csv"),
        "dir": data_dir
    }


@pytest.fixture(scope="module")
def db_conn(dataset_paths):
    conn = init_database(dataset_paths["dir"])
    yield conn
    conn.close()


def test_dataset_existence_and_shapes(dataset_paths):
    """Ensure all required datasets exist and have expected dimensions."""
    orders = pd.read_csv(dataset_paths["orders"])
    routes = pd.read_csv(dataset_paths["routes"])
    warehouses = pd.read_csv(dataset_paths["warehouses"])
    agents = pd.read_csv(dataset_paths["agents"])
    tracking = pd.read_csv(dataset_paths["tracking"])

    assert len(orders) == 300, "Orders dataset should have 300 records"
    assert len(routes) == 20, "Routes dataset should have 20 records"
    assert len(warehouses) == 10, "Warehouses dataset should have 10 records"
    assert len(agents) == 50, "Delivery agents dataset should have 50 records"
    assert len(tracking) == 1000, "Shipment tracking dataset should have 1000 records"


def test_primary_key_uniqueness(dataset_paths):
    """Verify that primary keys across all entities are strictly unique."""
    orders = pd.read_csv(dataset_paths["orders"])
    routes = pd.read_csv(dataset_paths["routes"])
    warehouses = pd.read_csv(dataset_paths["warehouses"])
    agents = pd.read_csv(dataset_paths["agents"])
    tracking = pd.read_csv(dataset_paths["tracking"])

    assert orders["Order_ID"].is_unique, "Order_ID must be unique"
    assert routes["Route_ID"].is_unique, "Route_ID must be unique"
    assert warehouses["Warehouse_ID"].is_unique, "Warehouse_ID must be unique"
    assert agents["Agent_ID"].is_unique, "Agent_ID must be unique"
    assert tracking["Tracking_ID"].is_unique, "Tracking_ID must be unique"


def test_foreign_key_referential_integrity(dataset_paths):
    """Verify foreign key relationships."""
    orders = pd.read_csv(dataset_paths["orders"])
    routes = pd.read_csv(dataset_paths["routes"])
    warehouses = pd.read_csv(dataset_paths["warehouses"])
    agents = pd.read_csv(dataset_paths["agents"])

    valid_warehouses = set(warehouses["Warehouse_ID"])
    valid_routes = set(routes["Route_ID"])
    valid_agents = set(agents["Agent_ID"])

    assert set(orders["Warehouse_ID"]).issubset(valid_warehouses), "Invalid Warehouse_ID found in orders"
    assert set(orders["Route_ID"]).issubset(valid_routes), "Invalid Route_ID found in orders"
    assert set(orders["Agent_ID"]).issubset(valid_agents), "Invalid Agent_ID found in orders"
    assert set(agents["Route_ID"]).issubset(valid_routes), "Invalid Route_ID found in delivery agents"


def test_date_logical_integrity(dataset_paths):
    """Verify delivery dates never precede order dates."""
    orders = pd.read_csv(dataset_paths["orders"])
    order_dt = pd.to_datetime(orders["Order_Date"], format="%d-%m-%Y")
    act_dt = pd.to_datetime(orders["Actual_Delivery_Date"], format="%d-%m-%Y")

    anomalies = orders[act_dt < order_dt]
    assert len(anomalies) == 0, f"Found {len(anomalies)} orders where Actual Delivery preceded Order Date"


def test_kpi_calculations(db_conn):
    """Verify baseline operational KPIs."""
    results = run_pipeline(db_conn)

    kpi = results["task7_kpi_scorecard"].iloc[0]
    assert kpi["total_orders"] == 300
    assert kpi["overall_ontime_rate_pct"] == pytest.approx(72.67, abs=0.1)
    assert kpi["overall_delayed_rate_pct"] == pytest.approx(27.33, abs=0.1)
    assert kpi["avg_turnaround_days"] == pytest.approx(4.51, abs=0.1)


def test_warehouse_bottlenecks(db_conn):
    """Verify that WH_10 is identified as the highest processing time warehouse."""
    results = run_pipeline(db_conn)
    wh_df = results["task4_warehouse_performance"]

    top_bottleneck = wh_df.iloc[0]
    assert top_bottleneck["Warehouse_ID"] == "WH_10"
    assert top_bottleneck["Average_Processing_Time_Min"] == 117
