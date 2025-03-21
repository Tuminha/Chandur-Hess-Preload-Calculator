#!/usr/bin/env python3
"""
Preload Calculator - Streamlit Application

This Streamlit app implements the Wadhwani-Hess method for calculating
dental implant preload with improved accuracy.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import json
import math
import io
import base64
from pathlib import Path
from datetime import datetime

# Import components
from components.welcome import show_welcome
from components.preload_calculator import show_preload_calculator
from components.final_torque_calculator import show_final_torque_calculator
from components.compare_methods import show_compare_methods
from components.implant_systems_analysis import show_implant_systems_analysis
from components.generate_report import generate_pdf_report

# Import core calculation modules
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.core.preload import (
    calculate_preload,
    calculate_final_torque,
    calculate_self_loosening,
    calculate_primary_locking,
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

# Set page configuration
st.set_page_config(
    page_title="Dental Implant Preload Calculator",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.5rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        border-radius: 5px;
        padding: 1.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        color: #7f8c8d;
        font-size: 0.8rem;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to load implant systems data
# Temporarily removing cache decorator for testing
# @st.cache_data
def load_implant_data():
    """Load implant systems data from JSON file."""
    # Try to load the enhanced database first, fall back to sample database if not available
    enhanced_path = Path(__file__).parent.parent / "data" / "implant_systems" / "enhanced_systems.json"
    sample_path = Path(__file__).parent.parent / "data" / "implant_systems" / "sample_systems.json"
    
    print(f"Enhanced path exists: {enhanced_path.exists()}")
    print(f"Sample path exists: {sample_path.exists()}")
    
    try:
        if enhanced_path.exists():
            print("Loading enhanced database")
            with open(enhanced_path, 'r') as f:
                data = json.load(f)
                print(f"Enhanced systems: {list(data['implant_systems'].keys())}")
                return data
        else:
            print("Loading sample database")
            with open(sample_path, 'r') as f:
                data = json.load(f)
                print(f"Sample systems: {list(data['implant_systems'].keys())}")
                return data
    except Exception as e:
        st.error(f"Error loading implant data: {e}")
        print(f"Error loading implant data: {e}")
        # Return a minimal dataset if loading fails
        return {
            "metadata": {"version": "1.0.0"},
            "implant_systems": {
                "Generic": {
                    "Standard": {
                        "connection_type": "Generic",
                        "screws": {
                            "standard": {
                                "diameter": 2.0,
                                "thread_pitch": 0.4,
                                "material": "Titanium Alloy",
                                "yield_strength": 950,
                                "K_factor": 0.2,
                                "recommended_torque": 35
                            }
                        }
                    }
                }
            }
        }

# Initialize session state
if 'implant_data' not in st.session_state:
    st.session_state.implant_data = load_implant_data()

if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

if 'calculation_results' not in st.session_state:
    st.session_state.calculation_results = {}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Sidebar authentication and navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dental-implant.png", width=80)
    st.title("Navigation")
    
    # Authentication section
    if not st.session_state.authenticated:
        st.subheader("Authentication Required")
        password = st.text_input("Enter access password", type="password")
        if st.button("Login"):
            if password == "chandur2025":
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect password")
    
    # Only show navigation if authenticated
    if st.session_state.authenticated:
        nav_options = [
            {"name": "Welcome", "icon": "👋", "id": "welcome"},
            {"name": "Preload Calculator", "icon": "🔢", "id": "preload_calculator"},
            {"name": "Final Torque Calculator", "icon": "🔧", "id": "final_torque_calculator"},
            {"name": "Compare Methods", "icon": "📊", "id": "compare_methods"},
            {"name": "Implant Systems Analysis", "icon": "🔍", "id": "implant_systems_analysis"}
        ]
        
        for option in nav_options:
            if st.sidebar.button(f"{option['icon']} {option['name']}", key=f"nav_{option['id']}"):
                st.session_state.page = option['id']
        
        st.sidebar.divider()
        
        if st.sidebar.button("📄 Generate PDF Report", disabled=not st.session_state.calculation_results):
            pdf_bytes = generate_pdf_report(st.session_state.calculation_results)
            st.sidebar.download_button(
                label="⬇️ Download Report",
                data=pdf_bytes,
                file_name=f"preload_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
        
        # Add logout option
        if st.sidebar.button("🔒 Logout"):
            st.session_state.authenticated = False
            st.rerun()

# Main content based on selected page and authentication
if st.session_state.authenticated:
    if st.session_state.page == 'welcome':
        show_welcome()
    elif st.session_state.page == 'preload_calculator':
        show_preload_calculator()
    elif st.session_state.page == 'final_torque_calculator':
        show_final_torque_calculator()
    elif st.session_state.page == 'compare_methods':
        show_compare_methods()
    elif st.session_state.page == 'implant_systems_analysis':
        show_implant_systems_analysis()
else:
    st.markdown("""
    <div style="text-align: center; margin-top: 100px;">
        <h1>Chandur-Hess Preload Calculator</h1>
        <p style="font-size: 1.2rem;">Please enter the password in the sidebar to access this application.</p>
        <p style="font-size: 0.9rem; color: #666;">This application contains proprietary calculations based on research by Chandur Wadhwani and Tom Hess.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer only shows when authenticated
if st.session_state.authenticated:
    st.markdown("""
    <div class="footer">
        <p>Developed based on research by Chandur Wadhwani and Tom Hess | © 2025 Preload Measurement MVP</p>
    </div>
    """, unsafe_allow_html=True) 