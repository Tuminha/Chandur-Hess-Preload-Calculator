#!/usr/bin/env python3
"""
Tests for implant systems calculations.

These tests validate the preload and torque calculations using data from
various dental implant systems defined in sample_systems.json.
"""

import unittest
import sys
import os
import json
import math
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import the modules to be tested
from src.core.preload import (
    calculate_preload,
    calculate_final_torque,
    estimate_uncertainty
)
from src.core.torque import (
    estimate_preload_from_torque,
    calculate_stress_from_preload,
    calculate_safety_factor,
    calculate_tensile_area,
    assess_risk
)


class TestImplantSystems(unittest.TestCase):
    """Test case for implant system calculations using real-world data."""

    def setUp(self):
        """Set up test fixtures."""
        # Load implant systems data
        data_path = Path(__file__).parent.parent / "data" / "implant_systems" / "sample_systems.json"
        
        with open(data_path, 'r') as f:
            self.implant_data = json.load(f)
        
        # Common test values for comparative calculations
        self.removal_torque_factor = 0.85  # Assume removal torque is 85% of tightening torque
        self.desired_preload_factor = 1.2  # Desired preload 20% higher than calculated preload
        
    def test_load_implant_data(self):
        """Test that implant data was loaded correctly."""
        self.assertIsNotNone(self.implant_data)
        self.assertIn("implant_systems", self.implant_data)
        
        # Verify we have data for major implant systems
        systems = self.implant_data["implant_systems"]
        self.assertIn("Nobel_Biocare", systems)
        self.assertIn("Straumann", systems)
        self.assertIn("Dentsply_Astra", systems)
        self.assertIn("Camlog", systems)
    
    def test_conventional_preload_estimation(self):
        """Test conventional preload estimation for different implant systems."""
        for system_name, system_data in self.implant_data["implant_systems"].items():
            for model_name, model_data in system_data.items():
                # Get screw data
                screw_data = model_data["screws"]["standard"]
                
                # Get parameters
                torque = screw_data["recommended_torque"]  # N-cm
                diameter = screw_data["diameter"] / 10  # mm to cm
                k_factor = screw_data["K_factor"]
                
                # Calculate estimated preload using conventional method
                estimated_preload = estimate_preload_from_torque(torque, diameter, k_factor)
                
                # Check that result is positive and reasonable
                self.assertGreater(estimated_preload, 0)
                
                # For typical dental implants, preload should generally be 200-1000 N
                self.assertGreaterEqual(estimated_preload, 200)
                self.assertLessEqual(estimated_preload, 1500)
                
                # Print for informational purposes
                print(f"{system_name} {model_name}: {estimated_preload:.2f} N")
    
    def test_wadhwani_hess_preload_calculation(self):
        """Test Wadhwani-Hess preload calculation for different implant systems."""
        for system_name, system_data in self.implant_data["implant_systems"].items():
            for model_name, model_data in system_data.items():
                # Get screw data
                screw_data = model_data["screws"]["standard"]
                
                # Get parameters
                tightening_torque = screw_data["recommended_torque"]  # N-cm
                removal_torque = tightening_torque * self.removal_torque_factor
                thread_pitch = screw_data["thread_pitch"] / 10  # mm to cm
                
                # Calculate preload using Wadhwani-Hess method
                calculated_preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
                
                # Check that result is positive and reasonable
                self.assertGreater(calculated_preload, 0)
                
                # For typical dental implants, preload should generally be 200-1000 N
                self.assertGreaterEqual(calculated_preload, 200)
                self.assertLessEqual(calculated_preload, 1500)
                
                # Print for informational purposes
                print(f"{system_name} {model_name} (W-H): {calculated_preload:.2f} N")
    
    def test_final_torque_calculation(self):
        """Test final torque calculation for desired preload for different implant systems."""
        for system_name, system_data in self.implant_data["implant_systems"].items():
            for model_name, model_data in system_data.items():
                # Get screw data
                screw_data = model_data["screws"]["standard"]
                
                # Get parameters
                initial_torque = screw_data["recommended_torque"]  # N-cm
                removal_torque = initial_torque * self.removal_torque_factor
                thread_pitch = screw_data["thread_pitch"] / 10  # mm to cm
                
                # First calculate initial preload using Wadhwani-Hess method
                initial_preload = calculate_preload(initial_torque, removal_torque, thread_pitch)
                
                # Now calculate desired preload (20% higher)
                desired_preload = initial_preload * self.desired_preload_factor
                
                # Calculate final torque needed for desired preload
                final_torque = calculate_final_torque(
                    initial_torque, 
                    removal_torque, 
                    initial_preload, 
                    desired_preload, 
                    thread_pitch
                )
                
                # Check that result is positive and reasonable
                self.assertGreater(final_torque, 0)
                
                # Final torque should be higher than initial torque by approximately the same factor
                expected_torque_ratio = desired_preload / initial_preload
                actual_torque_ratio = final_torque / initial_torque
                
                self.assertAlmostEqual(actual_torque_ratio, expected_torque_ratio, delta=0.01)
                
                # Print for informational purposes
                print(f"{system_name} {model_name} final torque: {final_torque:.2f} N-cm for {desired_preload:.2f} N preload")
    
    def test_stress_calculation(self):
        """Test stress calculation for different implant systems."""
        for system_name, system_data in self.implant_data["implant_systems"].items():
            for model_name, model_data in system_data.items():
                # Get screw data
                screw_data = model_data["screws"]["standard"]
                
                # Get parameters
                torque = screw_data["recommended_torque"]  # N-cm
                diameter = screw_data["diameter"]  # mm
                thread_pitch = screw_data["thread_pitch"]  # mm
                k_factor = screw_data["K_factor"]
                yield_strength = screw_data["yield_strength"]  # MPa
                
                # Calculate tensile area
                tensile_area = calculate_tensile_area(diameter, thread_pitch)
                
                # Calculate estimated preload using conventional method
                preload = estimate_preload_from_torque(torque, diameter/10, k_factor)
                
                # Calculate stress
                stress = calculate_stress_from_preload(preload, tensile_area)
                
                # Calculate safety factor
                safety_factor = calculate_safety_factor(stress, yield_strength)
                
                # Check that results are reasonable
                self.assertGreater(stress, 0)
                self.assertGreater(safety_factor, 0)
                
                # For dental implants, stress should generally be below yield strength
                self.assertLessEqual(stress, yield_strength)
                
                # Safety factor should ideally be above 1.5
                recommended_safety_factor = 1.5
                risk_level, recommendation = assess_risk(safety_factor, recommended_safety_factor)
                
                # Print for informational purposes
                print(f"{system_name} {model_name}: Stress = {stress:.2f} MPa, Safety Factor = {safety_factor:.2f}, Risk = {risk_level}")
    
    def test_compare_preload_methods(self):
        """Compare conventional and Wadhwani-Hess preload calculation methods."""
        for system_name, system_data in self.implant_data["implant_systems"].items():
            for model_name, model_data in system_data.items():
                # Get screw data
                screw_data = model_data["screws"]["standard"]
                
                # Get parameters
                torque = screw_data["recommended_torque"]  # N-cm
                diameter = screw_data["diameter"] / 10  # mm to cm
                k_factor = screw_data["K_factor"]
                removal_torque = torque * self.removal_torque_factor
                thread_pitch = screw_data["thread_pitch"] / 10  # mm to cm
                
                # Calculate preload using conventional method
                conventional_preload = estimate_preload_from_torque(torque, diameter, k_factor)
                
                # Calculate preload using Wadhwani-Hess method
                wh_preload = calculate_preload(torque, removal_torque, thread_pitch)
                
                # Get uncertainty percentages for both methods
                conventional_uncertainty, _ = estimate_uncertainty(torque, False)
                wh_uncertainty = 9  # 9% as per the paper
                
                # Calculate uncertainty ranges
                conv_min = conventional_preload * (1 - conventional_uncertainty/100)
                conv_max = conventional_preload * (1 + conventional_uncertainty/100)
                wh_min = wh_preload * (1 - wh_uncertainty/100)
                wh_max = wh_preload * (1 + wh_uncertainty/100)
                
                # Print for informational purposes
                print(f"{system_name} {model_name}:")
                print(f"  Conventional: {conventional_preload:.2f} N (±{conventional_uncertainty}%)")
                print(f"  Wadhwani-Hess: {wh_preload:.2f} N (±{wh_uncertainty}%)")
                
                # Check if Wadhwani-Hess result is within the conventional range
                in_conventional_range = conv_min <= wh_preload <= conv_max
                print(f"  W-H result within conventional range: {in_conventional_range}")
                
                # The W-H range should be narrower than the conventional range
                wh_range = wh_max - wh_min
                conv_range = conv_max - conv_min
                print(f"  Range reduction: {100 * (1 - wh_range/conv_range):.1f}%")
                print()
                
                # W-H uncertainty should be lower than conventional
                self.assertLess(wh_uncertainty, conventional_uncertainty)


if __name__ == "__main__":
    unittest.main() 