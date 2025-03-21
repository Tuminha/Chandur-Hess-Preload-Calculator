#!/usr/bin/env python3
"""
Tests for the preload calculation module.

These tests validate the implementation of the Wadhwani-Hess theoretical model
for dental implant preload calculations.
"""

import unittest
import sys
import os
import math
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import the preload calculation module (will be created)
from src.core.preload import (
    calculate_preload,
    calculate_final_torque,
    calculate_self_loosening,
    calculate_primary_locking,
    estimate_uncertainty,
    calculate_preload_range
)


class TestPreloadCalculations(unittest.TestCase):
    """Test case for preload calculations based on the Wadhwani-Hess model."""

    def setUp(self):
        """Set up test fixtures."""
        # Data from Table 1 in the paper for specimen #1
        self.specimen1_data = [
            {"tightening_torque": 35, "preload_measured": 466, "removal_torque": 28.9, "preload_calculated": 479, "error_percent": 2.8},
            {"tightening_torque": 35, "preload_measured": 450, "removal_torque": 28.8, "preload_calculated": 487, "error_percent": 8.2},
            {"tightening_torque": 35, "preload_measured": 433, "removal_torque": 29.2, "preload_calculated": 456, "error_percent": 5.2},
            {"tightening_torque": 35, "preload_measured": 422, "removal_torque": 29.8, "preload_calculated": 408, "error_percent": -3.2},
            {"tightening_torque": 35, "preload_measured": 419, "removal_torque": 29.7, "preload_calculated": 416, "error_percent": -0.7},
            {"tightening_torque": 35, "preload_measured": 411, "removal_torque": 29.3, "preload_calculated": 448, "error_percent": 8.9},
            {"tightening_torque": 35, "preload_measured": 405, "removal_torque": 29.9, "preload_calculated": 401, "error_percent": -1.1},
            {"tightening_torque": 35, "preload_measured": 407, "removal_torque": 29.5, "preload_calculated": 432, "error_percent": 6.1},
            {"tightening_torque": 35, "preload_measured": 398, "removal_torque": 30.3, "preload_calculated": 369, "error_percent": -7.3},
            {"tightening_torque": 35, "preload_measured": 390, "removal_torque": 30.4, "preload_calculated": 361, "error_percent": -7.4}
        ]
        
        # Data from Table 2 in the paper for specimen #2
        self.specimen2_data = [
            {"tightening_torque": 35, "preload_measured": 440, "removal_torque": 29.0, "preload_calculated": 471, "error_percent": 7.1},
            {"tightening_torque": 35, "preload_measured": 436, "removal_torque": 29.4, "preload_calculated": 440, "error_percent": 0.9},
            {"tightening_torque": 35, "preload_measured": 434, "removal_torque": 29.2, "preload_calculated": 456, "error_percent": 5.0},
            {"tightening_torque": 35, "preload_measured": 424, "removal_torque": 29.1, "preload_calculated": 463, "error_percent": 9.3},
            {"tightening_torque": 35, "preload_measured": 415, "removal_torque": 29.6, "preload_calculated": 424, "error_percent": 2.2},
            {"tightening_torque": 35, "preload_measured": 405, "removal_torque": 29.5, "preload_calculated": 432, "error_percent": 6.7},
            {"tightening_torque": 35, "preload_measured": 403, "removal_torque": 30.0, "preload_calculated": 393, "error_percent": -2.6},
            {"tightening_torque": 35, "preload_measured": 398, "removal_torque": 30.1, "preload_calculated": 385, "error_percent": -3.3},
            {"tightening_torque": 35, "preload_measured": 394, "removal_torque": 29.8, "preload_calculated": 408, "error_percent": 3.7},
            {"tightening_torque": 35, "preload_measured": 362, "removal_torque": 30.3, "preload_calculated": 369, "error_percent": 2.0}
        ]
        
        # Thread pitch from the paper (p = 0.4 mm = 0.04 cm)
        self.thread_pitch = 0.04  # cm
        
        # Example from page 11
        self.example_desired_preload = 400  # N
        self.example_initial_torque = 25  # N-cm
        self.example_removal_torque = 21.4  # N-cm
        self.example_final_torque = 35.4  # N-cm
        
        # Additional test scenarios for edge cases
        self.edge_cases = [
            # Very small thread pitch (0.01 cm)
            {"tightening_torque": 35, "removal_torque": 30, "thread_pitch": 0.01, "expected_preload": 1570.8},
            # Large thread pitch (0.1 cm)
            {"tightening_torque": 35, "removal_torque": 30, "thread_pitch": 0.1, "expected_preload": 157.08},
            # Small torque difference (0.5 N-cm)
            {"tightening_torque": 30, "removal_torque": 29.5, "thread_pitch": 0.04, "expected_preload": 39.27},
            # Large torque difference (20 N-cm)
            {"tightening_torque": 50, "removal_torque": 30, "thread_pitch": 0.04, "expected_preload": 1570.8}
        ]
        
        # Different materials with varied thread pitches and torques
        self.different_materials = [
            # Stainless steel (thread pitch 0.05 cm)
            {"tightening_torque": 40, "removal_torque": 32, "thread_pitch": 0.05, "expected_preload": 502.65},
            # Titanium Grade 5 (thread pitch 0.035 cm)
            {"tightening_torque": 30, "removal_torque": 24, "thread_pitch": 0.035, "expected_preload": 538.56},
            # Gold alloy (thread pitch 0.03 cm)
            {"tightening_torque": 20, "removal_torque": 15, "thread_pitch": 0.03, "expected_preload": 523.6}
        ]

    def test_calculate_preload(self):
        """Test preload calculation formula from Eq 3."""
        for data_point in self.specimen1_data:
            tightening_torque = data_point["tightening_torque"]
            removal_torque = data_point["removal_torque"]
            expected_preload = data_point["preload_calculated"]
            
            calculated_preload = calculate_preload(tightening_torque, removal_torque, self.thread_pitch)
            
            # Allow for a small margin of error due to rounding in the paper
            self.assertAlmostEqual(
                calculated_preload, 
                expected_preload, 
                delta=2.0,  # Allow variance of up to 2N
                msg=f"Preload calculation failed for tightening_torque={tightening_torque}, "
                    f"removal_torque={removal_torque}, thread_pitch={self.thread_pitch}"
            )
    
    def test_calculate_preload_specimen2(self):
        """Test preload calculation using data from specimen #2."""
        for data_point in self.specimen2_data:
            tightening_torque = data_point["tightening_torque"]
            removal_torque = data_point["removal_torque"]
            expected_preload = data_point["preload_calculated"]
            
            calculated_preload = calculate_preload(tightening_torque, removal_torque, self.thread_pitch)
            
            self.assertAlmostEqual(
                calculated_preload, 
                expected_preload, 
                delta=2.0,
                msg=f"Preload calculation failed for specimen #2: tightening_torque={tightening_torque}, "
                    f"removal_torque={removal_torque}"
            )
    
    def test_calculate_preload_edge_cases(self):
        """Test preload calculation with edge cases."""
        for case in self.edge_cases:
            tightening_torque = case["tightening_torque"]
            removal_torque = case["removal_torque"]
            thread_pitch = case["thread_pitch"]
            expected_preload = case["expected_preload"]
            
            calculated_preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
            
            self.assertAlmostEqual(
                calculated_preload, 
                expected_preload, 
                delta=0.1,  # Tighter tolerance for computed values
                msg=f"Preload calculation failed for edge case: tightening_torque={tightening_torque}, "
                    f"removal_torque={removal_torque}, thread_pitch={thread_pitch}"
            )
    
    def test_calculate_preload_different_materials(self):
        """Test preload calculation with different materials."""
        for material in self.different_materials:
            tightening_torque = material["tightening_torque"]
            removal_torque = material["removal_torque"]
            thread_pitch = material["thread_pitch"]
            expected_preload = material["expected_preload"]
            
            calculated_preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
            
            self.assertAlmostEqual(
                calculated_preload, 
                expected_preload, 
                delta=0.1,  # Tighter tolerance for computed values
                msg=f"Preload calculation failed for material: tightening_torque={tightening_torque}, "
                    f"removal_torque={removal_torque}, thread_pitch={thread_pitch}"
            )
    
    def test_calculate_preload_invalid_input(self):
        """Test preload calculation with invalid inputs."""
        # Test with zero thread pitch
        with self.assertRaises(ValueError):
            calculate_preload(35, 30, 0)
        
        # Test with negative thread pitch
        with self.assertRaises(ValueError):
            calculate_preload(35, 30, -0.01)
    
    def test_calculate_final_torque(self):
        """Test the final torque calculation formula from Eq 6."""
        # Test using the example from page 11
        initial_preload = calculate_preload(
            self.example_initial_torque, 
            self.example_removal_torque, 
            self.thread_pitch
        )
        
        final_torque = calculate_final_torque(
            self.example_initial_torque,
            self.example_removal_torque,
            initial_preload,
            self.example_desired_preload,
            self.thread_pitch
        )
        
        self.assertAlmostEqual(
            final_torque, 
            self.example_final_torque, 
            delta=0.1,  # Allow variance of up to 0.1 N-cm
            msg=f"Final torque calculation failed for example from paper"
        )
    
    def test_calculate_final_torque_additional_cases(self):
        """Test the final torque calculation with additional cases."""
        # Define additional cases with expected results
        cases = [
            # Low torque case
            {"initial_torque": 10, "removal_torque": 8, "initial_preload": 157.1, "desired_preload": 200, "thread_pitch": 0.04, "expected_torque": 12.73},
            # High torque case
            {"initial_torque": 50, "removal_torque": 40, "initial_preload": 785.4, "desired_preload": 1000, "thread_pitch": 0.04, "expected_torque": 63.66},
            # Different pitch case
            {"initial_torque": 30, "removal_torque": 25, "initial_preload": 314.2, "desired_preload": 400, "thread_pitch": 0.05, "expected_torque": 38.19}
        ]
        
        for case in cases:
            final_torque = calculate_final_torque(
                case["initial_torque"],
                case["removal_torque"],
                case["initial_preload"],
                case["desired_preload"],
                case["thread_pitch"]
            )
            
            self.assertAlmostEqual(
                final_torque,
                case["expected_torque"],
                delta=0.1,
                msg=f"Final torque calculation failed for additional case"
            )
    
    def test_calculate_final_torque_invalid_input(self):
        """Test final torque calculation with invalid inputs."""
        # Test with zero thread pitch
        with self.assertRaises(ValueError):
            calculate_final_torque(25, 20, 200, 300, 0)
        
        # Test with negative thread pitch
        with self.assertRaises(ValueError):
            calculate_final_torque(25, 20, 200, 300, -0.01)
        
        # Test with initial torque less than removal torque
        with self.assertRaises(ValueError):
            calculate_final_torque(20, 25, 200, 300, 0.04)
        
        # Test with equal initial and removal torque
        with self.assertRaises(ValueError):
            calculate_final_torque(25, 25, 200, 300, 0.04)
    
    def test_calculate_self_loosening(self):
        """Test self-loosening calculation."""
        # Using first data point as an example
        tightening_torque = self.specimen1_data[0]["tightening_torque"]
        removal_torque = self.specimen1_data[0]["removal_torque"]
        
        self_loosening = calculate_self_loosening(tightening_torque, removal_torque)
        
        # The expected value is (Tt - Tr) / 2
        expected_self_loosening = (tightening_torque - removal_torque) / 2
        
        self.assertAlmostEqual(
            self_loosening, 
            expected_self_loosening, 
            delta=0.01,
            msg="Self-loosening calculation failed"
        )
    
    def test_calculate_self_loosening_multiple_cases(self):
        """Test self-loosening calculation with multiple cases."""
        test_cases = [
            {"tightening_torque": 40, "removal_torque": 30, "expected": 5.0},
            {"tightening_torque": 25, "removal_torque": 20, "expected": 2.5},
            {"tightening_torque": 60, "removal_torque": 45, "expected": 7.5}
        ]
        
        for case in test_cases:
            self_loosening = calculate_self_loosening(
                case["tightening_torque"], 
                case["removal_torque"]
            )
            
            self.assertAlmostEqual(
                self_loosening, 
                case["expected"], 
                delta=0.01,
                msg=f"Self-loosening calculation failed for case: {case}"
            )
    
    def test_calculate_primary_locking(self):
        """Test primary locking calculation."""
        # Using first data point as an example
        tightening_torque = self.specimen1_data[0]["tightening_torque"]
        removal_torque = self.specimen1_data[0]["removal_torque"]
        
        primary_locking = calculate_primary_locking(tightening_torque, removal_torque)
        
        # The expected value is (Tt + Tr) / 2
        expected_primary_locking = (tightening_torque + removal_torque) / 2
        
        self.assertAlmostEqual(
            primary_locking, 
            expected_primary_locking, 
            delta=0.01,
            msg="Primary locking calculation failed"
        )
    
    def test_calculate_primary_locking_multiple_cases(self):
        """Test primary locking calculation with multiple cases."""
        test_cases = [
            {"tightening_torque": 40, "removal_torque": 30, "expected": 35.0},
            {"tightening_torque": 25, "removal_torque": 20, "expected": 22.5},
            {"tightening_torque": 60, "removal_torque": 45, "expected": 52.5}
        ]
        
        for case in test_cases:
            primary_locking = calculate_primary_locking(
                case["tightening_torque"], 
                case["removal_torque"]
            )
            
            self.assertAlmostEqual(
                primary_locking, 
                case["expected"], 
                delta=0.01,
                msg=f"Primary locking calculation failed for case: {case}"
            )
    
    def test_preload_error_percentage(self):
        """Test error percentage between measured and calculated preload."""
        for data_point in self.specimen1_data:
            tightening_torque = data_point["tightening_torque"]
            removal_torque = data_point["removal_torque"]
            measured_preload = data_point["preload_measured"]
            expected_error = data_point["error_percent"]
            
            calculated_preload = calculate_preload(tightening_torque, removal_torque, self.thread_pitch)
            error_percent = 100 * (calculated_preload - measured_preload) / measured_preload
            
            self.assertAlmostEqual(
                error_percent, 
                expected_error, 
                delta=0.5,  # Allow a small error margin
                msg=f"Error percentage calculation failed for tightening_torque={tightening_torque}, "
                    f"removal_torque={removal_torque}"
            )
    
    def test_estimate_uncertainty(self):
        """Test uncertainty estimation for conventional method."""
        # Test unlubricated case
        uncertainty_percent, uncertainty_value = estimate_uncertainty(35, False)
        self.assertEqual(uncertainty_percent, 35)
        self.assertAlmostEqual(uncertainty_value, 12.25)
        
        # Test lubricated case
        uncertainty_percent, uncertainty_value = estimate_uncertainty(35, True)
        self.assertEqual(uncertainty_percent, 25)
        self.assertAlmostEqual(uncertainty_value, 8.75)
    
    def test_calculate_preload_range(self):
        """Test calculation of preload range based on uncertainty."""
        preload = 400
        uncertainty_percent = 35
        
        min_preload, max_preload = calculate_preload_range(preload, uncertainty_percent)
        
        self.assertAlmostEqual(min_preload, 260)
        self.assertAlmostEqual(max_preload, 540)
    
    def test_equivalence_of_final_torque_formulas(self):
        """
        Test that both ways of calculating final torque (exact Equation 6 and ratio method)
        yield equivalent results when using the Wadhwani-Hess preload formula.
        
        This confirms that the ratio method is mathematically equivalent to Equation 6.
        """
        # Create a test function that uses the ratio method
        def calculate_final_torque_ratio(
            initial_torque, removal_torque, initial_preload, desired_preload, thread_pitch
        ):
            return initial_torque * (desired_preload / initial_preload)
        
        # Create a test function that uses the exact Equation 6
        def calculate_final_torque_exact(
            initial_torque, removal_torque, initial_preload, desired_preload, thread_pitch
        ):
            torque_difference = initial_torque - removal_torque
            return (thread_pitch * initial_torque * desired_preload) / (math.pi * torque_difference)
        
        # Test cases
        test_cases = [
            {"initial_torque": 25, "removal_torque": 21.4, "thread_pitch": 0.04, 
             "initial_preload": 282.74, "desired_preload": 400},
            {"initial_torque": 40, "removal_torque": 32, "thread_pitch": 0.05, 
             "initial_preload": 502.65, "desired_preload": 600},
            {"initial_torque": 30, "removal_torque": 24, "thread_pitch": 0.035, 
             "initial_preload": 538.56, "desired_preload": 700}
        ]
        
        for case in test_cases:
            # Calculate preload using Wadhwani-Hess formula
            initial_preload = calculate_preload(
                case["initial_torque"], 
                case["removal_torque"], 
                case["thread_pitch"]
            )
            
            # Both calculations should match
            exact_result = calculate_final_torque_exact(
                case["initial_torque"],
                case["removal_torque"],
                initial_preload,
                case["desired_preload"],
                case["thread_pitch"]
            )
            
            ratio_result = calculate_final_torque_ratio(
                case["initial_torque"],
                case["removal_torque"],
                initial_preload,
                case["desired_preload"],
                case["thread_pitch"]
            )
            
            # They should yield the same result
            self.assertAlmostEqual(
                exact_result,
                ratio_result,
                delta=0.01,
                msg=f"Final torque calculation methods are not equivalent for case: {case}"
            )


if __name__ == "__main__":
    unittest.main() 