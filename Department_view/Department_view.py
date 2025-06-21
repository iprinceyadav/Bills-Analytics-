import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import plotly.graph_objects as go
import function as fn

# Set page configuration
st.set_page_config(layout="wide", page_title="Vendor Payment Dashboard")

# Custom CSS for styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Reduce title margin */
    h1 {
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Reduce subheader margins */
    h2 {
        margin-top: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .kpi-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        text-align: center;
    }
    .kpi-title {
        font-size: 16px;
        font-weight: 600;
        color: #495057;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #2c3e50;
    }
    .kpi-subtext {
        font-size: 12px;
        color: #7f8c8d;
    }
    .selectbox-container {
        margin-top: 10px;
        margin-bottom: 5px;
    }
    .stakeholder-chart {
        height: 300px;
    }
    .vendor-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 16px;
    }
    .select-label {
        font-size: 14px;
        color: #495057;
        margin-bottom: 6px;
        display: block;
    }
    .stats-text {
        font-size: 12px;
        color: #7f8c8d;
        margin-top: 12px;
    }
    .stSelectbox > div > div {
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)
np.random.seed(42) 
# Sample data generation
def generate_sample_data():
    # Generate random vendor data
    vendors = []
    departments = ["Finance", "Procurement", "Operations", "HR", "IT"]
    financial_years = ["2021-22", "2022-23", "2023-24"]
    
    for i in range(1, 101):
        vendor_type = "MSME" if np.random.random() > 0.4 else "Non-MSME"
        submission_date = np.random.choice(pd.date_range('2021-04-01', '2023-12-31'))
        fy = "2021-22" if submission_date < pd.Timestamp('2022-04-01') else \
             "2022-23" if submission_date < pd.Timestamp('2023-04-01') else "2023-24"
        
        vendors.append({
            "Vendor ID": f"VEND{i:03d}",
            "Vendor Name": f"Vendor {i}",
            "Type": vendor_type,
            "Department": np.random.choice(departments),
            "FY": fy,
            "Submission Date": submission_date,
            "Pending Amount": round(np.random.uniform(1000, 500000), 2),
            "Paid Amount": round(np.random.uniform(500, 450000), 2),  # Added paid amount
            "Bill_Value": round(np.random.uniform(1500, 550000), 2),  # Added bill value
            "Days Pending": np.random.randint(1, 120),
            "Stakeholder": np.random.choice(["Finance", "Procurement", "Legal", "Operations", "Management"])
        })
    
    return pd.DataFrame(vendors)

# Load data
df = generate_sample_data()

# Calculate metrics
total_bill_pending = df["Pending Amount"].sum()
count_done = len(df[df["Pending Amount"] == 0])
msme_count = len(df[df["Type"] == "MSME"])
non_msme_count = len(df[df["Type"] == "Non-MSME"])
avg_days_pending = df["Days Pending"].mean()

# Four point summary for days pending
days_summary = df["Days Pending"].describe()[3:7].to_dict()

# Bottleneck analysis - top stakeholders by average days pending
bottleneck_data = df.groupby("Stakeholder")["Days Pending"].mean().sort_values(ascending=False).head(4)

# Dashboard layout
st.title("Department View Dashboard")

# Create 4 columns for KPI cards
col1, col2, col3, col4 = st.columns([1, 1, 1, 2]) 

with col1:
    fn.KPI_col1()

with col2:
    fn.KPI_col2()
    



with col3:
    fn.KPI_col3()

with col4:
    # Card container for Bottleneck Analysis
    fn.KPI_col4()

st.markdown("---")  # Horizontal divider

# Create 3 columns for the new section
col5, col6, col7 = st.columns([1, 1, 1.5])

with col5:
    fn.sec2_col5()

with col6:
    fn.sec2_col6()

with col7:
    fn.sec2_col7()



st.markdown("---")

col8, col9 = st.columns([1, 1])

with col8:
    fn.sec3_col8()

with col9:
    fn.sec3_col9()