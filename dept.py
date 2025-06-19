import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="Vendor Payment Analytics",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fixed data loading function
@st.cache_data
def load_data():
    np.random.seed(42)
    num_rows = 50
    
    # Define possible values
    departments = ['Finance', 'HR', 'IT', 'Operations', 'Marketing', 'Logistics']
    vendors = [f'Vendor {chr(i)}' for i in range(65, 91)]  # A-Z
    bill_types = ['Goods', 'Services', 'Consulting', 'Maintenance']
    statuses = ['Paid', 'Pending', 'Processed']
    
    # Generate base data
    data = {
        'TRACKINGNO': [f'TR{str(i).zfill(3)}' for i in range(1, num_rows+1)],
        'DOCUMENT_ID': [f'DOC{str(i).zfill(3)}' for i in range(1, num_rows+1)],
        'BILLNO': [f'BL{str(i).zfill(3)}' for i in range(1, num_rows+1)],
        'VENDORNAME': np.random.choice(vendors, num_rows),
        'DEPARTMENT': np.random.choice(departments, num_rows),
        'BILLVALUE': np.random.randint(5000, 50000, num_rows),
        'TOTAL_DAYS_for_PAYMENT': np.random.randint(5, 30, num_rows),
        'MSME_VENDOR': np.random.choice(['Yes', 'No'], num_rows, p=[0.6, 0.4]),
        'BILLTYPE': np.random.choice(bill_types, num_rows),
        'STATUS': np.random.choice(statuses, num_rows)
    }
    
    # Generate bill dates (as datetime objects)
    base_date = datetime(2023, 1, 1)
    data['BILLDATE'] = [base_date + timedelta(days=np.random.randint(0, 365)) for _ in range(num_rows)]
    
    # Calculate payment dates by adding payment days to bill dates
    data['PAYMENT_DONE'] = [
        data['BILLDATE'][i] + timedelta(days=int(data['TOTAL_DAYS_for_PAYMENT'][i]))
        for i in range(num_rows)
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Ensure datetime columns have proper type
    df['BILLDATE'] = pd.to_datetime(df['BILLDATE'])
    df['PAYMENT_DONE'] = pd.to_datetime(df['PAYMENT_DONE'])
    
    return df

# Load the data
try:
    df = load_data()
    st.success("Data loaded successfully!")
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()
# Sidebar filters (only date range and MSME filter remain here)
st.sidebar.header("Global Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=[df['PAYMENT_DONE'].min(), df['PAYMENT_DONE'].max()],
    min_value=df['PAYMENT_DONE'].min(),
    max_value=df['PAYMENT_DONE'].max()
)

msme_filter = st.sidebar.radio("MSME Vendors", ['All', 'Yes', 'No'])
bill_type_filter = st.sidebar.multiselect(
    "Bill Type",
    options=df['BILLTYPE'].unique(),
    default=df['BILLTYPE'].unique()
)

# Apply global filters
filtered_df = df.copy()
if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[
        (filtered_df['PAYMENT_DONE'] >= start_date) & 
        (filtered_df['PAYMENT_DONE'] <= end_date)
    ]

if msme_filter != 'All':
    filtered_df = filtered_df[filtered_df['MSME_VENDOR'] == msme_filter]

if bill_type_filter:
    filtered_df = filtered_df[filtered_df['BILLTYPE'].isin(bill_type_filter)]

# Main dashboard
st.title("Department-wise Vendor Payment Analytics")

# KPI cards
# col1, col2, col3 = st.columns(3)
# with col1:
#     st.metric("Total Vendors", filtered_df['VENDORNAME'].nunique())
# with col2:
#     total_payment = filtered_df['BILLVALUE'].sum()
#     st.metric("Total Payments", f"₹{total_payment:,.2f}")
# with col3:
#     avg_days = filtered_df['TOTAL_DAYS_for_PAYMENT'].mean()
#     st.metric("Avg Payment Days", f"{avg_days:.1f} days")

# Tabs


tab1, tab2 = st.tabs(["Department Analysis", "Vendor Analysis"])

with tab1:
    # Create a container with columns to control select box width
    col_select1, col_select2, col_select3 = st.columns([1, 3, 1])  # Middle column controls width
    
    with col_select2:  # This centers the select box and makes it smaller
        all_departments = ['All Departments'] + sorted(filtered_df['DEPARTMENT'].unique().tolist())
        selected_dept = st.selectbox(
            "Select Department", 
            all_departments, 
            key='dept_select'
        )
    
    if selected_dept == 'All Departments':
        st.subheader("Summary Across All Departments")
        
        # Create consistent color mapping for departments
        departments = filtered_df['DEPARTMENT'].unique()
        color_map = {dept: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] 
                    for i, dept in enumerate(departments)}
        
        # KPI cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Vendors", filtered_df['VENDORNAME'].nunique())
        with col2:
            total_payment = filtered_df['BILLVALUE'].sum()
            st.metric("Total Payments", f"₹{total_payment:,.2f}")
        with col3:
            avg_days = filtered_df['TOTAL_DAYS_for_PAYMENT'].mean()
            st.metric("Avg Payment Days", f"{avg_days:.1f} days")
        
        # Charts with consistent colors
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                vendor_count = filtered_df.groupby('DEPARTMENT')['VENDORNAME'].nunique().reset_index()
                fig1 = px.bar(
                    vendor_count, 
                    x='DEPARTMENT', 
                    y='VENDORNAME',
                    title="Number of Vendors by Department",
                    labels={'VENDORNAME': 'Vendor Count', 'DEPARTMENT': 'Department'},
                    color='DEPARTMENT',
                    color_discrete_map=color_map
                )
                st.plotly_chart(fig1, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating vendor count chart: {str(e)}")
        
        with col2:
            try:
                payment_sum = filtered_df.groupby('DEPARTMENT')['BILLVALUE'].sum().reset_index()
                payment_sum['Amount'] = payment_sum['BILLVALUE'].apply(lambda x: f"₹{x:,.2f}")
                
                fig2 = px.pie(
                    payment_sum,
                    values='BILLVALUE',
                    names='DEPARTMENT',
                    title="Payment Distribution by Department",
                    hole=0.3,
                    color='DEPARTMENT',
                    color_discrete_map=color_map,
                    hover_data=['Amount']
                )
                
                fig2.update_traces(
                    hovertemplate="<b>%{label}</b><br>" +
                                "Percentage: %{percent}<br>" +
                                "Amount: %{customdata[0]}<br>" +
                                "<extra></extra>",
                    textinfo='percent+label'
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating payment distribution chart: {str(e)}")
    
    else:
        # Single department view
        dept_df = filtered_df[filtered_df['DEPARTMENT'] == selected_dept]
        
        st.subheader(f"Analysis for {selected_dept} Department")
        
        # Department KPIs (removed Pending Payments)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Vendors", dept_df['VENDORNAME'].nunique())
        with col2:
            st.metric("Total Payments", f"₹{dept_df['BILLVALUE'].sum():,.2f}")
        with col3:
            st.metric("Avg Payment Days", f"{dept_df['TOTAL_DAYS_for_PAYMENT'].mean():.1f} days")
        
        # All vendors in this department (not just top 5)
        st.subheader(f"All Vendors in {selected_dept}")
        
        # Calculate payment frequency (how many times payment was done to each vendor)
        vendor_stats = dept_df.groupby('VENDORNAME').agg({
            'BILLVALUE': 'sum',
            'TOTAL_DAYS_for_PAYMENT': 'mean',
            'BILLNO': 'count',
            'PAYMENT_DONE': 'count'  # This counts how many times payment was done
        }).rename(columns={
            'BILLVALUE': 'Total Amount',
            'TOTAL_DAYS_for_PAYMENT': 'Avg Payment Days',
            'BILLNO': 'Bill Count',
            'PAYMENT_DONE': 'Payment Done Count'
        }).sort_values('Total Amount', ascending=False)
        
        st.dataframe(
            vendor_stats.style.format({
                'Total Amount': '₹{:,.2f}',
                'Avg Payment Days': '{:.1f} days',
                'Bill Count': '{:,.0f}',
                'Payment Done Count': '{:,.0f} times'
            }),
            use_container_width=True,
            height=min(600, 35 * len(vendor_stats)))  # Dynamic height

with tab2:
    st.subheader("Vendor Performance Analysis")
    
    # Vendor selector
    selected_vendor = st.selectbox(
        "Select Vendor",
        options=sorted(filtered_df['VENDORNAME'].unique())
    )
    
    vendor_data = filtered_df[filtered_df['VENDORNAME'] == selected_vendor]
    
    if not vendor_data.empty:
        # Vendor KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Payments", f"₹{vendor_data['BILLVALUE'].sum():,.2f}")
        with col2:
            st.metric("Number of Bills", len(vendor_data))
        with col3:
            st.metric("Avg Payment Days", f"{vendor_data['TOTAL_DAYS_for_PAYMENT'].mean():.1f} days")
        with col4:
            st.metric("Primary Department", vendor_data['DEPARTMENT'].mode()[0])
        
        # Vendor payment history
        st.subheader("Payment History")
        vendor_history = vendor_data[[
            'BILLNO', 'BILLDATE', 'PAYMENT_DONE', 'BILLVALUE', 
            'TOTAL_DAYS_for_PAYMENT', 'DEPARTMENT', 'BILLTYPE', 'STATUS'
        ]].sort_values('PAYMENT_DONE', ascending=False)
        
        st.dataframe(
            vendor_history.style.format({
                'BILLVALUE': '₹{:,.2f}',
                'TOTAL_DAYS_for_PAYMENT': '{:.1f} days',
                'BILLDATE': lambda x: x.strftime('%Y-%m-%d'),
                'PAYMENT_DONE': lambda x: x.strftime('%Y-%m-%d')
            }),
            use_container_width=True,
            height=300
        )
        
        # Payment trend over time
        
    else:
        st.warning("No data available for selected vendor")

# Add download button
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="Download Filtered Data",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name=f"vendor_payments_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# Show raw data option
if st.sidebar.checkbox("Show Raw Data"):
    st.sidebar.subheader("Filtered Data Preview")
    st.sidebar.dataframe(filtered_df.head(10))