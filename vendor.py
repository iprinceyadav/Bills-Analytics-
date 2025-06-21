import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import f

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
    excel_path = "E:\internship work\Bill Analytics\DUMP_FE_OVERVIEW.pkl"  # Replace with your file path
    df = pd.read_pickle(excel_path)

    # 2. Randomly sample 20% of the data
    sampled_df = df.sample(frac=0.2, random_state=42)  #
    return sampled_df


try:
    df = load_data()
    st.success("Data loaded successfully!")
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()
filtered_df=df.copy()
# Sidebar filters 

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
    col_select1, col_select2, col_select3 = st.columns([1, 3, 1])
    
    with col_select2:
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
                                "<extra></extra>"
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating payment distribution chart: {str(e)}")
    
    else:
        # Single department view
        dept_df = filtered_df[filtered_df['DEPARTMENT'] == selected_dept]
        
        st.subheader(f"Analysis for {selected_dept} Department")
        
        # Department KPIs
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Vendors", dept_df['VENDORNAME'].nunique())
        with col2:
            st.metric("Total Payments", f"₹{dept_df['BILLVALUE'].sum():,.2f}")
        with col3:
            st.metric("Avg Payment Days", f"{dept_df['TOTAL_DAYS_for_PAYMENT'].mean():.1f} days")
        
        # Vendor Payment Distribution Pie Chart
        st.subheader(f"Payment Distribution by Vendor in {selected_dept}")
        vendor_payments = dept_df.groupby('VENDORNAME')['BILLVALUE'].sum().reset_index()
        vendor_payments['Amount'] = vendor_payments['BILLVALUE'].apply(lambda x: f"₹{x:,.2f}")
        
        fig3 = px.pie(
            vendor_payments,
            values='BILLVALUE',
            names='VENDORNAME',
            title=f"Vendor Payment Distribution in {selected_dept}",
            hole=0.3,
            hover_data=['Amount']
        )
        
        fig3.update_traces(
            hovertemplate="<b>%{label}</b><br>" +
                        "Percentage: %{percent}<br>" +
                        "Amount: %{customdata[0]}<br>" +
                        "<extra></extra>",
            textinfo='percent+label'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # All vendors in this department
        st.subheader(f"All Vendors in {selected_dept}")
        all_vendors = dept_df.groupby('VENDORNAME').agg({
            'BILLVALUE': 'sum',
            'TOTAL_DAYS_for_PAYMENT': 'mean',
            'BILLNO': 'count',
            'PAYMENT_DONE': 'count'
        }).rename(columns={
            'BILLVALUE': 'Total Amount',
            'TOTAL_DAYS_for_PAYMENT': 'Avg Payment Days',
            'BILLNO': 'Bill Count',
            'PAYMENT_DONE': 'Payment Done Count'
        }).sort_values('Total Amount', ascending=False)
        
        st.dataframe(
            all_vendors.style.format({
                'Total Amount': '₹{:,.2f}',
                'Avg Payment Days': '{:.1f} days',
                'Bill Count': '{:,.0f}',
                'Payment Done Count': '{:,.0f} times'
            }),
            use_container_width=True,
            height=min(600, 35 * len(all_vendors))
        )
        
with tab2:
    st.subheader("Vendor Performance Analysis")
    
    # Vendor selector with controlled width
    vendor_col1, vendor_col2, vendor_col3 = st.columns([1, 3, 1])
    with vendor_col2:
        selected_vendor = st.selectbox(
            "Select Vendor",
            options=sorted(filtered_df['VENDORNAME'].unique()),
            key='vendor_select'
        )
    
    vendor_data = filtered_df[filtered_df['VENDORNAME'] == selected_vendor]
    
    if not vendor_data.empty:
        
        
        # 5 KPI cards in one row
        col1, col2, col3, col4  = st.columns(4)
        
        with col1:
            f.tab2_Col1(vendor_data)
            
        with col2:
            f.tab2_Col2(vendor_data,filtered_df)
        
        with col3:
            
            f.tab2_Col3(vendor_data)
        with col4:
            f.tab2_Col4(vendor_data)
        
        # Vendor payment history
        with st.expander("Payment History", expanded=False):
        
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