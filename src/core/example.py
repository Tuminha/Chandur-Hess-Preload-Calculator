#!/usr/bin/env python3
"""
Example script to demonstrate the use of the preload calculation module.

This script shows how to use the Wadhwani-Hess model to calculate
preload, final torque, self-loosening, and primary locking.
"""

import sys
import math
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the preload calculation modules
from src.core.preload import (
    calculate_preload,
    calculate_final_torque,
    calculate_self_loosening,
    calculate_primary_locking,
    estimate_uncertainty,
    calculate_preload_range
)

# Import torque calculation modules
from src.core.torque import (
    estimate_preload_from_torque,
    calculate_stress_from_preload,
    calculate_safety_factor,
    calculate_tensile_area,
    assess_risk
)


def example_wadhwani_hess_method():
    """
    Example using the Wadhwani-Hess method for preload calculation.
    
    This example uses the data from the paper to demonstrate the calculation
    of initial preload, final torque, self-loosening, and primary locking.
    """
    print("=" * 50)
    print("WADHWANI-HESS METHOD EXAMPLE")
    print("=" * 50)
    
    # Example data from the paper
    initial_torque = 25  # N-cm
    removal_torque = 21.4  # N-cm
    thread_pitch = 0.04  # cm
    desired_preload = 400  # N
    
    # Calculate the initial preload
    initial_preload = calculate_preload(initial_torque, removal_torque, thread_pitch)
    
    # Calculate the final torque needed for the desired preload
    final_torque = calculate_final_torque(
        initial_torque, removal_torque, initial_preload, desired_preload, thread_pitch
    )
    
    # Calculate final torque using the ratio method
    final_torque_ratio = calculate_final_torque(
        initial_torque, removal_torque, initial_preload, desired_preload, thread_pitch, 
        use_ratio_method=True
    )
    
    # Calculate the self-loosening and primary locking components
    self_loosening = calculate_self_loosening(initial_torque, removal_torque)
    primary_locking = calculate_primary_locking(initial_torque, removal_torque)
    
    # Print the results
    print(f"Initial torque: {initial_torque} N-cm")
    print(f"Removal torque: {removal_torque} N-cm")
    print(f"Initial preload: {initial_preload:.2f} N")
    print(f"Desired preload: {desired_preload} N")
    print(f"Final torque required (exact method): {final_torque:.2f} N-cm")
    print(f"Final torque required (ratio method): {final_torque_ratio:.2f} N-cm")
    print(f"Self-loosening: {self_loosening:.2f} N-cm")
    print(f"Primary locking: {primary_locking:.2f} N-cm")
    print()
    
    # Show formula details
    print("FORMULA DETAILS:")
    print("Preload (Equation 3): P = (Tt - Tr) * π / p")
    preload_manual = (initial_torque - removal_torque) * math.pi / thread_pitch
    print(f"  = ({initial_torque} - {removal_torque}) * π / {thread_pitch}")
    print(f"  = {preload_manual:.2f} N")
    print()
    
    print("Final Torque (Equation 6): Ti = (p * Tt * P_desired) / (π * (Tt - Tr))")
    torque_manual = (thread_pitch * initial_torque * desired_preload) / (math.pi * (initial_torque - removal_torque))
    print(f"  = ({thread_pitch} * {initial_torque} * {desired_preload}) / (π * ({initial_torque} - {removal_torque}))")
    print(f"  = {torque_manual:.2f} N-cm")
    print()
    
    print("Ratio Method: Ti = Tt * (P_desired / P_initial)")
    ratio_manual = initial_torque * (desired_preload / initial_preload)
    print(f"  = {initial_torque} * ({desired_preload} / {initial_preload:.2f})")
    print(f"  = {ratio_manual:.2f} N-cm")
    print()


def example_conventional_method():
    """
    Example using the conventional method for preload estimation.
    
    This example demonstrates the calculation of estimated preload,
    stress, safety factor, and risk assessment.
    """
    print("=" * 50)
    print("CONVENTIONAL METHOD EXAMPLE")
    print("=" * 50)
    
    # Example data
    nominal_torque = 35  # N-cm
    screw_diameter = 0.2  # cm (2 mm)
    thread_pitch = 0.04  # cm (0.4 mm)
    yield_strength = 800  # MPa for titanium alloy
    
    # Calculate tensile area (approximate)
    # Using the formula: A_t = π/4 * (d - 0.9382*p)^2
    tensile_diameter = screw_diameter - 0.9382 * thread_pitch
    tensile_area = math.pi/4 * tensile_diameter**2
    tensile_area_mm2 = tensile_area * 100  # convert from cm² to mm²
    
    # Estimate preload using conventional method (T = K*d*F)
    # Using K = 0.2 for lubricated screws
    k_factor = 0.2
    estimated_preload = nominal_torque / (k_factor * screw_diameter)
    
    # Calculate stress (N/mm² = MPa)
    # 1 N/mm² = 1 MPa
    stress_mpa = estimated_preload / tensile_area_mm2
    
    # Calculate safety factor
    safety_factor = yield_strength / stress_mpa
    
    # Assess risk level
    if safety_factor > 2.5:
        risk_level = "Low"
        recommendation = "Safe for long-term use with standard maintenance."
    elif safety_factor > 1.5:
        risk_level = "Medium"
        recommendation = "Safe for use, but consider more frequent check-ups."
    elif safety_factor > 1.0:
        risk_level = "High"
        recommendation = "Use with caution and frequent monitoring."
    else:
        risk_level = "Critical"
        recommendation = "NOT SAFE FOR USE. Redesign required."
    
    # Print results
    print(f"Nominal torque: {nominal_torque} N-cm")
    print(f"Screw diameter: {screw_diameter} cm")
    print(f"Thread pitch: {thread_pitch} cm")
    print(f"Tensile area: {tensile_area_mm2:.2f} mm²")
    print(f"Estimated preload: {estimated_preload:.2f} N")
    print(f"Stress: {stress_mpa:.2f} MPa")
    print(f"Yield strength: {yield_strength} MPa")
    print(f"Safety factor: {safety_factor:.2f}")
    print(f"Risk level: {risk_level}")
    print(f"Recommendation: {recommendation}")
    print()


def example_compare_methods():
    """
    Compare the Wadhwani-Hess method with the conventional method.
    
    This example demonstrates the improved accuracy of the
    Wadhwani-Hess method over the conventional method.
    """
    print("=" * 50)
    print("COMPARISON OF METHODS")
    print("=" * 50)
    
    # Example data
    nominal_torque = 35  # N-cm
    removal_torque = 29.5  # N-cm (average from specimen data)
    thread_pitch = 0.04  # cm
    screw_diameter = 0.2  # cm
    
    # Conventional method (with uncertainty)
    # Using K = 0.2 for lubricated screws
    k_factor = 0.2
    conventional_preload = estimate_preload_from_torque(nominal_torque, screw_diameter, k_factor)
    uncertainty_percent, uncertainty_value = estimate_uncertainty(nominal_torque, False)
    min_preload, max_preload = calculate_preload_range(conventional_preload, uncertainty_percent)
    
    # Wadhwani-Hess method
    wh_preload = calculate_preload(nominal_torque, removal_torque, thread_pitch)
    
    # Print results
    print("Conventional Method:")
    print(f"  Estimated preload: {conventional_preload:.2f} N")
    print(f"  Uncertainty: +/- {uncertainty_percent}%")
    print(f"  Preload range: {min_preload:.2f} - {max_preload:.2f} N")
    print()
    
    print("Wadhwani-Hess Method:")
    print(f"  Calculated preload: {wh_preload:.2f} N")
    print(f"  Uncertainty: +/- 9% (from paper)")
    print(f"  Preload range: {wh_preload*0.91:.2f} - {wh_preload*1.09:.2f} N")
    print()
    
    print("Conclusion:")
    in_range = min_preload <= wh_preload <= max_preload
    print(f"  Wadhwani-Hess preload {'is' if in_range else 'is not'} within the conventional method range.")
    print(f"  The uncertainty is reduced by {uncertainty_percent - 9}% compared to the conventional method.")
    print(f"  This confirms the improved accuracy of the Wadhwani-Hess method.")
    print()


def example_implant_systems():
    """
    Example calculations for different implant systems.
    
    This example demonstrates preload and stress calculations for
    different dental implant systems using data from the sample_systems.json file.
    """
    print("=" * 50)
    print("IMPLANT SYSTEMS COMPARISON")
    print("=" * 50)
    
    # Load implant systems data
    data_path = Path(__file__).parent.parent.parent / "data" / "implant_systems" / "sample_systems.json"
    
    with open(data_path, 'r') as f:
        implant_data = json.load(f)
    
    systems = implant_data["implant_systems"]
    
    # Set up comparison table headers
    print(f"{'Implant System':<25} {'Conv. Preload':<15} {'W-H Preload':<15} {'Safety Factor':<15} {'Risk Level':<10}")
    print("-" * 80)
    
    # Assume removal torque is 85% of tightening torque
    removal_torque_factor = 0.85
    
    for system_name, system_data in systems.items():
        for model_name, model_data in system_data.items():
            # Get screw data
            screw_data = model_data["screws"]["standard"]
            
            # Get parameters
            torque = screw_data["recommended_torque"]  # N-cm
            diameter = screw_data["diameter"] / 10  # mm to cm
            thread_pitch = screw_data["thread_pitch"] / 10  # mm to cm
            k_factor = screw_data["K_factor"]
            yield_strength = screw_data["yield_strength"]  # MPa
            
            # Calculate tensile area
            tensile_area = calculate_tensile_area(screw_data["diameter"], screw_data["thread_pitch"])
            
            # Calculate preload using conventional method
            conventional_preload = estimate_preload_from_torque(torque, diameter, k_factor)
            
            # Calculate stress and safety factor
            stress = calculate_stress_from_preload(conventional_preload, tensile_area)
            safety_factor = calculate_safety_factor(stress, yield_strength)
            
            # Get risk level
            risk_level, _ = assess_risk(safety_factor)
            
            # Calculate preload using Wadhwani-Hess method
            removal_torque = torque * removal_torque_factor
            wh_preload = calculate_preload(torque, removal_torque, thread_pitch)
            
            # Print results in table format
            print(f"{system_name + ' ' + model_name:<25} {conventional_preload:>10.2f} N    {wh_preload:>10.2f} N    {safety_factor:>10.2f}    {risk_level:<10}")
    
    print()
    print("Notes:")
    print("1. Conventional preload calculated using T = K*d*F formula")
    print("2. Wadhwani-Hess preload calculated using P = (Tt - Tr) * π / p")
    print("3. Removal torque estimated as 85% of tightening torque")
    print("4. Safety factor calculated as Yield Strength / Stress")
    print("5. Risk levels: Low (SF > 3.0), Medium (1.5 < SF ≤ 3.0), High (SF ≤ 1.5)")
    print()


def main():
    """Run all examples."""
    example_wadhwani_hess_method()
    example_conventional_method()
    example_compare_methods()
    example_implant_systems()


if __name__ == "__main__":
    main() 