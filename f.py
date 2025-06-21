import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import f



def tab2_Col1(vendor_data):
    
    st.markdown("""
            <div style='margin-bottom: -20px;'>
                <div style='font-size: 0.9em;'>Total Amount</div>
                <div style='font-size: 1.3em; font-weight: bold;'>₹{:,}</div>
            </div>
            """.format(total_amount), unsafe_allow_html=True)
    with st.expander(" ", expanded=False):
        st.caption(f"✅ Paid: ₹ paid_amount")
        st.caption(f"🔄 In Progress: ₹ inprogress_amount")
    
    st.write("FY wise Expense for that Vendor")



def tab2_Col2(vendor_data,filtered_df):
    total_amount = vendor_data['BILLVALUE'].sum()
    paid_amount = vendor_data[vendor_data['STATUS'] == 'Paid']['BILLVALUE'].sum()
    inprogress_amount = vendor_data[vendor_data['STATUS'] == 'In Progress']['BILLVALUE'].sum()
    total_bills = len(vendor_data)
    paid_bills = len(vendor_data[vendor_data['STATUS'] == 'Paid'])
    inprogress_bills = len(vendor_data[vendor_data['STATUS'] == 'In Progress'])
    median_days = vendor_data['TOTAL_DAYS_for_PAYMENT'].median()
    fast_payments = len(vendor_data[vendor_data['TOTAL_DAYS_for_PAYMENT'] <= 10])
    st.markdown("""
            <div style='margin-bottom: -20px;'>
                <div style='font-size: 0.9em;'>Total Bills</div>
                <div style='font-size: 1.3em; font-weight: bold;'>{:,}</div>
            </div>
            """.format(total_bills), unsafe_allow_html=True)
    with st.expander(" ", expanded=False):
        st.caption(f"✅ Paid: {paid_bills}")
        st.caption(f"🔄 In Progress: {inprogress_bills}")

    st.write("User Wise Expense")
    
    

def tab2_Col3(vendor_data):

    total_amount = vendor_data['BILLVALUE'].sum()
    paid_amount = vendor_data[vendor_data['STATUS'] == 'Paid']['BILLVALUE'].sum()
    inprogress_amount = vendor_data[vendor_data['STATUS'] == 'In Progress']['BILLVALUE'].sum()
    total_bills = len(vendor_data)
    paid_bills = len(vendor_data[vendor_data['STATUS'] == 'Paid'])
    inprogress_bills = len(vendor_data[vendor_data['STATUS'] == 'In Progress'])
    median_days = vendor_data['TOTAL_DAYS_for_PAYMENT'].median()
    fast_payments = len(vendor_data[vendor_data['TOTAL_DAYS_for_PAYMENT'] <= 10])

    days_stats = vendor_data['TOTAL_DAYS_for_PAYMENT'].describe()
    median_days = days_stats['50%']
    
    st.markdown("""
    <div style='margin-bottom: -20px;'>
        <div style='font-size: 0.9em;'>Payment Days</div>
        <div style='font-size: 1.3em; font-weight: bold;'>{:.1f}</div>
    </div>
    """.format(median_days), unsafe_allow_html=True)
    with st.expander("Payment Speed Analysis", expanded=False):
        st.caption("🚀 Fastest Payment: {:.1f} days".format(days_stats['min']))
        st.caption("📊 Typical Fast Range (25th %): {:.1f} days".format(days_stats['25%']))
        st.caption("📌 Median Payment Time: {:.1f} days".format(days_stats['50%']))
        st.caption("📈 Typical Slow Range (75th %): {:.1f} days".format(days_stats['75%']))
        st.caption("🐢 Slowest Payment: {:.1f} days".format(days_stats['max'])) 

def tab2_Col4(vendor_data):
    total_amount = vendor_data['BILLVALUE'].sum()
    paid_amount = vendor_data[vendor_data['STATUS'] == 'Paid']['BILLVALUE'].sum()
    inprogress_amount = vendor_data[vendor_data['STATUS'] == 'In Progress']['BILLVALUE'].sum()
    total_bills = len(vendor_data)
    paid_bills = len(vendor_data[vendor_data['STATUS'] == 'Paid'])
    inprogress_bills = len(vendor_data[vendor_data['STATUS'] == 'In Progress'])
    median_days = vendor_data['TOTAL_DAYS_for_PAYMENT'].median()
    fast_payments = len(vendor_data[vendor_data['TOTAL_DAYS_for_PAYMENT'] <= 10])

    days_stats = vendor_data['TOTAL_DAYS_for_PAYMENT'].describe()
    median_days = days_stats['50%']
    # Department Distribution Bar Chart with fixed text display
    st.subheader("Department Distribution")
    dept_stats = vendor_data.groupby('DEPARTMENT').agg({
        'BILLVALUE': 'sum',
        'BILLNO': 'count'
    }).rename(columns={'BILLVALUE': 'Amount', 'BILLNO': 'Bill Count'}).sort_values('Amount')
    
    fig_bar = px.bar(
        dept_stats,
        x='Amount',
        y=dept_stats.index,
        orientation='h',
        color=dept_stats.index,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hover_data=['Bill Count'],
        text='Amount'
    )
    
    fig_bar.update_traces(
        texttemplate='₹%{text:,.0f}',
        textposition='auto',  # Changed from 'outside' to 'auto'
        hovertemplate="<b>%{y}</b><br>Amount: ₹%{x:,.2f}<br>Bills: %{customdata[0]}<extra></extra>",
        width=0.6,
        textfont_size=12  # Explicit font size
    )
    
    fig_bar.update_layout(
        showlegend=False,
        margin=dict(l=120, r=20, t=30, b=10),  # Increased left margin
        xaxis=dict(
            showgrid=False,
            range=[0, dept_stats['Amount'].max() * 1.2]  # Add 20% padding
        ),
        yaxis=dict(showgrid=False),
        height=300,
        uniformtext_minsize=8,  # Minimum text size
        uniformtext_mode='hide'  # Hide if doesn't fit
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)