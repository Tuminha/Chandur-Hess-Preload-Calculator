#!/usr/bin/env python3
"""
Preload Calculator Component

This component allows users to calculate preload from tightening and removal torque
using the Wadhwani-Hess method.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
import json
from pathlib import Path

# Import calculation functions
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.preload import (
    calculate_preload,
    calculate_self_loosening,
    calculate_primary_locking
)


def show_preload_calculator():
    """Display the preload calculator interface."""
    st.markdown('<h1 class="main-header">Preload Calculator</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">Calculate preload from torque measurements</h2>', unsafe_allow_html=True)
    
    # Main container
    with st.container():
        st.markdown("""
        <div style="background-color: #1e2a38; color: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <p style="font-size: 1.05rem; line-height: 1.6; margin: 0;">This calculator implements <b>Equation 3</b> from the Wadhwani-Hess paper:
            <br>P = (Tt - Tr) × π / p</p>
            <p style="font-size: 1.05rem; line-height: 1.6; margin-top: 0.5rem;">Where P is preload, Tt is tightening torque, Tr is removal torque, and p is thread pitch.</p>
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
                <div style="background-color: #ffffff; color: #333333; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h4 style="color: #2c3e50; margin-bottom: 15px;">{selected_system.replace('_', ' ')} {selected_model}</h4>
                    <ul style="font-size: 1.05rem; line-height: 1.5; color: #333333;">
                        <li>Connection Type: {implant_data["implant_systems"][selected_system][selected_model]["connection_type"]}</li>
                        <li>Screw Material: {screw_data["material"]}</li>
                        <li>Recommended Torque: {screw_data["recommended_torque"]} N-cm</li>
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
                default_tightening = float(screw_data["recommended_torque"])
                default_removal = default_tightening * 0.85  # Estimate removal as 85% of tightening
            
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
                default_tightening = 35.0
                default_removal = 29.5
            
            # Torque measurements
            tightening_torque = st.number_input(
                "Tightening Torque (N-cm)",
                min_value=1.0,
                max_value=100.0,
                value=default_tightening,
                step=0.1,
                format="%.1f"
            )
            
            removal_torque = st.number_input(
                "Removal Torque (N-cm)",
                min_value=1.0,
                max_value=tightening_torque - 0.1,  # Must be less than tightening
                value=min(default_removal, tightening_torque - 0.1),
                step=0.1,
                format="%.1f"
            )
            
            # Calculate button
            calculate_pressed = st.button("Calculate Preload", type="primary", use_container_width=True)
        
        with col2:
            st.subheader("Results")
            
            if calculate_pressed or st.session_state.get('last_calculation') == 'preload':
                # Store calculation type
                st.session_state.last_calculation = 'preload'
                
                # Calculate preload
                preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
                
                # Calculate additional information
                self_loosening = calculate_self_loosening(tightening_torque, removal_torque)
                primary_locking = calculate_primary_locking(tightening_torque, removal_torque)
                
                # Uncertainty range (9% as per the paper)
                uncertainty_percent = 9
                min_preload = preload * (1 - uncertainty_percent/100)
                max_preload = preload * (1 + uncertainty_percent/100)
                
                # Display the main result with large font
                st.markdown(f"""
                <div style="background-color: #ffffff; color: #333333; padding: 2rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center;">
                    <h3 style="color: #2c3e50; margin-bottom: 15px;">Calculated Preload</h3>
                    <p style="font-size: 2.5rem; font-weight: bold; color: #2c3e50;">
                        {preload:.2f} N
                    </p>
                    <p style="color: #333333;">Uncertainty Range (±{uncertainty_percent}%):<br>
                    {min_preload:.2f} N to {max_preload:.2f} N</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Additional metrics
                st.markdown("""
                <h4>Component Analysis</h4>
                """, unsafe_allow_html=True)
                
                # Create columns for metrics
                m1, m2 = st.columns(2)
                with m1:
                    st.metric(
                        label="Self-Loosening Component",
                        value=f"{self_loosening:.2f} N-cm",
                        help="The inherent self-loosening torque due to screw geometry"
                    )
                
                with m2:
                    st.metric(
                        label="Primary Locking Component",
                        value=f"{primary_locking:.2f} N-cm",
                        help="The torque component that resists loosening due to friction"
                    )
                
                # Create gauge chart for preload
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=preload,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Preload (N)"},
                    gauge={
                        'axis': {'range': [0, max(1200, max_preload * 1.2)]},
                        'bar': {'color': "#1f77b4"},
                        'steps': [
                            {'range': [0, min_preload], 'color': "#f8d7da"},
                            {'range': [min_preload, max_preload], 'color': "#d1e7dd"},
                            {'range': [max_preload, max(1200, max_preload * 1.2)], 'color': "#f8d7da"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': preload
                        }
                    }
                ))
                
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                # Formula details
                with st.expander("See Calculation Details"):
                    st.markdown(f"""
                    <h4>Formula Application:</h4>
                    <p>P = (T<sub>t</sub> - T<sub>r</sub>) × π / p</p>
                    <p>P = ({tightening_torque} - {removal_torque}) × π / {thread_pitch}</p>
                    <p>P = {tightening_torque - removal_torque} × {math.pi:.4f} / {thread_pitch}</p>
                    <p>P = {((tightening_torque - removal_torque) * math.pi):.4f} / {thread_pitch}</p>
                    <p>P = {preload:.2f} N</p>
                    """, unsafe_allow_html=True)
                
                # Store results in session state for reporting
                st.session_state.calculation_results['preload'] = {
                    'tightening_torque': tightening_torque,
                    'removal_torque': removal_torque,
                    'thread_pitch': thread_pitch,
                    'preload': preload,
                    'min_preload': min_preload, 
                    'max_preload': max_preload,
                    'self_loosening': self_loosening,
                    'primary_locking': primary_locking,
                    'uncertainty_percent': uncertainty_percent,
                }
                
                if input_method == "Select from Implant System Database":
                    st.session_state.calculation_results['preload']['system'] = selected_system
                    st.session_state.calculation_results['preload']['model'] = selected_model 