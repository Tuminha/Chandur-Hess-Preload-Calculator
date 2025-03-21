#!/usr/bin/env python3
"""
Torque-related calculations for dental implant preload.

This module implements torque-related calculations, including:
- Conventional preload estimation from tightening torque
- Stress calculation from preload
- Safety factor calculation
- Risk assessment
"""

import math
from typing import Union, Tuple, Dict, List, Optional


def estimate_preload_from_torque(
    torque: float,
    screw_diameter: float,
    k_factor: float = 0.2
) -> float:
    """
    Estimate preload from tightening torque using conventional methods.
    
    Parameters:
    -----------
    torque : float
        The tightening torque in N-cm
    screw_diameter : float
        The nominal diameter of the screw in cm
    k_factor : float, optional
        The nut factor, which accounts for friction (default: 0.2)
        Typical values:
        - 0.20 for lubricated or coated screws
        - 0.30 for unlubricated screws
        
    Returns:
    --------
    float
        The estimated preload in N
    
    Notes:
    ------
    Uses the conventional formula: T = K * F * d
    Where T is torque, K is the nut factor, F is preload, and d is screw diameter.
    """
    if screw_diameter <= 0:
        raise ValueError("Screw diameter must be positive")
    if k_factor <= 0:
        raise ValueError("k_factor must be positive")
    
    return torque / (k_factor * screw_diameter)


def calculate_stress_from_preload(
    preload: float,
    tensile_area: float
) -> float:
    """
    Calculate stress in the screw from preload.
    
    Parameters:
    -----------
    preload : float
        The preload force in N
    tensile_area : float
        The tensile stress area of the screw in mm²
        
    Returns:
    --------
    float
        The stress in MPa (N/mm²)
    
    Notes:
    ------
    Uses the formula: Stress = Force / Area
    """
    if tensile_area <= 0:
        raise ValueError("Tensile area must be positive")
    
    # Convert N/mm² to MPa (they are equivalent)
    return preload / tensile_area


def calculate_safety_factor(
    stress: float,
    yield_strength: float
) -> float:
    """
    Calculate safety factor based on stress and material yield strength.
    
    Parameters:
    -----------
    stress : float
        The stress in the screw in MPa
    yield_strength : float
        The yield strength of the screw material in MPa
        
    Returns:
    --------
    float
        The safety factor (dimensionless)
    
    Notes:
    ------
    Uses the formula: Safety Factor = Yield Strength / Stress
    """
    if stress <= 0:
        raise ValueError("Stress must be positive")
    if yield_strength <= 0:
        raise ValueError("Yield strength must be positive")
    
    return yield_strength / stress


def assess_risk(
    safety_factor: float,
    min_safety_factor: float = 1.5
) -> Tuple[str, str]:
    """
    Assess the risk of screw loosening or failure based on safety factor.
    
    Parameters:
    -----------
    safety_factor : float
        The calculated safety factor
    min_safety_factor : float, optional
        The minimum acceptable safety factor (default: 1.5)
        
    Returns:
    --------
    Tuple[str, str]
        A tuple containing (risk_level, recommendation)
        
    Notes:
    ------
    Risk levels:
    - Low risk: safety_factor > 3.0
    - Medium risk: 1.5 <= safety_factor <= 3.0
    - High risk: safety_factor < 1.5
    """
    if safety_factor < 0:
        raise ValueError("Safety factor must be positive")
    
    if safety_factor > 3.0:
        risk_level = "Low"
        recommendation = "Safe for use with standard protocol"
    elif safety_factor >= min_safety_factor:
        risk_level = "Medium"
        recommendation = "Safe for use, but consider more frequent check-ups"
    else:
        risk_level = "High"
        recommendation = "Not recommended, consider alternative implant system or reduced loading"
    
    return risk_level, recommendation


def calculate_tensile_area(
    nominal_diameter: float,
    thread_pitch: float
) -> float:
    """
    Calculate tensile stress area of a screw.
    
    Parameters:
    -----------
    nominal_diameter : float
        The nominal diameter of the screw in mm
    thread_pitch : float
        The thread pitch in mm
        
    Returns:
    --------
    float
        The tensile stress area in mm²
    
    Notes:
    ------
    Uses the formula: A_t = (π/4) * (d - 0.9382*p)²
    Where d is nominal diameter and p is thread pitch.
    """
    if nominal_diameter <= 0:
        raise ValueError("Nominal diameter must be positive")
    if thread_pitch <= 0:
        raise ValueError("Thread pitch must be positive")
    
    effective_diameter = nominal_diameter - 0.9382 * thread_pitch
    return (math.pi / 4) * (effective_diameter ** 2)


def calculate_torque_range(
    nominal_torque: float,
    is_lubricated: bool = False
) -> Tuple[float, float]:
    """
    Calculate the acceptable range of tightening torques based on manufacturer specifications.
    
    Parameters:
    -----------
    nominal_torque : float
        The nominal torque specified by the manufacturer in N-cm
    is_lubricated : bool, optional
        Whether the screw is lubricated (default: False)
        
    Returns:
    --------
    Tuple[float, float]
        The minimum and maximum torque values in N-cm
    
    Notes:
    ------
    According to the paper, conventional uncertainty is:
    - +/- 35% for unlubricated screws
    - +/- 25% for lubricated screws
    """
    uncertainty = 25 if is_lubricated else 35
    uncertainty_factor = uncertainty / 100
    
    min_torque = nominal_torque * (1 - uncertainty_factor)
    max_torque = nominal_torque * (1 + uncertainty_factor)
    
    return min_torque, max_torque 