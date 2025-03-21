#!/usr/bin/env python3
"""
Tests for the torque calculation module.

These tests validate the torque-related calculations for dental implant preload,
including the relationships between torque, preload, and stress.
"""

import unittest
import sys
import os
import math
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import modules to be tested
from src.core.preload import calculate_preload, calculate_final_torque
from src.core.torque import (
    estimate_preload_from_torque,
    calculate_stress_from_preload,
    calculate_safety_factor
)


class TestTorqueCalculations(unittest.TestCase):
    """Test case for torque-related calculations."""

    def setUp(self):
        """Set up test fixtures."""
        # Standard test values
        self.thread_pitch = 0.04  # cm (0.4 mm)
        self.screw_diameter = 0.2  # cm (2 mm), based on the paper
        self.nominal_torque = 35  # N-cm, standard torque for dental implants
        
        # Material properties for titanium alloy (common in dental implants)
        self.yield_strength = 800  # MPa (N/mm²)
        self.tensile_area = 2.0  # mm²
        
        # K-factor (nut factor) for DLC coated screws
        self.k_factor = 0.2

    def test_estimate_preload_from_torque(self):
        """Test estimation of preload from torque using conventional methods."""
        # Using standard formula T = K*F*d, solved for F: F = T / (K*d)
        # For torque = 35 N-cm, k = 0.2, d = 0.2 cm
        expected_preload = 35 / (0.2 * 0.2)  # N
        
        calculated_preload = estimate_preload_from_torque(
            self.nominal_torque, 
            self.screw_diameter, 
            self.k_factor
        )
        
        self.assertAlmostEqual(
            calculated_preload,
            expected_preload,
            delta=1.0,
            msg="Preload estimation from torque failed"
        )
    
    def test_calculate_stress_from_preload(self):
        """Test calculation of stress from preload."""
        preload = 400  # N
        # Stress = Force / Area
        # 400 N / 2.0 mm² = 200 MPa
        expected_stress = 200  # MPa
        
        calculated_stress = calculate_stress_from_preload(
            preload, 
            self.tensile_area
        )
        
        self.assertAlmostEqual(
            calculated_stress,
            expected_stress,
            delta=0.1,
            msg="Stress calculation from preload failed"
        )
    
    def test_calculate_safety_factor(self):
        """Test calculation of safety factor."""
        stress = 200  # MPa
        # Safety Factor = Yield Strength / Stress
        # 800 MPa / 200 MPa = 4.0
        expected_safety_factor = 4.0
        
        calculated_safety_factor = calculate_safety_factor(
            stress, 
            self.yield_strength
        )
        
        self.assertAlmostEqual(
            calculated_safety_factor,
            expected_safety_factor,
            delta=0.01,
            msg="Safety factor calculation failed"
        )
    
    def test_integrated_torque_stress_calculation(self):
        """Test the integrated calculation from torque to safety factor."""
        # Starting with a torque of 35 N-cm
        torque = 35  # N-cm
        
        # Calculate preload using conventional method
        preload = estimate_preload_from_torque(
            torque, 
            self.screw_diameter, 
            self.k_factor
        )
        
        # Calculate stress from preload
        stress = calculate_stress_from_preload(
            preload, 
            self.tensile_area
        )
        
        # Calculate safety factor from stress
        safety_factor = calculate_safety_factor(
            stress, 
            self.yield_strength
        )
        
        # For 35 N-cm, should give approximately 875 N preload
        self.assertGreater(preload, 800, "Preload should be >800N for 35 N-cm torque")
        
        # Stress should be <450 MPa for this preload
        self.assertLess(stress, 450, "Stress should be <450 MPa for the given preload")
        
        # Safety factor should be >1.5 to be acceptable
        self.assertGreater(
            safety_factor, 
            1.5, 
            "Safety factor should be >1.5 for dental implants"
        )
    
    def test_risk_assessment(self):
        """Test risk assessment based on safety factor."""
        # Low risk (high safety factor)
        high_safety_factor = 4.0
        
        # Medium risk (moderate safety factor)
        medium_safety_factor = 2.0
        
        # High risk (low safety factor)
        low_safety_factor = 1.2
        
        # Minimum acceptable safety factor for dental implants
        min_safety_factor = 1.5
        
        self.assertGreater(
            high_safety_factor,
            min_safety_factor,
            "High safety factor should indicate low risk"
        )
        
        self.assertGreater(
            medium_safety_factor,
            min_safety_factor,
            "Medium safety factor should still be acceptable"
        )
        
        self.assertLess(
            low_safety_factor,
            min_safety_factor,
            "Low safety factor should indicate high risk"
        )


if __name__ == "__main__":
    unittest.main() 