#!/usr/bin/env python3
"""
Implant Systems Analysis Component

This component allows users to analyze and compare different implant systems
using both the Wadhwani-Hess and conventional methods.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import math
import json
from pathlib import Path

# Import calculation functions
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.preload import (
    calculate_preload,
    estimate_uncertainty
)
from src.core.torque import (
    estimate_preload_from_torque,
    calculate_stress_from_preload,
    calculate_safety_factor,
    calculate_tensile_area,
    assess_risk
)


def show_implant_systems_analysis():
    """Display analysis of different implant systems."""
    st.markdown('<h1 class="main-header">Implant Systems Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">Compare preload and safety across implant systems</h2>', unsafe_allow_html=True)
    
    # Get implant systems data
    implant_data = st.session_state.implant_data
    
    # Main container
    with st.container():
        st.markdown("""
        <div style="background-color: #1e2a38; color: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <p style="font-size: 1.05rem; line-height: 1.6; margin: 0;">This analysis provides a comprehensive comparison of different implant systems
            and their preload characteristics using both the Wadhwani-Hess method and conventional methods.
            The analysis evaluates preload, stress, safety factors, and risk levels for each system,
            helping clinicians make informed decisions based on scientific data.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Removal torque assumption
        removal_factor = st.slider(
            "Removal Torque Factor (% of tightening torque)",
            min_value=70,
            max_value=95,
            value=85,
            step=5,
            help="Estimate of removal torque as a percentage of tightening torque"
        ) / 100.0
        
        # Generate data for all implant systems
        analysis_data = generate_implant_analysis(implant_data, removal_factor)
        
        # Display the analysis
        show_analysis_results(analysis_data)


def generate_implant_analysis(implant_data, removal_factor=0.85):
    """Generate analysis data for all implant systems."""
    analysis = []
    
    # Loop through all implant systems
    for system_name, system_data in implant_data["implant_systems"].items():
        for model_name, model_data in system_data.items():
            # Get screw data
            screw_data = model_data["screws"]["standard"]
            
            # Extract parameters
            torque = float(screw_data["recommended_torque"])  # N-cm
            diameter = float(screw_data["diameter"]) / 10  # mm to cm
            thread_pitch = float(screw_data["thread_pitch"]) / 10  # mm to cm
            k_factor = float(screw_data["K_factor"])
            yield_strength = float(screw_data["yield_strength"])  # MPa
            
            # Estimate removal torque
            removal_torque = torque * removal_factor
            
            # Calculate tensile area
            tensile_area = calculate_tensile_area(float(screw_data["diameter"]), float(screw_data["thread_pitch"]))
            
            # Calculate conventional preload and uncertainty
            conventional_preload = estimate_preload_from_torque(torque, diameter, k_factor)
            conv_uncertainty, _ = estimate_uncertainty(torque, False)
            
            # Calculate Wadhwani-Hess preload and uncertainty
            wh_preload = calculate_preload(torque, removal_torque, thread_pitch)
            wh_uncertainty = 9  # 9% as per the paper
            
            # Calculate stress for both methods
            conv_stress = calculate_stress_from_preload(conventional_preload, tensile_area)
            wh_stress = calculate_stress_from_preload(wh_preload, tensile_area)
            
            # Calculate safety factors
            conv_safety = calculate_safety_factor(conv_stress, yield_strength)
            wh_safety = calculate_safety_factor(wh_stress, yield_strength)
            
            # Assess risk for both methods
            conv_risk, _ = assess_risk(conv_safety)
            wh_risk, _ = assess_risk(wh_safety)
            
            # Check if WH preload is within conventional range
            conv_min = conventional_preload * (1 - conv_uncertainty/100)
            conv_max = conventional_preload * (1 + conv_uncertainty/100)
            in_range = conv_min <= wh_preload <= conv_max
            
            # Calculate uncertainty reduction
            uncertainty_reduction = (conv_uncertainty - wh_uncertainty) / conv_uncertainty * 100
            
            # Add to analysis data
            analysis.append({
                "System": system_name.replace("_", " "),
                "Model": model_name.replace("_", " "),
                "Connection Type": model_data["connection_type"],
                "Recommended Torque (N-cm)": torque,
                "Diameter (mm)": screw_data["diameter"],
                "Thread Pitch (mm)": screw_data["thread_pitch"],
                "K-Factor": k_factor,
                "Yield Strength (MPa)": yield_strength,
                "Conventional Preload (N)": conventional_preload,
                "WH Preload (N)": wh_preload,
                "Conv Uncertainty (%)": conv_uncertainty,
                "WH Uncertainty (%)": wh_uncertainty,
                "Conv Stress (MPa)": conv_stress,
                "WH Stress (MPa)": wh_stress,
                "Conv Safety Factor": conv_safety,
                "WH Safety Factor": wh_safety,
                "Conv Risk Level": conv_risk,
                "WH Risk Level": wh_risk,
                "In Conv Range": in_range,
                "Uncertainty Reduction (%)": uncertainty_reduction,
                "Preload Difference (%)": (conventional_preload - wh_preload) / conventional_preload * 100
            })
    
    return analysis


def show_analysis_results(analysis_data):
    """Display the analysis results."""
    # Convert to DataFrame
    df = pd.DataFrame(analysis_data)
    
    # Create main table view
    st.subheader("Implant Systems Comparison")
    
    # Select columns for display
    display_cols = [
        "System", "Model", "Recommended Torque (N-cm)", 
        "Conventional Preload (N)", "WH Preload (N)", 
        "Conv Uncertainty (%)", "WH Uncertainty (%)",
        "Conv Safety Factor", "WH Safety Factor",
        "Conv Risk Level", "WH Risk Level"
    ]
    
    # Display table
    st.dataframe(df[display_cols], use_container_width=True)
    
    # Summary metrics
    st.subheader("Summary Metrics")
    
    # Calculate averages
    avg_conv_preload = df["Conventional Preload (N)"].mean()
    avg_wh_preload = df["WH Preload (N)"].mean()
    avg_reduction = df["Uncertainty Reduction (%)"].mean()
    avg_preload_diff = df["Preload Difference (%)"].mean()
    
    # Display metrics in columns
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.metric(
            label="Avg. Conventional Preload",
            value=f"{avg_conv_preload:.2f} N"
        )
    
    with metric_cols[1]:
        st.metric(
            label="Avg. Wadhwani-Hess Preload",
            value=f"{avg_wh_preload:.2f} N",
            delta=f"{-avg_preload_diff:.1f}%",
            delta_color="inverse"
        )
    
    with metric_cols[2]:
        st.metric(
            label="Avg. Uncertainty Reduction",
            value=f"{avg_reduction:.1f}%",
            delta="Improved Accuracy"
        )
    
    with metric_cols[3]:
        systems_in_range = df["In Conv Range"].sum()
        st.metric(
            label="Systems in Conventional Range",
            value=f"{systems_in_range}/{len(df)}",
            delta=f"{systems_in_range/len(df)*100:.1f}%"
        )
    
    # Risk level breakdown
    st.subheader("Risk Level Distribution")
    
    # Calculate risk level counts
    conv_risk_counts = df["Conv Risk Level"].value_counts().reset_index()
    conv_risk_counts.columns = ["Risk Level", "Count"]
    conv_risk_counts["Method"] = "Conventional"
    
    wh_risk_counts = df["WH Risk Level"].value_counts().reset_index()
    wh_risk_counts.columns = ["Risk Level", "Count"]
    wh_risk_counts["Method"] = "Wadhwani-Hess"
    
    # Combine risk data
    risk_data = pd.concat([conv_risk_counts, wh_risk_counts])
    
    # Create risk distribution chart
    fig = px.bar(
        risk_data,
        x="Risk Level",
        y="Count",
        color="Method",
        barmode="group",
        title="Risk Level Distribution by Method",
        category_orders={"Risk Level": ["Low", "Medium", "High"]}
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Preload comparison chart
    st.subheader("Preload Comparison by System")
    
    # Create system labels for X-axis
    df["System_Model"] = df["System"] + " " + df["Model"]
    
    # Create preload comparison chart
    fig2 = go.Figure()
    
    # Calculate error values for conventional method
    conv_error_values = df["Conventional Preload (N)"] * df["Conv Uncertainty (%)"] / 100
    
    fig2.add_trace(go.Bar(
        name="Conventional",
        x=df["System_Model"],
        y=df["Conventional Preload (N)"],
        error_y=dict(
            type="data",
            array=conv_error_values.tolist(),
            visible=True
        ),
        marker_color="#1f77b4"
    ))
    
    # Calculate error values for Wadhwani-Hess method
    wh_error_values = df["WH Preload (N)"] * df["WH Uncertainty (%)"] / 100
    
    fig2.add_trace(go.Bar(
        name="Wadhwani-Hess",
        x=df["System_Model"],
        y=df["WH Preload (N)"],
        error_y=dict(
            type="data",
            array=wh_error_values.tolist(),
            visible=True
        ),
        marker_color="#ff7f0e"
    ))
    
    fig2.update_layout(
        title="Preload Comparison by Implant System",
        xaxis_title="Implant System",
        yaxis_title="Preload (N)",
        barmode="group",
        height=500
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Safety factor comparison
    st.subheader("Safety Factor Analysis")
    
    # Create safety factor chart
    fig3 = go.Figure()
    
    # Add safety limit line
    fig3.add_shape(
        type="line",
        x0=-0.5,
        y0=1.5,
        x1=len(df) - 0.5,
        y1=1.5,
        line=dict(
            color="red",
            width=2,
            dash="dash",
        )
    )
    
    fig3.add_annotation(
        x=len(df) - 1,
        y=1.55,
        text="Safety Threshold",
        showarrow=False,
        font=dict(color="red")
    )
    
    fig3.add_trace(go.Bar(
        name="Conventional",
        x=df["System_Model"],
        y=df["Conv Safety Factor"],
        marker_color="#1f77b4"
    ))
    
    fig3.add_trace(go.Bar(
        name="Wadhwani-Hess",
        x=df["System_Model"],
        y=df["WH Safety Factor"],
        marker_color="#ff7f0e"
    ))
    
    fig3.update_layout(
        title="Safety Factor by Implant System",
        xaxis_title="Implant System",
        yaxis_title="Safety Factor",
        barmode="group",
        height=500
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # Detailed data table
    with st.expander("View Full Analysis Data"):
        st.dataframe(df, use_container_width=True)
    
    # Export option
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Analysis as CSV",
        data=csv,
        file_name="implant_systems_analysis.csv",
        mime="text/csv",
        help="Download the complete analysis data for further processing"
    ) 