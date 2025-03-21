#!/usr/bin/env python3
"""
Welcome Page for the Preload Calculator App

This component displays the welcome screen with an introduction to the
Wadhwani-Hess method and its benefits.
"""

import streamlit as st
from pathlib import Path


def show_welcome():
    """Display the welcome screen with introduction to the app."""
    st.markdown('<h1 class="main-header">Dental Implant Preload Calculator</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">Based on the Wadhwani-Hess Method</h2>', unsafe_allow_html=True)
    
    # Main columns for content
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Introduction section - completely rewritten
        st.subheader("Welcome to the Dental Implant Preload Calculator")
        
        st.info("""
        This application implements the novel approach developed by Wadhwani and Hess
        for more accurate calculation of preload in dental implant screws.
        """)
        
        # Introduction box
        st.markdown("""
        <div style="background-color: #1e2a38; color: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            <h4 style="color: white; margin-bottom: 10px; font-weight: 500;">The Wadhwani-Hess Method</h4>
            <p style="font-size: 1.05rem; line-height: 1.6; margin: 0;">
                Introduces a revolutionary way to determine preload by using both 
                <span style="font-weight: bold">tightening torque</span> and 
                <span style="font-weight: bold">removal torque</span> measurements, 
                significantly reducing uncertainty compared to conventional methods.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #ffffff; color: #333333; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #2c3e50; margin-bottom: 15px;">Key Benefits</h3>
            <ul style="font-size: 1.05rem; line-height: 1.7; color: #333333;">
                <li><span style="color: #2980b9; font-weight: bold;">Improved Accuracy:</span> Reduces uncertainty from ±35% to ±9%</li>
                <li><span style="color: #2980b9; font-weight: bold;">Individual Joint Assessment:</span> Provides joint-specific calculations</li>
                <li><span style="color: #2980b9; font-weight: bold;">Accounts for Variations:</span> Considers thread interface conditions</li>
                <li><span style="color: #2980b9; font-weight: bold;">Clinical Relevance:</span> Directly applicable to everyday practice</li>
                <li><span style="color: #2980b9; font-weight: bold;">Risk Assessment:</span> Evaluate safety factors and potential risks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #ffffff; color: #333333; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #2c3e50; margin-bottom: 15px;">Scientific Foundation</h3>
            <p style="font-size: 1.05rem; line-height: 1.5; color: #333333;">Based on the paper:<br>
            <i>"A Novel Approach to Achieve Preload in Dental Implant Systems"</i><br>
            by Chandur Wadhwani and Tom Hess</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.image("https://img.icons8.com/color/240/000000/dental-implant.png", width=200)
        
        st.markdown("""
        <div style="background-color: #ffffff; color: #333333; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #2c3e50; margin-bottom: 15px;">Getting Started</h3>
            <p style="font-size: 1.05rem; margin-bottom: 10px; color: #333333;">Use the sidebar navigation to explore different features:</p>
            <ul style="font-size: 1.05rem; line-height: 1.5; color: #333333;">
                <li>Calculate preload from measured torque values</li>
                <li>Determine required torque for desired preload</li>
                <li>Compare different calculation methods</li>
                <li>Analyze various implant systems</li>
                <li>Generate detailed reports</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Equations section
    st.subheader("Core Scientific Formulas")
    
    eq_col1, eq_col2 = st.columns(2)
    
    with eq_col1:
        st.markdown("""
        <div style="background-color: #ffffff; color: #333333; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">Equation 3: Preload Calculation</h4>
            <p style="font-size: 1.2rem; text-align: center; background-color: #f1f8ff; padding: 10px; border-radius: 5px; font-weight: bold; color: #2c3e50;">
                P = (T<sub>t</sub> - T<sub>r</sub>) × π / p
            </p>
            <p style="line-height: 1.6; margin-top: 15px; color: #333333;"><strong>Where:</strong><br>
            P: Preload (N)<br>
            T<sub>t</sub>: Tightening torque (N-cm)<br>
            T<sub>r</sub>: Removal torque (N-cm)<br>
            p: Thread pitch (cm)<br>
            π: Pi (3.14159...)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with eq_col2:
        st.markdown("""
        <div style="background-color: #ffffff; color: #333333; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">Equation 6: Final Tightening Torque</h4>
            <p style="font-size: 1.2rem; text-align: center; background-color: #f1f8ff; padding: 10px; border-radius: 5px; font-weight: bold; color: #2c3e50;">
                T<sub>i</sub> = (p × T<sub>t initial</sub> × P<sub>desired</sub>) / (π × (T<sub>t initial</sub> - T<sub>r</sub>))
            </p>
            <p style="line-height: 1.6; margin-top: 15px; color: #333333;"><strong>Where:</strong><br>
            T<sub>i</sub>: Final tightening torque (N-cm)<br>
            P<sub>desired</sub>: Desired preload (N)<br>
            T<sub>t initial</sub>: Initial tightening torque (N-cm)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 1.5rem; background-color: #e8f4f8; border-radius: 8px;">
        <h3 style="color: #2c3e50; margin-bottom: 15px;">Ready to calculate more accurate preload values?</h3>
        <p style="font-size: 1.1rem; color: #333333;">Navigate to the Preload Calculator in the sidebar to start using the Wadhwani-Hess method!</p>
    </div>
    """, unsafe_allow_html=True) 