import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


np.random.seed(42) 

######################################            Sample data generation                ################################

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






###################################                   KPI Dashboard                       ##########################################

def KPI_col1():
    st.markdown(f"""
    <div class="kpi-card" style="text-align: center;">
        <div class="kpi-title">Total Bill Pending</div>
        <div class="kpi-value">₹ 10 Lakh</div>
        <div class="kpi-subtext"> Paid Bill: 230</div>
        <div class="kpi-subtext"> Paid Amount: ₹320 Crore</div>
    </div>
    """, unsafe_allow_html=True)




def KPI_col2():
    with st.container():
        st.markdown(f"""
        <div style="
            background-color: #ffffff;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            width: 200px;
        ">
            <div style="font-size: 14px; font-weight: 600; color: #2c3e50; margin-bottom: 12px;">
                MSME/Non-MSME
            </div>
            <div style="font-size: 11px; color: #7f8c8d; margin-top: 10px;">
                MSME: {msme_count} | Non-MSME: {non_msme_count}
            </div>       
                    
        """, unsafe_allow_html=True)
        # Close the card
        
        
        # Vendor type selection
        st.markdown('<div style="font-size: 12px; color: #495057; margin-bottom: 4px;">Select Vendor Type</div>', unsafe_allow_html=True)
        vendor_type = st.selectbox(
            "",
            ["MSME", "Non-MSME"],
            key="vendor_type_select",
            label_visibility="collapsed"
        )
        
        
        
        

def KPI_col3():
    try:
        # Calculate statistics
        days_stats = df["Days Pending"].describe()
        avg_days = df["Days Pending"].mean()
        
        # Create horizontal bar chart
        metrics = {
            'Fastest': days_stats['min'],
            '25th %ile': days_stats['25%'],
            'Median': days_stats['50%'],
            '75th %ile': days_stats['75%'],
            'Slowest': days_stats['max']
        }
        
        fig = px.bar(
            x=list(metrics.values()),
            y=list(metrics.keys()),
            orientation='h',
            color=list(metrics.values()),
            color_continuous_scale='Blues',
            height=200,
            width=250
        )
        
        fig.update_layout(
            margin=dict(l=0, r=0, t=20, b=20),
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis={'categoryorder':'total ascending'}
        )
        
        fig.update_traces(
            hovertemplate="%{y}: %{x:.0f} days",
            texttemplate="%{x:.0f}d",
            textposition='inside',
            textfont_color='white'
        )
        
        # Main card
        st.markdown(f"""
        <div class="kpi-card" style="padding: 10px; height: 80px;">
            <div style="font-size: 13px; font-weight: 600; color: #2c3e50; margin-bottom: 5px;">
                ⏳ Payment Processing Days
            </div>
            <div style="font-size: 15px; color: #555; margin-bottom: 10px;">
                Average: <strong>{avg_days:.0f} days</strong>
            </div>    
            </div>
        """, unsafe_allow_html=True)
        
        # Display the chart
        with st.expander("Days Pending Summary", expanded=True):
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            
        
    except Exception as e:
        st.error(f"Error displaying timeline: {str(e)}")

def KPI_col4():

    st.subheader("Bottleneck Analysis")
    # Vendor selection
    st.markdown('<div style="font-size: 12px; color: #495057; margin-bottom: 4px; margin-top: 8px;">Select Vendor</div>', unsafe_allow_html=True)
    vendors = df[df["Type"] == st.session_state.vendor_type_select]["Vendor Name"].unique()
    selected_vendor = st.selectbox(
        "",
        vendors,
        key="vendor_select",
        label_visibility="collapsed"
        )
    
    # Create a vertical bar chart for bottleneck analysis
    fig = px.bar(
        x=bottleneck_data.index,
        y=bottleneck_data.values,
        labels={'x': 'Stakeholder', 'y': 'Avg Days Pending'},
        color=bottleneck_data.index,
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    
    fig.update_layout(
        height=200,  # Smaller height
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        xaxis=dict(
            showline=False,  # Hide x-axis line
            showgrid=False   # Hide x-axis grid lines
        ),
        yaxis=dict(
            showline=False,  # Hide y-axis line
            showgrid=False   # Hide y-axis grid lines
        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)'  # Transparent background
    )
    
    # Remove color axis and make bars thinner
    fig.update_traces(
        width=0.4,  # Thinner bars
        marker_line_width=0  # No border on bars
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)




############################################     -------  SECTION 2 :   ----------           ##############################################


def sec2_col5():
    st.markdown("**Stakeholder Processing Time**")
    
    # Calculate average days by stakeholder
    stakeholder_days = df.groupby('Stakeholder')['Days Pending'].mean().sort_values(ascending=False)
    
    # Create vertical bar chart
    fig1 = px.bar(
        stakeholder_days,
        orientation='v',  # Changed to vertical
        labels={'value': 'Average Days', 'index': ''},
        color=stakeholder_days.values,
        color_continuous_scale='Blues',
        text=[f"{x:.1f}d" for x in stakeholder_days.values]  # Add days abbreviation
    )
    
    # Customize layout
    fig1.update_layout(
        height=350,  # Slightly taller for vertical format
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis_title="Average Processing Days",
        xaxis_title="",
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x'
    )
    
    # Format bars and text
    fig1.update_traces(
        textposition='outside',
        textfont_size=12,
        width=0.6,  # Narrower bars for vertical format
        hovertemplate="<b>%{x}</b><br>%{y:.1f} days<extra></extra>"
    )
    
    st.plotly_chart(fig1, use_container_width=True)


def sec2_col6():
    st.markdown("**Vendor Bill Analysis**")
    # Horizontal bar graph of vendor bills
    vendor_bills = df['Vendor Name'].value_counts().sort_values(ascending=True)[-10:]  # Top 10 vendors
    fig2 = px.bar(
        vendor_bills,
        orientation='h',
        labels={'value': 'Number of Bills', 'index': 'Vendor'},
        text=vendor_bills.values,
        color=vendor_bills.values,
        color_continuous_scale='Greens'
    )
    fig2.update_layout(
        height=400,
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Number of Bills",
        yaxis_title=""
    )
    fig2.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)


def sec2_col7():
    st.markdown("**Cancelled Bill History**")
    # Filter cancelled bills (assuming a 'Status' column exists)
    if 'Status' in df.columns:
        cancelled_bills = df[df['Status'] == 'Cancelled'].head(10)
    else:
        # Create sample cancelled bills if no status column exists
        cancelled_bills = df.sample(5).copy()
        cancelled_bills['Status'] = 'Cancelled'
        cancelled_bills['Cancellation Reason'] = np.random.choice(
            ['Duplicate', 'Incorrect Amount', 'Vendor Request', 'System Error'],
            size=5
        )
    
    # Display cancelled bills table
    st.dataframe(
        cancelled_bills[[
            'Vendor Name', 
            'Pending Amount', 
            'Days Pending', 
            'Status',
            'Cancellation Reason' if 'Cancellation Reason' in cancelled_bills.columns else 'Stakeholder'
        ]],
        height=400,
        use_container_width=True
    )

############################################     -------  SECTION 3 :   ----------           ############################################## 

def sec3_col8():
    st.markdown("**Department & FY-wise Trend**")
    
    # Prepare data for waterfall
    fy_data = df.groupby('FY')['Bill_Value'].sum().reset_index()
    fy_data['Change'] = fy_data['Bill_Value'].diff().fillna(fy_data['Bill_Value'].iloc[0])
    
    # Create waterfall chart with adjusted margins
    fig_fy = go.Figure(go.Waterfall(
        x=fy_data['FY'],
        y=fy_data['Change'],
        measure=['absolute'] + ['relative']*(len(fy_data)-1),
        text=[f"₹{x:,.0f}" for x in fy_data['Bill_Value']],
        connector={"line":{"color":"rgb(63, 63, 63)"}},
    ))
    
    fig_fy.update_layout(
        height=400,  # Increased height
        margin=dict(l=80, r=80, t=60, b=100),  # Expanded margins
        yaxis_title="Bill Value Change (₹)",
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis_tickangle=-30  # Angle labels if needed
    )
    
    # Format with padding
    fig_fy.update_traces(
        increasing={"marker":{"color":"#2ca02c"}},
        decreasing={"marker":{"color":"#d62728"}},
        textposition="outside",
        textfont_size=10,  # Slightly smaller text
        outsidetextfont=dict(size=10, color='black'),
        cliponaxis=False  # Prevent text clipping
    )
    
    st.plotly_chart(fig_fy, use_container_width=True)

def sec3_col9():
    st.markdown("**Vendor Contribution by Financial Year**")
    
    try:
        # Create vendor dropdown
        all_vendors = df['Vendor Name'].unique()
        selected_vendor = st.selectbox(
            "Select Vendor:",
            options=all_vendors,
            index=0,  # Default to first vendor
            key="vendor_waterfall"
        )
        
        # Prepare data for selected vendor
        vendor_fy_data = df[df['Vendor Name'] == selected_vendor].groupby('FY')['Bill_Value'].sum().reset_index()
        
        # Check if vendor has multi-year data
        if len(vendor_fy_data) < 2:
            st.warning(f"⚠️ {selected_vendor} has only 1 year of data - cannot show trends")
            vendor_fy_data['Change'] = vendor_fy_data['Bill_Value']
        else:
            vendor_fy_data['Change'] = vendor_fy_data['Bill_Value'].diff().fillna(vendor_fy_data['Bill_Value'].iloc[0])
        
        # Create waterfall chart
        fig = go.Figure(go.Waterfall(
            name="Contribution",
            x=vendor_fy_data['FY'],
            y=vendor_fy_data['Change'],
            measure=['absolute'] + ['relative']*(len(vendor_fy_data)-1),
            text=[f"₹{x:,.0f}" for x in vendor_fy_data['Bill_Value']],
            connector={"line":{"color":"#666","width":1.2}},
            increasing={"marker":{"color":"#4C78A8"}},
            decreasing={"marker":{"color":"#E45756"}},
            totals={"marker":{"color":"#54A24B"}}
        ))
        
        # Format layout
        fig.update_layout(
            title=dict(text=f"Yearly Contribution: {selected_vendor}", 
                      x=0.5, xanchor='center', font=dict(size=14)),
            height=450,
            margin=dict(l=80, r=80, t=100, b=120),
            yaxis_title="Amount (₹)",
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            xaxis=dict(tickangle=-30 if len(vendor_fy_data) > 3 else 0)
        )
        
        # Format traces
        fig.update_traces(
            textposition="outside",
            textfont=dict(size=10),
            outsidetextfont=dict(size=10, color='black'),
            cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>Change: ₹%{y:,.0f}<br>Total: ₹%{text}<extra></extra>"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error generating vendor analysis: {str(e)}")
        st.info("Required columns: 'Vendor Name', 'Bill_Value', 'FY'")