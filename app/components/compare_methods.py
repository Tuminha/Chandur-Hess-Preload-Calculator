#!/usr/bin/env python3
"""
Compare Methods Component

This component provides a comparison between the Wadhwani-Hess method
and conventional preload calculation methods.
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
    estimate_uncertainty,
    calculate_preload_range
)
from src.core.torque import (
    estimate_preload_from_torque,
    calculate_stress_from_preload,
    calculate_safety_factor,
    calculate_tensile_area,
    assess_risk
)


def show_compare_methods():
    """Display a comparison between calculation methods."""
    st.markdown('<h1 class="main-header">Compare Methods</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">Wadhwani-Hess vs. Conventional Methods</h2>', unsafe_allow_html=True)
    
    # Main container
    with st.container():
        st.markdown("""
        <div style="background-color: #1e2a38; color: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <p style="font-size: 1.05rem; line-height: 1.6; margin: 0;">This component demonstrates the advantages of the Wadhwani-Hess method over conventional
            methods for preload calculation. The key difference is improved accuracy with reduced
            uncertainty (±9% vs. ±35%).</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Input method selection
        input_method = st.radio(
            "Input Method",
            ["Select from Implant System Database", "Manual Entry"],
            horizontal=True
        )
        
        # Main column layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Input Parameters")
            
            if input_method == "Select from Implant System Database":
                # Get implant systems data
                implant_data = st.session_state.implant_data
                
                # System selection
                system_names = list(implant_data["implant_systems"].keys())
                selected_system = st.selectbox(
                    "Select Implant System",
                    system_names,
                    format_func=lambda x: x.replace("_", " ")
                )
                
                # Model selection
                model_names = list(implant_data["implant_systems"][selected_system].keys())
                selected_model = st.selectbox(
                    "Select Model",
                    model_names,
                    format_func=lambda x: x.replace("_", " ")
                )
                
                # Get screw data
                screw_data = implant_data["implant_systems"][selected_system][selected_model]["screws"]["standard"]
                
                # Display information about the selected system
                st.markdown(f"""
                <div style="background-color: #ffffff; color: #333333; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h4 style="color: #2c3e50; margin-bottom: 15px;">{selected_system.replace('_', ' ')} {selected_model}</h4>
                    <ul style="font-size: 1.05rem; line-height: 1.5; color: #333333;">
                        <li>Connection Type: {implant_data["implant_systems"][selected_system][selected_model]["connection_type"]}</li>
                        <li>Screw Material: {screw_data["material"]}</li>
                        <li>Recommended Torque: {screw_data["recommended_torque"]} N-cm</li>
                        <li>Screw Diameter: {screw_data["diameter"]} mm</li>
                        <li>Thread Pitch: {screw_data["thread_pitch"]} mm</li>
                        <li>K-Factor: {screw_data["K_factor"]}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Default values from database
                torque = float(screw_data["recommended_torque"])
                diameter = float(screw_data["diameter"]) / 10  # mm to cm
                thread_pitch = float(screw_data["thread_pitch"]) / 10  # mm to cm
                k_factor = float(screw_data["K_factor"])
                removal_torque = torque * 0.85  # Default estimate
                yield_strength = float(screw_data["yield_strength"])
            
            else:  # Manual Entry
                # Default values for manual entry
                torque = st.number_input(
                    "Tightening Torque (N-cm)",
                    min_value=1.0,
                    max_value=100.0,
                    value=35.0,
                    step=0.1
                )
                
                diameter = st.number_input(
                    "Screw Diameter (mm)",
                    min_value=0.5,
                    max_value=5.0,
                    value=2.0,
                    step=0.1
                ) / 10  # Convert to cm
                
                thread_pitch = st.number_input(
                    "Thread Pitch (mm)",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.4,
                    step=0.05
                ) / 10  # Convert to cm
                
                k_factor = st.number_input(
                    "K-Factor",
                    min_value=0.1,
                    max_value=0.5,
                    value=0.2,
                    step=0.01,
                    help="Also known as 'nut factor', typically 0.2 for lubricated screws"
                )
                
                removal_torque = st.number_input(
                    "Removal Torque (N-cm)",
                    min_value=1.0,
                    max_value=torque - 0.1,
                    value=min(torque * 0.85, torque - 0.1),
                    step=0.1
                )
                
                yield_strength = st.number_input(
                    "Yield Strength (MPa)",
                    min_value=100,
                    max_value=1500,
                    value=950,
                    step=50,
                    help="For titanium alloy (Ti-6Al-4V), typically around 950 MPa"
                )
            
            # Calculate button
            calculate_pressed = st.button("Compare Methods", type="primary", use_container_width=True)
        
        with col2:
            st.subheader("Comparison Results")
            
            if calculate_pressed or st.session_state.get('last_calculation') == 'compare':
                # Store calculation type
                st.session_state.last_calculation = 'compare'
                
                # Calculate preload using conventional method
                conventional_preload = estimate_preload_from_torque(torque, diameter, k_factor)
                
                # Get uncertainty for conventional method
                conv_uncertainty, _ = estimate_uncertainty(torque, False)
                
                # Calculate preload range for conventional method
                conv_min_preload, conv_max_preload = calculate_preload_range(
                    conventional_preload, 
                    conv_uncertainty
                )
                
                # Calculate preload using Wadhwani-Hess method
                wh_preload = calculate_preload(torque, removal_torque, thread_pitch)
                
                # Uncertainty for Wadhwani-Hess method (9% as per the paper)
                wh_uncertainty = 9
                
                # Calculate preload range for Wadhwani-Hess method
                wh_min_preload, wh_max_preload = calculate_preload_range(
                    wh_preload, 
                    wh_uncertainty
                )
                
                # Calculate tensile area and stress
                tensile_area = calculate_tensile_area(diameter * 10, thread_pitch * 10)  # Convert back to mm
                
                # Calculate stress for both methods
                conv_stress = calculate_stress_from_preload(conventional_preload, tensile_area)
                wh_stress = calculate_stress_from_preload(wh_preload, tensile_area)
                
                # Calculate safety factors
                conv_safety = calculate_safety_factor(conv_stress, yield_strength)
                wh_safety = calculate_safety_factor(wh_stress, yield_strength)
                
                # Assess risk for both methods
                conv_risk, conv_recommendation = assess_risk(conv_safety)
                wh_risk, wh_recommendation = assess_risk(wh_safety)
                
                # Create a comparison table
                comp_data = {
                    "Method": ["Conventional", "Wadhwani-Hess"],
                    "Preload (N)": [f"{conventional_preload:.2f}", f"{wh_preload:.2f}"],
                    "Uncertainty": [f"±{conv_uncertainty}%", f"±{wh_uncertainty}%"],
                    "Preload Range (N)": [
                        f"{conv_min_preload:.2f} - {conv_max_preload:.2f}",
                        f"{wh_min_preload:.2f} - {wh_max_preload:.2f}"
                    ],
                    "Stress (MPa)": [f"{conv_stress:.2f}", f"{wh_stress:.2f}"],
                    "Safety Factor": [f"{conv_safety:.2f}", f"{wh_safety:.2f}"],
                    "Risk Level": [conv_risk, wh_risk]
                }
                
                # Display the comparison table
                st.markdown("""
                <h4>Preload Calculation Comparison</h4>
                """, unsafe_allow_html=True)
                
                df = pd.DataFrame(comp_data)
                st.dataframe(df, hide_index=True, use_container_width=True)
                
                # Check if WH preload is within conventional range
                in_conventional_range = conv_min_preload <= wh_preload <= conv_max_preload
                
                if in_conventional_range:
                    st.success("✅ Wadhwani-Hess preload is within the conventional method's uncertainty range.")
                else:
                    st.warning("⚠️ Wadhwani-Hess preload is outside the conventional method's uncertainty range.")
                
                # Calculate uncertainty reduction
                uncertainty_reduction = (conv_uncertainty - wh_uncertainty) / conv_uncertainty * 100
                
                # Calculate preload percentage difference (WH compared to conventional)
                preload_difference = ((wh_preload - conventional_preload) / conventional_preload) * 100
                
                st.info(f"📊 The Wadhwani-Hess method reduces uncertainty by {uncertainty_reduction:.1f}%")
                
                # Risk assessment
                if wh_risk != conv_risk:
                    st.warning(f"""
                    ⚠️ Risk level assessment differs between methods:
                    - Conventional: {conv_risk} risk
                    - Wadhwani-Hess: {wh_risk} risk
                    """)
                
                # Visualization - Preload Range Comparison
                fig = go.Figure()
                
                # Add conventional method range
                fig.add_trace(go.Bar(
                    name="Conventional Method",
                    x=["Conventional"],
                    y=[conventional_preload],
                    error_y=dict(
                        type='data',
                        symmetric=False,
                        array=[conv_max_preload - conventional_preload],
                        arrayminus=[conventional_preload - conv_min_preload],
                        color="rgba(31, 119, 180, 0.6)"
                    ),
                    marker_color="rgba(31, 119, 180, 0.6)"
                ))
                
                # Add Wadhwani-Hess method range
                fig.add_trace(go.Bar(
                    name="Wadhwani-Hess Method",
                    x=["Wadhwani-Hess"],
                    y=[wh_preload],
                    error_y=dict(
                        type='data',
                        symmetric=False,
                        array=[wh_max_preload - wh_preload],
                        arrayminus=[wh_preload - wh_min_preload],
                        color="rgba(255, 127, 14, 0.6)"
                    ),
                    marker_color="rgba(255, 127, 14, 0.6)"
                ))
                
                fig.update_layout(
                    title="Preload Range Comparison",
                    yaxis_title="Preload (N)",
                    barmode='group',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Formula details
                with st.expander("See Calculation Details"):
                    st.markdown(f"""
                    <h4>Conventional Method:</h4>
                    <p>P = T / (K × d)</p>
                    <p>P = {torque} / ({k_factor} × {diameter})</p>
                    <p>P = {torque} / {k_factor * diameter:.4f}</p>
                    <p>P = {conventional_preload:.2f} N</p>
                    
                    <h4>Wadhwani-Hess Method:</h4>
                    <p>P = (T<sub>t</sub> - T<sub>r</sub>) × π / p</p>
                    <p>P = ({torque} - {removal_torque}) × π / {thread_pitch}</p>
                    <p>P = {torque - removal_torque} × {math.pi:.4f} / {thread_pitch}</p>
                    <p>P = {((torque - removal_torque) * math.pi):.4f} / {thread_pitch}</p>
                    <p>P = {wh_preload:.2f} N</p>
                    """, unsafe_allow_html=True)
                
                # Store results in session state for reporting
                st.session_state.calculation_results['compare'] = {
                    'torque': torque,
                    'removal_torque': removal_torque,
                    'diameter': diameter,
                    'thread_pitch': thread_pitch,
                    'k_factor': k_factor,
                    'conventional_preload': conventional_preload,
                    'wh_preload': wh_preload,
                    'conv_uncertainty': conv_uncertainty,
                    'wh_uncertainty': wh_uncertainty,
                    'conv_min_preload': conv_min_preload,
                    'conv_max_preload': conv_max_preload,
                    'wh_min_preload': wh_min_preload,
                    'wh_max_preload': wh_max_preload,
                    'uncertainty_reduction': uncertainty_reduction,
                    'preload_difference': preload_difference,
                    'conv_stress': conv_stress,
                    'wh_stress': wh_stress,
                    'conv_safety': conv_safety,
                    'wh_safety': wh_safety,
                    'conv_risk': conv_risk,
                    'wh_risk': wh_risk,
                    'in_conventional_range': in_conventional_range
                }
                
                if input_method == "Select from Implant System Database":
                    st.session_state.calculation_results['compare']['system'] = selected_system
                    st.session_state.calculation_results['compare']['model'] = selected_model 