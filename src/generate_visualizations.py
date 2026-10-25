#!/usr/bin/env python3
"""
Logistics Optimization for Delivery Routes - Flipkart
Automated High-Resolution Visualizations Generator

Author: Sujal Agrahari
License: MIT
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Configure matplotlib style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

# Flipkart Brand Color Palette
FLIPKART_BLUE = "#2874F0"
FLIPKART_YELLOW = "#FFE500"
DARK_NAVY = "#172337"
ACCENT_RED = "#FB641B"
ACCENT_GREEN = "#388E3C"
MUTED_GRAY = "#878787"


def generate_all_charts(base_dir: str):
    dataset_dir = os.path.join(base_dir, "datasets")
    viz_dir = os.path.join(base_dir, "visualizations")
    os.makedirs(viz_dir, exist_ok=True)

    # Load datasets
    orders = pd.read_csv(os.path.join(dataset_dir, "Flipkart_Orders.csv"))
    routes = pd.read_csv(os.path.join(dataset_dir, "Flipkart_Routes.csv"))
    warehouses = pd.read_csv(os.path.join(dataset_dir, "Flipkart_Warehouses.csv"))
    agents = pd.read_csv(os.path.join(dataset_dir, "Flipkart_DeliveryAgents.csv"))
    tracking = pd.read_csv(os.path.join(dataset_dir, "Flipkart_ShipmentTracking.csv"), keep_default_na=False)

    orders["Order_Date"] = pd.to_datetime(orders["Order_Date"], format="%d-%m-%Y")
    orders["Expected_Delivery_Date"] = pd.to_datetime(orders["Expected_Delivery_Date"], format="%d-%m-%Y")
    orders["Actual_Delivery_Date"] = pd.to_datetime(orders["Actual_Delivery_Date"], format="%d-%m-%Y")
    orders["Delay_Days"] = (orders["Actual_Delivery_Date"] - orders["Expected_Delivery_Date"]).dt.days
    orders["Is_Delayed"] = orders["Delay_Days"] > 0

    print("Generating Flipkart Logistics analytical visualizations...")

    # -------------------------------------------------------------
    # Chart 1: Top 10 Delayed Routes (Avg Delay Days & Delayed %)
    # -------------------------------------------------------------
    route_delays = orders.groupby("Route_ID").agg(
        avg_delay=("Delay_Days", "mean"),
        total=("Order_ID", "count"),
        delayed=("Is_Delayed", "sum")
    ).reset_index()
    route_delays = route_delays.merge(routes[["Route_ID", "Start_Location", "End_Location", "Traffic_Delay_Min"]], on="Route_ID")
    route_delays["delayed_pct"] = (route_delays["delayed"] * 100.0 / route_delays["total"]).round(1)
    route_delays["Route_Label"] = route_delays["Route_ID"] + " (" + route_delays["Start_Location"].str[:3] + "→" + route_delays["End_Location"].str[:3] + ")"
    top_10 = route_delays.sort_values("avg_delay", ascending=False).head(10)

    fig, ax1 = plt.subplots(figsize=(11, 6), dpi=300)
    bars = ax1.bar(top_10["Route_Label"], top_10["avg_delay"], color=FLIPKART_BLUE, alpha=0.88, width=0.55, label="Avg Delay (Days)")
    ax1.set_ylabel("Average Delay (Days)", color=FLIPKART_BLUE, fontsize=12, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=FLIPKART_BLUE)
    ax1.set_ylim(0, max(top_10["avg_delay"]) * 1.25)

    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f"{h:.2f}d", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax2 = ax1.twinx()
    ax2.plot(top_10["Route_Label"], top_10["delayed_pct"], color=ACCENT_RED, marker="o", linewidth=2.5, markersize=7, label="Delayed %")
    ax2.set_ylabel("Delayed Shipments (%)", color=ACCENT_RED, fontsize=12, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=ACCENT_RED)
    ax2.set_ylim(0, 100)

    for i, txt in enumerate(top_10["delayed_pct"]):
        ax2.annotate(f"{txt:.0f}%", (i, txt), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=9, fontweight="bold", color=ACCENT_RED)

    plt.title("Top 10 Most Delayed Delivery Routes (Flipkart Operations)", fontsize=14, fontweight="bold", pad=15)
    ax1.set_xticks(range(len(top_10)))
    ax1.set_xticklabels(top_10["Route_Label"], rotation=30, ha="right", fontsize=10)
    fig.tight_layout()
    chart1_path = os.path.join(viz_dir, "01_top_delayed_routes.png")
    fig.savefig(chart1_path)
    plt.close()
    print(f"  [SAVED] {chart1_path}")

    # -------------------------------------------------------------
    # Chart 2: Warehouse Processing Time vs Global Benchmark
    # -------------------------------------------------------------
    wh_sorted = warehouses.sort_values("Average_Processing_Time_Min", ascending=True).copy()
    benchmark = warehouses["Average_Processing_Time_Min"].mean()
    colors = [ACCENT_RED if val > benchmark else ACCENT_GREEN for val in wh_sorted["Average_Processing_Time_Min"]]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    bars = ax.barh(wh_sorted["City"], wh_sorted["Average_Processing_Time_Min"], color=colors, height=0.6, alpha=0.9)
    ax.axvline(benchmark, color=DARK_NAVY, linestyle="--", linewidth=2, label=f"Global Benchmark ({benchmark:.1f} min)")

    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{int(w)} min", xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points", ha="left", va="center", fontsize=10, fontweight="bold")

    ax.set_xlabel("Average Processing Time (Minutes)", fontsize=12, fontweight="bold")
    ax.set_title("Warehouse Processing Time vs Benchmark (Bottleneck Detection)", fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="lower right", fontsize=10)
    ax.set_xlim(0, max(wh_sorted["Average_Processing_Time_Min"]) * 1.18)
    fig.tight_layout()
    chart2_path = os.path.join(viz_dir, "02_warehouse_processing_benchmark.png")
    fig.savefig(chart2_path)
    plt.close()
    print(f"  [SAVED] {chart2_path}")

    # -------------------------------------------------------------
    # Chart 3: Shipment Delay Reasons Breakdown (Donut Chart)
    # -------------------------------------------------------------
    delay_trk = tracking[tracking["Delay_Reason"] != "None"].copy()
    reason_counts = delay_trk["Delay_Reason"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 7), dpi=300)
    donut_colors = [FLIPKART_BLUE, "#00A859", ACCENT_RED]
    wedges, texts, autotexts = ax.pie(
        reason_counts,
        labels=reason_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=donut_colors,
        pctdistance=0.75,
        explode=[0.03, 0.03, 0.03],
        textprops={"fontsize": 11, "fontweight": "bold"}
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(11)

    # Draw center circle for donut effect
    centre_circle = plt.Circle((0, 0), 0.52, fc="white")
    ax.add_artist(centre_circle)
    ax.annotate(f"Total Incidents\n{len(delay_trk):,}", xy=(0, 0), ha="center", va="center", fontsize=12, fontweight="bold", color=DARK_NAVY)

    ax.set_title("Root Causes of In-Transit Shipment Delays (N=686)", fontsize=14, fontweight="bold", pad=15)
    fig.tight_layout()
    chart3_path = os.path.join(viz_dir, "03_shipment_delay_root_causes.png")
    fig.savefig(chart3_path)
    plt.close()
    print(f"  [SAVED] {chart3_path}")

    # -------------------------------------------------------------
    # Chart 4: Route Efficiency vs Traffic Delay
    # -------------------------------------------------------------
    routes["efficiency"] = routes["Distance_KM"] / routes["Average_Travel_Time_Min"]
    routes = routes.merge(route_delays[["Route_ID", "avg_delay", "delayed_pct"]], on="Route_ID")

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    scatter = ax.scatter(
        routes["Traffic_Delay_Min"],
        routes["efficiency"],
        s=routes["delayed_pct"] * 6,
        c=routes["avg_delay"],
        cmap="YlOrRd",
        alpha=0.85,
        edgecolor=DARK_NAVY,
        linewidth=1.2
    )

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Avg Delivery Delay (Days)", fontsize=11, fontweight="bold")

    # Annotate outlier / bottleneck routes
    for _, r in routes.iterrows():
        if r["efficiency"] < 1.15 or r["Traffic_Delay_Min"] > 70 or r["delayed_pct"] > 35:
            ax.annotate(r["Route_ID"], (r["Traffic_Delay_Min"], r["efficiency"]),
                        xytext=(5, 4), textcoords="offset points", fontsize=9, fontweight="bold")

    ax.set_xlabel("Traffic Delay (Minutes)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Efficiency Ratio (Distance KM / Travel Time Min)", fontsize=12, fontweight="bold")
    ax.set_title("Route Transit Efficiency vs. Traffic Delay (Bubble size = Delayed %)", fontsize=14, fontweight="bold", pad=15)
    fig.tight_layout()
    chart4_path = os.path.join(viz_dir, "04_route_efficiency_vs_traffic.png")
    fig.savefig(chart4_path)
    plt.close()
    print(f"  [SAVED] {chart4_path}")

    # -------------------------------------------------------------
    # Chart 5: Delivery Agent Speed vs On-Time Performance Quadrant
    # -------------------------------------------------------------
    agent_orders = orders.groupby("Agent_ID").agg(
        actual_ontime=("Is_Delayed", lambda s: (~s).mean() * 100),
        order_count=("Order_ID", "count")
    ).reset_index()
    agent_perf = agents.merge(agent_orders, on="Agent_ID")

    avg_speed = agent_perf["Avg_Speed_KMPH"].mean()
    avg_ontime = agent_perf["actual_ontime"].mean()

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.scatter(agent_perf["Avg_Speed_KMPH"], agent_perf["actual_ontime"],
               s=agent_perf["order_count"] * 18, color=FLIPKART_BLUE, alpha=0.75, edgecolors=DARK_NAVY, linewidth=1)

    ax.axvline(avg_speed, color=MUTED_GRAY, linestyle="--", linewidth=1.2, label=f"Avg Speed ({avg_speed:.1f} km/h)")
    ax.axhline(avg_ontime, color=MUTED_GRAY, linestyle=":", linewidth=1.2, label=f"Avg On-Time ({avg_ontime:.1f}%)")

    # Quadrant labels
    ax.text(avg_speed + 2, 95, "High Speed / High On-Time\n(Elite Performers)", color=ACCENT_GREEN, fontweight="bold", fontsize=10)
    ax.text(avg_speed - 12, 45, "Low Speed / Low On-Time\n(Requires Coaching/Rebalancing)", color=ACCENT_RED, fontweight="bold", fontsize=10)

    ax.set_xlabel("Average Speed (km/h)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Actual On-Time Delivery Rate (%)", fontsize=12, fontweight="bold")
    ax.set_title("Delivery Agent Performance Matrix (Speed vs Reliability)", fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="lower right", fontsize=10)
    fig.tight_layout()
    chart5_path = os.path.join(viz_dir, "05_agent_speed_vs_ontime.png")
    fig.savefig(chart5_path)
    plt.close()
    print(f"  [SAVED] {chart5_path}")

    print("\nAll 5 high-resolution visualizations successfully generated!")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generate_all_charts(base_dir)
