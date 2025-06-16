import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set up the page
st.set_page_config(layout="wide", page_title="Invoice Processing Dashboard")
st.title("Invoice Processing Workflow Analysis")

# Load data function (replace with your actual data loading)
@st.cache_data
def load_data():
    # In a real app, you would load your data here
    # For demo purposes, we'll create a dummy dataframe
    data = {
        "TRACKINGNO": [f"TRK{1000+i}" for i in range(100)],
        "DOCUMENT_ID": [f"DOC{2000+i}" for i in range(100)],
        "RECVDATE": pd.date_range(start="2023-01-01", periods=100, freq="D"),
        "VENDORID": [f"V{3000+i}" for i in range(100)],
        "VENDORNAME": [f"Vendor {i}" for i in range(100)],
        "MSME_VENDOR": np.random.choice(["Yes", "No"], 100),
        "BILLTYPECODE": np.random.choice(["A", "B", "C"], 100),
        "BILLTYPE": np.random.choice(["Type1", "Type2", "Type3"], 100),
        "UNIT_ID": np.random.choice(["Unit1", "Unit2", "Unit3"], 100),
        "BILLNO": [f"BL{4000+i}" for i in range(100)],
        "BILLDATE": pd.date_range(start="2023-01-01", periods=100, freq="D"),
        "INITIATOR": [f"User{i}" for i in range(100)],
        "PONO": [f"PO{5000+i}" for i in range(100)],
        "BILLVALUE": np.random.uniform(1000, 50000, 100).round(2),
        "STATUS": np.random.choice(["Approved", "Pending", "Rejected", "Hold"], 100),
        "ACTIONBY": [f"Approver{i}" for i in range(100)],
        "REMARK": np.random.choice(["", "Urgent", "Review needed", "Complete"], 100),
        "GRNNO": [f"GRN{6000+i}" for i in range(100)],
        "GRNDATE": pd.date_range(start="2023-01-05", periods=100, freq="D"),
        "DEPARTMENT": np.random.choice(["Finance", "HR", "IT", "Operations"], 100),
        "CATEGORY": np.random.choice(["Category1", "Category2", "Category3"], 100),
        "DAYS_Vendor_to_BD": np.random.randint(1, 10, 100),
        "DAYS_BD_to_SPOC": np.random.randint(1, 5, 100),
        "DAYS_SPOC_to_User": np.random.randint(1, 7, 100),
        "TOTAL_DAYS_to_BD": np.random.randint(1, 15, 100),
        "TOTAL_DAYS_to_SPOC": np.random.randint(5, 20, 100),
        "TOTAL_DAYS_to_User": np.random.randint(10, 30, 100),
        "TOTAL_DAYS_for_PAYMENT": np.random.randint(15, 60, 100)
    }
    return pd.DataFrame(data)

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
department_filter = st.sidebar.multiselect("Department", options=df["DEPARTMENT"].unique(), default=df["DEPARTMENT"].unique())
status_filter = st.sidebar.multiselect("Status", options=df["STATUS"].unique(), default=df["STATUS"].unique())

# MSME Vendor as checkboxes
st.sidebar.subheader("MSME Vendor")
msme_yes = st.sidebar.checkbox("Yes", value=True, key="msme_yes")
msme_no = st.sidebar.checkbox("No", value=True, key="msme_no")

# Determine selected MSME types
selected_msme = []
if msme_yes:
    selected_msme.append("Yes")
if msme_no:
    selected_msme.append("No")

bill_type_filter = st.sidebar.multiselect("Bill Type", options=df["BILLTYPE"].unique(), default=df["BILLTYPE"].unique())


# Apply filters
filtered_df = df[
    (df["DEPARTMENT"].isin(department_filter)) &
    (df["STATUS"].isin(status_filter)) &
    (df["MSME_VENDOR"].isin(selected_msme)) &
    (df["BILLTYPE"].isin(bill_type_filter))
]

# Main dashboard (rest of your code remains the same)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", 
    "Timeline Analysis", 
    "Vendor Analysis", 
    "Department View", 
    "Detailed Records"
])

with tab1:
    st.header("Process Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Invoices", len(filtered_df))
    with col2:
        avg_processing_time = filtered_df["TOTAL_DAYS_for_PAYMENT"].mean()
        st.metric("Avg Processing Time (days)", round(avg_processing_time, 1))
    with col3:
        total_value = filtered_df["BILLVALUE"].sum()
        st.metric("Total Bill Value", f"${total_value:,.2f}")
    
    # Status distribution
    st.subheader("Status Distribution")
    fig, ax = plt.subplots()
    filtered_df["STATUS"].value_counts().plot(kind="bar", ax=ax)
    st.pyplot(fig)
    
    # Bill value distribution
    st.subheader("Bill Value Distribution")
    fig, ax = plt.subplots()
    sns.histplot(filtered_df["BILLVALUE"], bins=20, ax=ax)
    st.pyplot(fig)

with tab2:
    st.header("Timeline Analysis")
    
    # Processing time by stage
    st.subheader("Average Days by Processing Stage")
    timeline_data = filtered_df[[
        "DAYS_Vendor_to_BD", "DAYS_BD_to_SPOC", "DAYS_SPOC_to_User",
        "TOTAL_DAYS_to_BD", "TOTAL_DAYS_to_SPOC", "TOTAL_DAYS_to_User"
    ]].mean().reset_index()
    timeline_data.columns = ["Stage", "Average Days"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=timeline_data, x="Stage", y="Average Days", ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Time trends
    st.subheader("Processing Time Trends")
    time_data = filtered_df.groupby(filtered_df["RECVDATE"].dt.to_period("M"))["TOTAL_DAYS_for_PAYMENT"].mean().reset_index()
    time_data["RECVDATE"] = time_data["RECVDATE"].astype(str)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=time_data, x="RECVDATE", y="TOTAL_DAYS_for_PAYMENT", ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

with tab3:
    st.header("Vendor Analysis")
    
    # Top vendors by bill count
    st.subheader("Top Vendors by Invoice Count")
    top_vendors_count = filtered_df["VENDORNAME"].value_counts().head(10).reset_index()
    top_vendors_count.columns = ["Vendor", "Count"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_vendors_count, x="Count", y="Vendor", ax=ax)
    st.pyplot(fig)
    
    # Top vendors by bill value
    st.subheader("Top Vendors by Bill Value")
    top_vendors_value = filtered_df.groupby("VENDORNAME")["BILLVALUE"].sum().nlargest(10).reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_vendors_value, x="BILLVALUE", y="VENDORNAME", ax=ax)
    st.pyplot(fig)
    
    # MSME vs non-MSME comparison
    st.subheader("MSME vs Non-MSME Comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Average Processing Time")
        msme_time = filtered_df.groupby("MSME_VENDOR")["TOTAL_DAYS_for_PAYMENT"].mean().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(data=msme_time, x="MSME_VENDOR", y="TOTAL_DAYS_for_PAYMENT", ax=ax)
        st.pyplot(fig)
    with col2:
        st.write("Average Bill Value")
        msme_value = filtered_df.groupby("MSME_VENDOR")["BILLVALUE"].mean().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(data=msme_value, x="MSME_VENDOR", y="BILLVALUE", ax=ax)
        st.pyplot(fig)

with tab4:
    st.header("Department View")
    
    # Department-wise metrics
    st.subheader("Department Performance")
    dept_metrics = filtered_df.groupby("DEPARTMENT").agg({
        "BILLVALUE": ["count", "sum", "mean"],
        "TOTAL_DAYS_for_PAYMENT": "mean"
    }).reset_index()
    dept_metrics.columns = ["Department", "Invoice Count", "Total Value", "Avg Bill Value", "Avg Processing Time"]
    st.dataframe(dept_metrics.style.format({
        "Total Value": "${:,.2f}",
        "Avg Bill Value": "${:,.2f}",
        "Avg Processing Time": "{:.1f} days"
    }))
    
    # Department comparison charts
    col1, col2 = st.columns(2)
    with col1:
        st.write("Invoice Count by Department")
        fig, ax = plt.subplots()
        filtered_df["DEPARTMENT"].value_counts().plot(kind="bar", ax=ax)
       #st.pyplot(fig)
    with col2:
        st.write("Processing Time by Department")
        fig, ax = plt.subplots()
        sns.boxplot(data=filtered_df, x="DEPARTMENT", y="TOTAL_DAYS_for_PAYMENT", ax=ax)
        plt.xticks(rotation=45)
        #st.pyplot(fig)

with tab5:
    st.header("Detailed Records")
    
    # Detailed data view with filtering options
    st.subheader("Invoice Details")
    columns_to_show = st.multiselect(
        "Select columns to display",
        options=filtered_df.columns,
        default=[
            "TRACKINGNO", "VENDORNAME", "DEPARTMENT", "BILLTYPE", 
            "BILLVALUE", "STATUS", "TOTAL_DAYS_for_PAYMENT"
        ]
    )
    
    st.dataframe(filtered_df[columns_to_show])
    
    # Download option
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Filtered Data",
        csv,
        "invoice_processing_data.csv",
        "text/csv",
        key='download-csv'
    )

# Add some styling
st.markdown("""
<style>
    .stDataFrame {
        width: 100%;
    }
    
</style>
""", unsafe_allow_html=True)