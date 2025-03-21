#!/usr/bin/env python3
"""
Final Torque Calculator Component

This component allows users to calculate the final torque needed to achieve
a desired preload using the Wadhwani-Hess method.
"""

import streamlit as st
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
    calculate_final_torque,
    calculate_self_loosening,
    calculate_primary_locking
)


def show_final_torque_calculator():
    """Display the final torque calculator interface."""
    st.markdown('<h1 class="main-header">Final Torque Calculator</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">Calculate required torque for desired preload</h2>', unsafe_allow_html=True)
    
    # Main container
    with st.container():
        st.markdown("""
        <div style="background-color: #1e2a38; color: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <p style="font-size: 1.05rem; line-height: 1.6; margin: 0;">This calculator implements <b>Equation 6</b> from the Wadhwani-Hess paper:
            <br>T<sub>i</sub> = (p × T<sub>t initial</sub> × P<sub>desired</sub>) / (π × (T<sub>t initial</sub> - T<sub>r</sub>))</p>
            <p style="font-size: 1.05rem; line-height: 1.6; margin-top: 0.5rem;">Where T<sub>i</sub> is final torque, p is thread pitch, T<sub>t initial</sub> is initial tightening torque,
            T<sub>r</sub> is removal torque, and P<sub>desired</sub> is the desired preload.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Input method selection
        input_method = st.radio(
            "Input Method",
            ["Select from Implant System Database", "Manual Entry"],
            horizontal=True
        )
        
        # Two columns for input and results
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
                <div style="background-color: white; color: #333; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h4 style="color: #1e2a38; margin-bottom: 0.75rem;">{selected_system.replace('_', ' ')} {selected_model}</h4>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li style="margin-bottom: 0.5rem;"><b>Connection Type:</b> {implant_data["implant_systems"][selected_system][selected_model]["connection_type"]}</li>
                        <li style="margin-bottom: 0.5rem;"><b>Screw Material:</b> {screw_data["material"]}</li>
                        <li style="margin-bottom: 0.5rem;"><b>Recommended Torque:</b> {screw_data["recommended_torque"]} N-cm</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Prefill thread pitch from database but allow override
                thread_pitch_mm = st.number_input(
                    "Thread Pitch (mm)",
                    min_value=0.1,
                    max_value=1.0,
                    value=float(screw_data["thread_pitch"]),
                    step=0.05,
                    format="%.2f"
                )
                thread_pitch = thread_pitch_mm / 10  # Convert mm to cm
                
                # Default torque values
                default_initial_torque = float(screw_data["recommended_torque"]) * 0.7  # Lower initial torque for test
                default_removal_torque = default_initial_torque * 0.85  # Estimate removal as 85% of initial
                
                # Calculate conventional preload estimate for reference
                diameter_cm = float(screw_data["diameter"]) / 10  # mm to cm
                k_factor = float(screw_data["K_factor"])
                conventional_preload = float(screw_data["recommended_torque"]) / (k_factor * diameter_cm)
            
            else:  # Manual Entry
                thread_pitch_mm = st.number_input(
                    "Thread Pitch (mm)",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.4,
                    step=0.05,
                    format="%.2f"
                )
                thread_pitch = thread_pitch_mm / 10  # Convert mm to cm
                
                # Default torque values for manual entry
                default_initial_torque = 25.0
                default_removal_torque = 21.4
            
            # Initial measurements
            st.subheader("Initial Measurements")
            initial_torque = st.number_input(
                "Initial Tightening Torque (N-cm)",
                min_value=1.0,
                max_value=100.0,
                value=default_initial_torque,
                step=0.1,
                format="%.1f",
                help="Lower initial torque used to measure removal torque"
            )
            
            removal_torque = st.number_input(
                "Removal Torque (N-cm)",
                min_value=1.0,
                max_value=initial_torque - 0.1,  # Must be less than tightening
                value=min(default_removal_torque, initial_torque - 0.1),
                step=0.1,
                format="%.1f",
                help="Measured torque when loosening the screw"
            )
            
            # Calculate initial preload
            initial_preload = calculate_preload(initial_torque, removal_torque, thread_pitch)
            
            st.info(f"Measured Initial Preload: {initial_preload:.2f} N")
            
            # Target preload
            st.subheader("Target Preload")
            
            # Calculate max allowed value for desired preload
            max_desired_preload = initial_preload * 3.0
            
            # Ensure default_desired_preload doesn't exceed max_value
            if input_method == "Select from Implant System Database":
                default_desired_preload = min(conventional_preload, max_desired_preload)
            else:
                default_desired_preload = min(400.0, max_desired_preload)
            
            desired_preload = st.number_input(
                "Desired Preload (N)",
                min_value=initial_preload * 0.5,
                max_value=max_desired_preload,
                value=default_desired_preload,
                step=10.0,
                format="%.1f",
                help="Target preload you want to achieve"
            )
            
            # Calculate button
            calculate_pressed = st.button("Calculate Final Torque", type="primary", use_container_width=True)
        
        with col2:
            st.subheader("Results")
            
            if calculate_pressed or st.session_state.get('last_calculation') == 'final_torque':
                # Store calculation type
                st.session_state.last_calculation = 'final_torque'
                
                # Calculate final torque using the exact formula (Equation 6)
                final_torque = calculate_final_torque(
                    initial_torque, 
                    removal_torque, 
                    initial_preload, 
                    desired_preload, 
                    thread_pitch,
                    use_ratio_method=False
                )
                
                # Also calculate with ratio method for comparison
                final_torque_ratio = calculate_final_torque(
                    initial_torque, 
                    removal_torque, 
                    initial_preload, 
                    desired_preload, 
                    thread_pitch,
                    use_ratio_method=True
                )
                
                # Uncertainty range (9% as per the paper)
                uncertainty_percent = 9
                min_preload = desired_preload * (1 - uncertainty_percent/100)
                max_preload = desired_preload * (1 + uncertainty_percent/100)
                
                # Display the main result with large font
                st.markdown(f"""
                <div style="background-color: #1e2a38; color: white; text-align: center; padding: 2rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h3 style="color: white; margin-bottom: 1rem;">Final Tightening Torque</h3>
                    <p style="font-size: 2.5rem; font-weight: bold; color: white; margin-bottom: 0.5rem;">
                        {final_torque:.2f} N-cm
                    </p>
                    <p>To achieve {desired_preload:.2f} N preload (±{uncertainty_percent}%)</p>
                    <p>Preload Range: {min_preload:.2f} N to {max_preload:.2f} N</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show ratio method result for comparison
                st.markdown(f"""
                <p><b>Alternative Calculation (Ratio Method):</b> {final_torque_ratio:.2f} N-cm 
                <span style="color: #6c757d; font-size: 0.9rem;">
                    (Difference: {abs(final_torque - final_torque_ratio):.2f} N-cm)
                </span></p>
                """, unsafe_allow_html=True)
                
                # Create torque-preload chart
                torque_range = np.linspace(initial_torque * 0.5, final_torque * 1.5, 100)
                preload_values = [(torque/initial_torque) * initial_preload for torque in torque_range]
                
                fig = px.line(
                    x=torque_range,
                    y=preload_values,
                    labels={"x": "Torque (N-cm)", "y": "Preload (N)"},
                    title="Torque-Preload Relationship"
                )
                
                # Add markers for initial and final points
                fig.add_scatter(
                    x=[initial_torque, final_torque],
                    y=[initial_preload, desired_preload],
                    mode="markers+text",
                    marker=dict(size=10, color=["blue", "red"]),
                    text=["Initial", "Final"],
                    textposition="top center",
                    showlegend=False
                )
                
                # Add horizontal line for target preload
                fig.add_shape(
                    type="line",
                    x0=initial_torque * 0.5,
                    y0=desired_preload,
                    x1=final_torque,
                    y1=desired_preload,
                    line=dict(color="green", width=2, dash="dash"),
                )
                
                # Add vertical line for calculated torque
                fig.add_shape(
                    type="line",
                    x0=final_torque,
                    y0=0,
                    x1=final_torque,
                    y1=desired_preload,
                    line=dict(color="red", width=2, dash="dash"),
                )
                
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                # Formula details
                with st.expander("See Calculation Details"):
                    st.markdown(f"""
                    <h4>Exact Formula (Equation 6):</h4>
                    <p>T<sub>i</sub> = (p × T<sub>t initial</sub> × P<sub>desired</sub>) / (π × (T<sub>t initial</sub> - T<sub>r</sub>))</p>
                    <p>T<sub>i</sub> = ({thread_pitch} × {initial_torque} × {desired_preload}) / (π × ({initial_torque} - {removal_torque}))</p>
                    <p>T<sub>i</sub> = ({thread_pitch * initial_torque * desired_preload:.2f}) / ({math.pi:.4f} × {initial_torque - removal_torque:.2f})</p>
                    <p>T<sub>i</sub> = ({thread_pitch * initial_torque * desired_preload:.2f}) / ({math.pi * (initial_torque - removal_torque):.4f})</p>
                    <p>T<sub>i</sub> = {final_torque:.2f} N-cm</p>
                    
                    <h4>Ratio Method:</h4>
                    <p>T<sub>i</sub> = T<sub>t initial</sub> × (P<sub>desired</sub> / P<sub>initial</sub>)</p>
                    <p>T<sub>i</sub> = {initial_torque} × ({desired_preload} / {initial_preload:.2f})</p>
                    <p>T<sub>i</sub> = {initial_torque} × {desired_preload / initial_preload:.4f}</p>
                    <p>T<sub>i</sub> = {final_torque_ratio:.2f} N-cm</p>
                    """, unsafe_allow_html=True)
                
                # Store results in session state for reporting
                st.session_state.calculation_results['final_torque'] = {
                    'initial_torque': initial_torque,
                    'removal_torque': removal_torque,
                    'thread_pitch': thread_pitch,
                    'initial_preload': initial_preload,
                    'desired_preload': desired_preload,
                    'final_torque': final_torque,
                    'final_torque_ratio': final_torque_ratio,
                    'min_preload': min_preload,
                    'max_preload': max_preload,
                    'uncertainty_percent': uncertainty_percent,
                }
                
                if input_method == "Select from Implant System Database":
                    st.session_state.calculation_results['final_torque']['system'] = selected_system
                    st.session_state.calculation_results['final_torque']['model'] = selected_model 