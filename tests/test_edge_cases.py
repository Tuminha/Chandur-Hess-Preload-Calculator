#!/usr/bin/env python3
"""
Edge case tests for dental implant preload calculations.

This test module focuses specifically on edge cases and boundary conditions
to ensure the robustness of the core calculation functions.
"""

import unittest
import sys
import os
import math
import numpy as np
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import calculation modules
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
    assess_risk,
    calculate_torque_range
)


class TestCalculationEdgeCases(unittest.TestCase):
    """Test edge cases for calculation functions."""

    def test_very_close_tightening_and_removal_torque(self):
        """
        Test with tightening and removal torque values that are very close.
        
        This simulates a situation where there is minimal difference between
        the tightening and removal torques, which could cause numerical
        instability in the preload calculation.
        """
        # Very small difference (0.001 N-cm)
        tightening_torque = 35.0
        removal_torque = 34.999  # Difference of 0.001 N-cm
        thread_pitch = 0.04
        
        # Calculate preload
        preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
        
        # The preload should be very small but positive
        self.assertGreater(preload, 0, "Preload should be positive for very small torque differences")
        self.assertLess(preload, 1, "Preload should be less than 1N for a 0.001 N-cm torque difference")
        
        # Test with tightening and removal torque values that are extremely close
        tightening_torque = 35.0
        removal_torque = 34.9999999  # Ultra small difference
        
        # Calculate preload
        preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
        
        # The preload should be calculated correctly despite the very small difference
        expected_preload = (tightening_torque - removal_torque) * math.pi / thread_pitch
        self.assertAlmostEqual(preload, expected_preload, places=10)
    
    def test_extremely_large_torque_values(self):
        """
        Test with extremely large torque values.
        
        This tests for potential overflow or precision issues with large numbers.
        """
        tightening_torque = 1_000_000  # 1 million N-cm
        removal_torque = 800_000  # 800,000 N-cm
        thread_pitch = 0.04
        
        # Calculate preload
        preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
        
        # The expected preload should be calculated correctly
        expected_preload = (tightening_torque - removal_torque) * math.pi / thread_pitch
        self.assertAlmostEqual(preload, expected_preload, places=3)
        
        # Test with extremely large difference
        self.assertGreater(preload, 0, "Preload should be positive for large torque values")
    
    def test_final_torque_with_tiny_preload_increase(self):
        """
        Test final torque calculation with a tiny increase in desired preload.
        
        This tests for precision in small adjustment scenarios.
        """
        initial_torque = 35.0
        removal_torque = 30.0
        thread_pitch = 0.04
        
        # Calculate initial preload
        initial_preload = calculate_preload(initial_torque, removal_torque, thread_pitch)
        
        # Desired preload is just 0.1% higher than initial
        desired_preload = initial_preload * 1.001
        
        # Calculate final torque
        final_torque = calculate_final_torque(
            initial_torque, 
            removal_torque, 
            initial_preload, 
            desired_preload, 
            thread_pitch
        )
        
        # The final torque should be very close to but slightly higher than initial torque
        self.assertGreater(final_torque, initial_torque, 
                          "Final torque should be greater than initial for increased preload")
        self.assertLess(final_torque - initial_torque, 0.1, 
                       "Final torque increase should be less than 0.1 N-cm for 0.1% preload increase")
    
    def test_final_torque_with_huge_preload_increase(self):
        """
        Test final torque calculation with a massive increase in desired preload.
        
        This tests for handling large scale adjustments.
        """
        initial_torque = 35.0
        removal_torque = 30.0
        thread_pitch = 0.04
        
        # Calculate initial preload
        initial_preload = calculate_preload(initial_torque, removal_torque, thread_pitch)
        
        # Desired preload is 10 times initial
        desired_preload = initial_preload * 10
        
        # Calculate final torque
        final_torque = calculate_final_torque(
            initial_torque, 
            removal_torque, 
            initial_preload, 
            desired_preload, 
            thread_pitch
        )
        
        # The final torque should be approximately 10 times initial
        self.assertAlmostEqual(
            final_torque / initial_torque, 
            10.0, 
            places=1,
            msg="Final torque should be approximately 10x initial for 10x preload"
        )
    
    def test_extremely_small_thread_pitch(self):
        """
        Test with extremely small thread pitch.
        
        This tests for potential division by very small numbers, which could
        cause numerical instability.
        """
        tightening_torque = 35.0
        removal_torque = 30.0
        thread_pitch = 1e-10  # Extremely small
        
        # Calculate preload
        preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
        
        # The preload should be very large but finite
        self.assertTrue(np.isfinite(preload), "Preload should be finite even with tiny thread pitch")
        self.assertGreater(preload, 0, "Preload should be positive")
        
        # Calculate expected value
        expected_preload = (tightening_torque - removal_torque) * math.pi / thread_pitch
        self.assertAlmostEqual(preload, expected_preload, places=3)
    
    def test_extremely_large_thread_pitch(self):
        """
        Test with extremely large thread pitch.
        
        This tests boundary conditions for unusually large thread pitch values.
        """
        tightening_torque = 35.0
        removal_torque = 30.0
        thread_pitch = 1000.0  # Very large thread pitch
        
        # Calculate preload
        preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
        
        # The preload should be very small but positive
        self.assertGreater(preload, 0, "Preload should be positive")
        self.assertLess(preload, 1, "Preload should be small with large thread pitch")
        
        # Calculate expected value
        expected_preload = (tightening_torque - removal_torque) * math.pi / thread_pitch
        self.assertAlmostEqual(preload, expected_preload, places=10)
    
    def test_handling_floating_point_precision(self):
        """
        Test handling of floating-point precision issues.
        
        This tests for robustness against floating-point rounding errors.
        """
        # Use values known to cause floating-point precision issues
        tightening_torque = 0.1 + 0.2  # Actually 0.30000000000000004 in floating point
        removal_torque = 0.1
        thread_pitch = 0.04
        
        # Calculate preload
        preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
        
        # Calculate with precise values
        expected_preload = 0.2 * math.pi / thread_pitch
        
        # Should still get correct result despite floating-point issues
        self.assertAlmostEqual(preload, expected_preload, places=10)
    
    def test_torque_stress_safety_factor_chain(self):
        """
        Test the entire calculation chain from torque to safety factor with extreme values.
        
        This tests the integration of multiple functions with edge case inputs.
        """
        # Very large torque value
        torque = 1000.0  # 1000 N-cm
        screw_diameter = 0.2  # cm
        k_factor = 0.2
        tensile_area = 2.0  # mm²
        yield_strength = 800  # MPa
        
        # Calculate preload using conventional method
        preload = estimate_preload_from_torque(torque, screw_diameter, k_factor)
        
        # Calculate stress
        stress = calculate_stress_from_preload(preload, tensile_area)
        
        # Calculate safety factor
        safety_factor = calculate_safety_factor(stress, yield_strength)
        
        # The safety factor should be calculated correctly
        expected_preload = torque / (k_factor * screw_diameter)
        expected_stress = expected_preload / tensile_area
        expected_safety_factor = yield_strength / expected_stress
        
        self.assertAlmostEqual(safety_factor, expected_safety_factor, places=10)
        
        # For these extreme values, we should get a very low safety factor
        self.assertLess(safety_factor, 1.0, "Safety factor should be very low for extreme torque")
        
        # Assess risk
        risk_level, _ = assess_risk(safety_factor)
        self.assertEqual(risk_level, "High", "Should report high risk for low safety factor")
    
    def test_stress_with_microscopic_tensile_area(self):
        """
        Test stress calculation with extremely small tensile area.
        
        This tests division by a very small number in stress calculation.
        """
        preload = 400  # N
        tensile_area = 1e-6  # Extremely small area (1 µm²)
        
        # Calculate stress
        stress = calculate_stress_from_preload(preload, tensile_area)
        
        # Stress should be very high but finite
        self.assertTrue(np.isfinite(stress), "Stress should be finite")
        self.assertGreater(stress, 0, "Stress should be positive")
        
        # Check expected value
        expected_stress = preload / tensile_area
        self.assertAlmostEqual(stress, expected_stress, places=3)
    
    def test_zero_stress_safety_factor(self):
        """
        Test safety factor calculation with zero stress.
        
        This tests division by zero protection in safety factor calculation.
        """
        stress = 0.0
        yield_strength = 800
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            calculate_safety_factor(stress, yield_strength)
    
    def test_negative_safety_factor_risk_assessment(self):
        """
        Test risk assessment with negative safety factor.
        
        This tests input validation for the risk assessment function.
        """
        safety_factor = -1.0
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            assess_risk(safety_factor)
    
    def test_all_functions_type_safety(self):
        """
        Test type safety of all functions with invalid types.
        
        This ensures functions properly validate input types.
        """
        # Test with strings instead of numbers
        with self.assertRaises((TypeError, ValueError)):
            calculate_preload("35", "30", "0.04")
        
        with self.assertRaises((TypeError, ValueError)):
            calculate_final_torque("25", "20", "200", "300", "0.04")
        
        with self.assertRaises((TypeError, ValueError)):
            calculate_stress_from_preload("400", "2.0")
        
        with self.assertRaises((TypeError, ValueError)):
            calculate_safety_factor("200", "800")
    
    def test_boundary_value_analysis(self):
        """
        Test boundary values for each function.
        
        This systematically tests boundary conditions for each parameter.
        """
        # Very small positive values (approaching zero)
        epsilon = sys.float_info.epsilon  # Smallest positive float
        
        # Test calculate_preload
        preload = calculate_preload(epsilon, 0, epsilon)
        self.assertTrue(np.isfinite(preload), "Preload should be finite with tiny values")
        
        # Test calculate_stress_from_preload with minimum positive area
        stress = calculate_stress_from_preload(epsilon, epsilon)
        self.assertEqual(stress, 1.0, "Stress should be 1.0 when force = area")
        
        # Test with maximum float values
        max_float = sys.float_info.max
        
        # Should not overflow with very large values for safety factor
        safety_factor = calculate_safety_factor(1.0, max_float)
        self.assertTrue(np.isfinite(safety_factor), "Safety factor should be finite")
        self.assertGreater(safety_factor, 0, "Safety factor should be positive")


if __name__ == "__main__":
    unittest.main() 