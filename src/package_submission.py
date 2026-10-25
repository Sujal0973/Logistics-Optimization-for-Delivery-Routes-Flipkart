#!/usr/bin/env python3
"""
Package Project Submission (.zip) according to submission guidelines:
- PPT Presentation (.pptx / .pdf)
- SQL Script (.sql)

Author: Sujal Agrahari
"""

import os
import shutil
import zipfile

def package_submission(base_dir: str):
    submission_dir = os.path.join(base_dir, "submission")
    os.makedirs(submission_dir, exist_ok=True)

    sql_src = os.path.join(base_dir, "sql", "Flipkart_Logistics_Optimization.sql")
    pptx_src = os.path.join(base_dir, "presentation", "Flipkart_Logistics_Optimization.pptx")
    pdf_src = os.path.join(base_dir, "presentation", "Logistics_Optimization_for_Delivery_Routes_Flipkart.pdf")

    # Copy files to submission directory
    shutil.copy2(sql_src, os.path.join(submission_dir, "Flipkart_Logistics_Optimization.sql"))
    if os.path.exists(pptx_src):
        shutil.copy2(pptx_src, os.path.join(submission_dir, "Flipkart_Logistics_Optimization.pptx"))
    if os.path.exists(pdf_src):
        shutil.copy2(pdf_src, os.path.join(submission_dir, "Logistics_Optimization_for_Delivery_Routes_Flipkart.pdf"))

    # Create ZIP archive
    zip_path = os.path.join(base_dir, "Flipkart_Logistics_Optimization_Submission.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(submission_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, submission_dir)
                zipf.write(file_path, arcname)

    print(f"[SUCCESS] Submission packaged into: {zip_path}")
    print("Files included in ZIP:")
    with zipfile.ZipFile(zip_path, "r") as zipf:
        for info in zipf.infolist():
            print(f"  - {info.filename} ({info.file_size:,} bytes)")

    return zip_path

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    package_submission(base_dir)
