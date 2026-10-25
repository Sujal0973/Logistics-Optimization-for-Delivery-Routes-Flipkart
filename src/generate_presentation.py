#!/usr/bin/env python3
"""
Generate PowerPoint Presentation for Flipkart Logistics Optimization
Task 8 & 9 compliance for submission.

Author: Sujal Agrahari
License: MIT
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Theme Colors
NAVY = RGBColor(23, 35, 55)         # #172337
BLUE = RGBColor(40, 116, 240)       # #2874F0 Flipkart Blue
YELLOW = RGBColor(255, 230, 0)      # #FFE500 Flipkart Yellow
WHITE = RGBColor(255, 255, 255)
DARK_GRAY = RGBColor(60, 64, 67)
LIGHT_BG = RGBColor(245, 247, 250)
BORDER_GRAY = RGBColor(220, 224, 230)


def apply_header(slide, title_text, category_text="FLIPKART LOGISTICS OPTIMIZATION"):
    """Adds a consistent branded top banner to the slide."""
    # Top accent bar
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = BLUE
    top_bar.line.fill.background()

    # Category / Breadcrumb
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.3), Inches(11.5), Inches(0.3))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = BLUE

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(11.5), Inches(0.6))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = NAVY


def add_code_block(slide, left, top, width, height, code_text):
    """Adds a dark code block styling for SQL queries."""
    bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(30, 35, 45)
    bg.line.color.rgb = RGBColor(50, 60, 75)

    tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.1), width - Inches(0.3), height - Inches(0.2))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = code_text.strip()
    p.font.size = Pt(9.5)
    p.font.name = "Consolas"
    p.font.color.rgb = RGBColor(230, 240, 255)


def add_card(slide, left, top, width, height, title, body_lines):
    """Adds a styled white card with bullet points."""
    bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    bg.line.color.rgb = BORDER_GRAY

    tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), height - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p_head = tf.paragraphs[0]
    p_head.text = title
    p_head.font.size = Pt(13)
    p_head.font.bold = True
    p_head.font.color.rgb = NAVY

    for line in body_lines:
        p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(4)


def create_presentation(base_dir: str):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    viz_dir = os.path.join(base_dir, "visualizations")

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    # Title box
    tb = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(2.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🚚 Logistics Optimization for Delivery Routes"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = WHITE

    p2 = tf.add_paragraph()
    p2.text = "Flipkart Supply Chain Performance & Warehouse Analytics (Ekart)"
    p2.font.size = Pt(20)
    p2.font.color.rgb = YELLOW
    p2.space_before = Pt(10)

    # Metadata card
    meta = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.5), Inches(10.9), Inches(2.0))
    meta.fill.solid()
    meta.fill.fore_color.rgb = RGBColor(30, 45, 70)
    meta.line.color.rgb = BLUE

    tb_m = s1.shapes.add_textbox(Inches(1.5), Inches(4.7), Inches(10.3), Inches(1.6))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    
    p = tf_m.paragraphs[0]
    p.text = "Author: Sujal Agrahari | Internshala Data Science Training Program"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = WHITE

    p = tf_m.add_paragraph()
    p.text = "Technology Stack: MySQL 8.0, Advanced SQL (CTEs, Window Functions, Subqueries), Python Analytics Pipeline"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(200, 215, 235)
    p.space_before = Pt(6)

    p = tf_m.add_paragraph()
    p.text = "Video Walkthrough: https://www.loom.com/share/519a939ef711457d970e77f466b2729b (Part 1 & 2)"
    p.font.size = Pt(12)
    p.font.color.rgb = YELLOW
    p.space_before = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 2: PROJECT OVERVIEW & OBJECTIVES
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    apply_header(s2, "Project Overview & Core Business Objectives")

    add_card(s2, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4), "Business Context (Flipkart Logistics)", [
        "• Ekart operates a pan-India fulfillment network comprising regional sorting hubs, mother warehouses, and last-mile delivery partners.",
        "• Rising order volume during festive sales triggers severe route bottlenecks, traffic delays, and fulfillment capacity constraints.",
        "• Challenge 1: Pinpoint the root causes of transit delays (hub processing vs in-transit congestion).",
        "• Challenge 2: Optimize delivery corridors based on distance-to-time efficiency ratios.",
        "• Challenge 3: Quantify delivery agent productivity and workload balance."
    ])

    add_card(s2, Inches(6.8), Inches(1.4), Inches(5.6), Inches(5.4), "Evaluation Scope & Rubric Tasks", [
        "• Task 1: Data Cleaning & Validation (Duplicates, Imputation, Date formats) [10M]",
        "• Task 2: Delivery Delay Analysis (Delay Days, Top 10 Routes, Window Ranking) [10M]",
        "• Task 3: Route Optimization Insights (Efficiency Ratio, >20% Late Corridors) [20M]",
        "• Task 4: Warehouse Throughput (Highest Processing Time, CTE Bottlenecks) [10M]",
        "• Task 5: Delivery Agent Performance (Subqueries: Top 5 vs Bottom 5 speed) [10M]",
        "• Task 6: Shipment Tracking Analytics (Latest Checkpoints, Root Causes) [10M]",
        "• Task 7: Advanced KPI Reporting (Regional Delays, On-Time Rate %, Traffic) [10M]",
        "• Task 8 & 9: Presentation & Walkthrough Video Delivery [20M]"
    ])

    # -------------------------------------------------------------
    # SLIDE 3: TASK 1 - DATA CLEANING & PREPARATION
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    apply_header(s3, "Task 1: Data Cleaning & Preparation (10 Marks)")

    code_t1 = """-- 1. Identify and delete duplicate Order_ID records
SELECT Order_ID, COUNT(*) AS count 
FROM flipkart_orders GROUP BY Order_ID HAVING count > 1;

-- 2. Replace null Traffic_Delay_Min with route average delay
UPDATE flipkart_routes r 
JOIN (SELECT Route_ID, AVG(Traffic_Delay_Min) AS avg_delay 
      FROM flipkart_routes GROUP BY Route_ID) t 
ON r.Route_ID = t.Route_ID 
SET r.Traffic_Delay_Min = COALESCE(t.avg_delay, 50)
WHERE r.Traffic_Delay_Min IS NULL;

-- 3. Convert all date columns into YYYY-MM-DD format
UPDATE flipkart_orders SET order_date = STR_TO_DATE(order_date, '%d-%m-%Y');
UPDATE flipkart_orders SET Expected_Delivery_Date = STR_TO_DATE(Expected_Delivery_Date, '%d-%m-%Y');
UPDATE flipkart_orders SET Actual_Delivery_Date = STR_TO_DATE(Actual_Delivery_Date, '%d-%m-%Y');

-- 4. Flag invalid delivery records (Actual < Order Date)
SELECT Order_ID, Actual_Delivery_Date, Order_Date,
       CASE WHEN Actual_Delivery_Date < Order_Date THEN 'Invalid' ELSE 'Valid' END AS flag
FROM flipkart_orders;"""
    add_code_block(s3, Inches(0.8), Inches(1.4), Inches(6.8), Inches(5.4), code_t1)

    add_card(s3, Inches(8.0), Inches(1.4), Inches(4.5), Inches(5.4), "Validation Outcomes & Insights", [
        "✓ Duplicate Verification:",
        "  - 0 duplicate Order_IDs found. Strict primary key uniqueness maintained (300 orders).",
        "",
        "✓ Safe Imputation Applied:",
        "  - Null traffic delays imputed using route average with global fallback to prevent bias.",
        "",
        "✓ Chronological Standardization:",
        "  - Converted dates to standard MySQL DATE format (YYYY-MM-DD).",
        "  - Standardized checkpoint scan timestamps to DATETIME to avoid text sorting bugs.",
        "",
        "✓ Delivery Timeline Integrity:",
        "  - 100% of orders valid (zero anomalies where Actual Delivery preceded Order Date)."
    ])

    # -------------------------------------------------------------
    # SLIDE 4: TASK 2 - DELIVERY DELAY ANALYSIS
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    apply_header(s4, "Task 2: Delivery Delay Analysis (10 Marks)")

    code_t2 = """-- Calculate delivery delay (in days) for each order
SELECT Order_ID, 
       DATEDIFF(Actual_Delivery_Date, Expected_Delivery_Date) AS delivery_delay 
FROM flipkart_orders;

-- Top 10 delayed routes based on average delay days
SELECT Route_ID, 
       ROUND(AVG(DATEDIFF(Actual_Delivery_Date, Expected_Delivery_Date)), 2) AS avg_delay 
FROM flipkart_orders 
GROUP BY Route_ID 
ORDER BY avg_delay DESC LIMIT 10;

-- Window function: Rank all orders by delay within each warehouse
SELECT Order_ID, Warehouse_ID, 
       DATEDIFF(Actual_Delivery_Date, Expected_Delivery_Date) AS delivery_delay,
       RANK() OVER (PARTITION BY Warehouse_ID 
                    ORDER BY DATEDIFF(Actual_Delivery_Date, Expected_Delivery_Date) DESC) AS wh_rank 
FROM flipkart_orders;"""
    add_code_block(s4, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4), code_t2)

    img1 = os.path.join(viz_dir, "01_top_delayed_routes.png")
    if os.path.exists(img1):
        s4.shapes.add_picture(img1, Inches(6.9), Inches(1.4), width=Inches(5.6))

    # -------------------------------------------------------------
    # SLIDE 5: TASK 3 - ROUTE OPTIMIZATION INSIGHTS
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    apply_header(s5, "Task 3: Route Optimization Insights (20 Marks)")

    code_t3 = """-- Route performance: Delivery time, Traffic delay, Efficiency Ratio
SELECT r.Route_ID,
       ROUND(AVG(DATEDIFF(o.Actual_Delivery_Date, o.Order_Date)), 2) AS avg_delivery_time,
       ROUND(AVG(r.Traffic_Delay_Min), 2) AS avg_traffic_delay,
       ROUND(AVG(r.Distance_KM / r.Average_Travel_Time_Min), 3) AS efficiency_ratio 
FROM flipkart_orders o 
JOIN flipkart_routes r ON r.Route_ID = o.Route_ID 
GROUP BY r.Route_ID;

-- 3 routes with worst efficiency ratio
SELECT Route_ID, ROUND(AVG(Distance_KM / Average_Travel_Time_Min), 3) AS ratio
FROM flipkart_routes GROUP BY Route_ID ORDER BY ratio ASC LIMIT 3;

-- Routes with >20% delayed shipments
SELECT Route_ID, 
       ROUND(COUNT(CASE WHEN Actual_Delivery_Date > Expected_Delivery_Date THEN 1 END) * 100.0 / COUNT(*), 2) AS delay_pct
FROM flipkart_orders GROUP BY Route_ID HAVING delay_pct > 20;"""
    add_code_block(s5, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4), code_t3)

    img4 = os.path.join(viz_dir, "04_route_efficiency_vs_traffic.png")
    if os.path.exists(img4):
        s5.shapes.add_picture(img4, Inches(6.9), Inches(1.4), width=Inches(5.6))

    # -------------------------------------------------------------
    # SLIDE 6: TASK 4 - WAREHOUSE PERFORMANCE
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    apply_header(s6, "Task 4: Warehouse Performance & Bottleneck Analysis (10 Marks)")

    code_t4 = """-- Top 3 warehouses with highest average processing time
SELECT Warehouse_ID, Warehouse_Name, Average_Processing_Time_Min 
FROM flipkart_warehouses ORDER BY Average_Processing_Time_Min DESC LIMIT 3;

-- Total vs delayed shipments per warehouse
SELECT Warehouse_ID, COUNT(*) AS Total,
       COUNT(CASE WHEN Actual_Delivery_Date > Expected_Delivery_Date THEN 1 END) AS Delayed 
FROM flipkart_orders GROUP BY Warehouse_ID;

-- CTE: Bottleneck warehouses exceeding global average
WITH Avg_Processing AS (
    SELECT AVG(Average_Processing_Time_Min) AS Global_Average FROM flipkart_warehouses
)
SELECT w.Warehouse_ID, w.Warehouse_Name, w.Average_Processing_Time_Min,
       ROUND(a.Global_Average, 2) AS Global_Average 
FROM flipkart_warehouses w, Avg_Processing a 
WHERE w.Average_Processing_Time_Min > a.Global_Average;"""
    add_code_block(s6, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4), code_t4)

    img2 = os.path.join(viz_dir, "02_warehouse_processing_benchmark.png")
    if os.path.exists(img2):
        s6.shapes.add_picture(img2, Inches(6.9), Inches(1.4), width=Inches(5.6))

    # -------------------------------------------------------------
    # SLIDE 7: TASK 5 - DELIVERY AGENT PERFORMANCE
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    apply_header(s7, "Task 5: Delivery Agent Performance & Subquery Analysis (10 Marks)")

    code_t5 = """-- Compare average speed of top 5 vs bottom 5 agents USING SUBQUERIES
SELECT 'Top 5 Agents' AS Category, ROUND(AVG(Avg_Speed_KMPH), 2) AS avg_speed 
FROM (
    SELECT a.Agent_ID, a.Avg_Speed_KMPH
    FROM flipkart_orders o
    JOIN flipkart_deliveryagents a ON o.Agent_ID = a.Agent_ID
    GROUP BY a.Agent_ID, a.Avg_Speed_KMPH
    ORDER BY (SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) DESC
    LIMIT 5
) AS top_agents

UNION ALL

SELECT 'Bottom 5 Agents', ROUND(AVG(Avg_Speed_KMPH), 2) 
FROM (
    SELECT a.Agent_ID, a.Avg_Speed_KMPH
    FROM flipkart_orders o
    JOIN flipkart_deliveryagents a ON o.Agent_ID = a.Agent_ID
    GROUP BY a.Agent_ID, a.Avg_Speed_KMPH
    ORDER BY (SUM(CASE WHEN o.Actual_Delivery_Date <= o.Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) ASC
    LIMIT 5
) AS bottom_agents;"""
    add_code_block(s7, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4), code_t5)

    img5 = os.path.join(viz_dir, "05_agent_speed_vs_ontime.png")
    if os.path.exists(img5):
        s7.shapes.add_picture(img5, Inches(6.9), Inches(1.4), width=Inches(5.6))

    # -------------------------------------------------------------
    # SLIDE 8: TASK 6 - SHIPMENT TRACKING ANALYTICS
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    apply_header(s8, "Task 6: Shipment Tracking Analytics & Root Causes (10 Marks)")

    code_t6 = """-- For each order, list the last checkpoint and time
SELECT t.Order_ID, t.Checkpoint, t.Checkpoint_Time AS last_checkpoint 
FROM flipkart_shipmenttracking t 
INNER JOIN (
    SELECT Order_ID, MAX(Checkpoint_Time) AS Last_Checkpoint 
    FROM flipkart_shipmenttracking GROUP BY Order_ID
) m ON t.Order_ID = m.Order_ID AND t.Checkpoint_Time = m.Last_Checkpoint;

-- Most common delay reasons (excluding None)
SELECT Delay_Reason, COUNT(*) AS Frequency 
FROM flipkart_shipmenttracking 
WHERE Delay_Reason != 'None' AND Delay_Reason IS NOT NULL 
GROUP BY Delay_Reason ORDER BY Frequency DESC;

-- Identify orders with >2 delayed checkpoints
SELECT Order_ID, COUNT(*) AS Delay_Frequency 
FROM flipkart_shipmenttracking 
WHERE Delay_Reason != 'None' AND Delay_Reason IS NOT NULL 
GROUP BY Order_ID HAVING Delay_Frequency > 2;"""
    add_code_block(s8, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4), code_t6)

    img3 = os.path.join(viz_dir, "03_shipment_delay_root_causes.png")
    if os.path.exists(img3):
        s8.shapes.add_picture(img3, Inches(7.2), Inches(1.4), width=Inches(5.2))

    # -------------------------------------------------------------
    # SLIDE 9: TASK 7 - ADVANCED KPI REPORTING
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    apply_header(s9, "Task 7: Advanced KPI Reporting (10 Marks)")

    code_t7 = """-- 1. Average Delivery Delay per Region (Start_Location)
SELECT r.Start_Location, 
       ROUND(AVG(DATEDIFF(o.Actual_Delivery_Date, o.Expected_Delivery_Date)), 2) AS avg_delay 
FROM flipkart_orders o 
JOIN flipkart_routes r ON r.Route_ID = o.Route_ID 
GROUP BY r.Start_Location ORDER BY avg_delay DESC;

-- 2. On-Time Delivery % = (Total On-Time Deliveries / Total Deliveries) * 100
SELECT ROUND((SUM(CASE WHEN Actual_Delivery_Date <= Expected_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) 
       AS On_Time_Percentage 
FROM flipkart_orders;

-- 3. Average Traffic Delay per Route
SELECT Route_ID, ROUND(AVG(Traffic_Delay_Min), 2) AS Average_Traffic_Delay 
FROM flipkart_routes GROUP BY Route_ID ORDER BY Average_Traffic_Delay DESC;"""
    add_code_block(s9, Inches(0.8), Inches(1.4), Inches(6.0), Inches(5.4), code_t7)

    add_card(s9, Inches(7.2), Inches(1.4), Inches(5.3), Inches(5.4), "Executive Logistics Scorecard", [
        "📊 Key Quantitative Findings:",
        "• Total Orders Analyzed: 300 Orders (₹7,619,897.98 Total Value)",
        "• Overall On-Time Delivery Rate: 72.67% (218 / 300 orders)",
        "• Delayed Orders Rate: 27.33% (82 orders late)",
        "• Average Order Turnaround: 4.51 Days",
        "• Average Delay Across Late Orders: 1.66 Days (~40 hours)",
        "",
        "🌍 Regional Performance Hierarchy:",
        "• Hyderabad: 0.54 days avg delay (68.99% on-time)",
        "• Ahmedabad: 0.52 days avg delay (69.70% on-time)",
        "• Pune: 0.50 days avg delay (71.74% on-time)",
        "• Bengaluru: 0.24 days avg delay (81.58% on-time)",
        "• Lucknow: 0.15 days avg delay (84.62% on-time - Top Region)"
    ])

    # -------------------------------------------------------------
    # SLIDE 10: ACTIONABLE RECOMMENDATIONS & IMPLEMENTATION
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    apply_header(s10, "Strategic Business Recommendations for Flipkart Logistics")

    add_card(s10, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4), "1. Route Optimization & Transit Strategy", [
        "• Split Bottleneck Corridors into Relay Segments:",
        "  - Route RT_13 (Hyderabad -> Jaipur) experiences 54.5% delay over 1,078 km.",
        "  - Introduce staged driver relays at Nagpur/Bhopal hubs to eliminate fatigue.",
        "",
        "• Dynamic Night-Window Dispatches:",
        "  - Traffic causes 56.41% of all in-transit delays.",
        "  - Shift interstate trunk runs to 10 PM - 5 AM off-peak windows to reduce transit times by up to 35%."
    ])

    add_card(s10, Inches(6.8), Inches(1.4), Inches(5.6), Inches(5.4), "2. Warehouse & Fleet Equalization", [
        "• Modernize High-Latency Fulfillment Hubs:",
        "  - Chennai (WH_10: 117 min) and Hyderabad (WH_09: 110 min) exceed network benchmark (79.4 min) by >30 mins.",
        "  - Implement wave-based automated parcel sortation.",
        "",
        "• Workload Rebalancing for Delivery Drivers:",
        "  - Bottom 5 agents achieve only 40.7% on-time despite driving at 41 km/h.",
        "  - Rebalance high-density urban routes and provide GPS turn-by-turn guidance apps."
    ])

    # -------------------------------------------------------------
    # SLIDE 11: SUBMISSION DELIVERABLES & VIDEO WALKTHROUGH
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    apply_header(s11, "Task 8 & 9: Project Submission & Video Walkthrough Links")

    add_card(s11, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4), "Task 9: Video Presentation Details (10 Marks)", [
        "🎥 Video Walkthrough Links (Face Visible, 5-9 Mins):",
        "",
        "• Loom Walkthrough Part 1:",
        "  https://www.loom.com/share/519a939ef711457d970e77f466b2729b",
        "  (Covers problem understanding, schema architecture, data cleaning, and delay distribution)",
        "",
        "• Loom Walkthrough Part 2:",
        "  https://www.loom.com/share/2bce798c27254d4db2faf6ce44ddacb4",
        "  (Covers route optimization, warehouse bottlenecks, driver cohorts, and strategic recommendations)",
        "",
        "• Google Drive Backup Link:",
        "  [Add Google Drive Video Link Here as per guidelines]"
    ])

    add_card(s11, Inches(6.8), Inches(1.4), Inches(5.6), Inches(5.4), "Submission Checklist & Guidelines", [
        "📁 Submission Package Structure:",
        "  • Flipkart_Logistics_Optimization.sql (Clean MySQL script)",
        "  • Flipkart_Logistics_Optimization.pptx (Presentation Deck)",
        "  • Logistics_Optimization_for_Delivery_Routes_Flipkart.pdf",
        "",
        "✓ All Tasks 1 to 7 fully solved with exact MySQL queries.",
        "✓ Queries, result tables, and high-resolution charts integrated.",
        "✓ Cleaned date standardizations and edge-case imputations.",
        "✓ Packaged in submission .zip folder as required by dashboard."
    ])

    ppt_path = os.path.join(base_dir, "presentation", "Flipkart_Logistics_Optimization.pptx")
    prs.save(ppt_path)
    print(f"Presentation generated successfully: {ppt_path}")
    return ppt_path


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    create_presentation(base_dir)
