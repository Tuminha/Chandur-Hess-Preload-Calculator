#!/usr/bin/env python3
"""
Preload calculation module based on the Wadhwani-Hess theoretical model.

This module implements the calculation formulas from the paper:
"A new method to estimate dental implant stability and critical healing time
using torque values" by Chandur P.K. Wadhwani and Thomas D. Hess.

References:
- Equation 3: P = (Tt - Tr) * π / p
- Equation 6: Ti = (p * Tt * P_desired) / (π * (Tt - Tr))

Where:
- P: Preload (N)
- Tt: Tightening torque (N-cm)
- Tr: Removal torque (N-cm)
- p: Thread pitch (cm)
- π: Pi (3.14159...)
- Ti: Final tightening torque (N-cm)
- P_desired: Desired preload (N)
"""

import math
from typing import Tuple, Optional


def calculate_preload(tightening_torque: float, removal_torque: float, thread_pitch: float) -> float:
    """
    Calculate the preload based on the Wadhwani-Hess formula (Equation 3).
    
    Args:
        tightening_torque: The initial tightening torque (N-cm)
        removal_torque: The measured removal torque (N-cm)
        thread_pitch: The thread pitch of the screw (cm)
        
    Returns:
        float: The calculated preload (N)
        
    Raises:
        ValueError: If thread_pitch is less than or equal to zero
    """
    if thread_pitch <= 0:
        raise ValueError("Thread pitch must be greater than zero")
        
    # Equation 3: P = (Tt - Tr) * π / p
    return (tightening_torque - removal_torque) * math.pi / thread_pitch


def calculate_final_torque(
    initial_torque: float,
    removal_torque: float,
    initial_preload: float,
    desired_preload: float,
    thread_pitch: float,
    use_ratio_method: bool = False
) -> float:
    """
    Calculate the final tightening torque needed to achieve the desired preload.
    
    This implements Equation 6 from the Wadhwani-Hess paper:
    Ti = (p * Tt * P_desired) / (π * (Tt - Tr))
    
    Args:
        initial_torque: The initial tightening torque (N-cm)
        removal_torque: The measured removal torque (N-cm)
        initial_preload: The initial preload calculated from initial_torque and removal_torque
        desired_preload: The desired final preload (N)
        thread_pitch: The thread pitch of the screw (cm)
        use_ratio_method: Whether to use the ratio method instead of Equation 6 (default: False)
        
    Returns:
        float: The calculated final tightening torque (N-cm)
        
    Raises:
        ValueError: If thread_pitch is less than or equal to zero or if 
                   initial_torque is less than or equal to removal_torque
    """
    if thread_pitch <= 0:
        raise ValueError("Thread pitch must be greater than zero")
        
    if initial_torque <= removal_torque:
        raise ValueError("Initial torque must be greater than removal torque")
    
    # Simple ratio method (mathematically equivalent to Equation 6 when using Wadhwani-Hess preload formula)
    ratio_method = initial_torque * (desired_preload / initial_preload)
    
    # Equation 6: Ti = (p * Tt * P_desired) / (π * (Tt - Tr))
    exact_method = (thread_pitch * initial_torque * desired_preload) / (math.pi * (initial_torque - removal_torque))
    
    return ratio_method if use_ratio_method else exact_method


def calculate_self_loosening(tightening_torque: float, removal_torque: float) -> float:
    """
    Calculate the self-loosening component of torque.
    
    Self-loosening is defined as (Tt - Tr) / 2
    
    Args:
        tightening_torque: The tightening torque (N-cm)
        removal_torque: The removal torque (N-cm)
        
    Returns:
        float: The calculated self-loosening torque (N-cm)
    """
    return (tightening_torque - removal_torque) / 2


def calculate_primary_locking(tightening_torque: float, removal_torque: float) -> float:
    """
    Calculate the primary locking component of torque.
    
    Primary locking is defined as (Tt + Tr) / 2
    
    Args:
        tightening_torque: The tightening torque (N-cm)
        removal_torque: The removal torque (N-cm)
        
    Returns:
        float: The calculated primary locking torque (N-cm)
    """
    return (tightening_torque + removal_torque) / 2


def estimate_uncertainty(torque_value: float, is_lubricated: bool = False) -> Tuple[int, float]:
    """
    Estimate the uncertainty in preload for conventional calculation methods.
    
    For conventional methods, the uncertainty is typically:
    - 35% for unlubricated screws
    - 25% for lubricated screws
    
    Args:
        torque_value: The torque value (N-cm)
        is_lubricated: Whether the screw is lubricated
        
    Returns:
        Tuple[int, float]: A tuple containing (uncertainty_percentage, uncertainty_value)
    """
    uncertainty_percent = 25 if is_lubricated else 35
    uncertainty_value = (uncertainty_percent / 100) * torque_value
    
    return uncertainty_percent, uncertainty_value


def calculate_preload_range(preload: float, uncertainty_percent: float) -> Tuple[float, float]:
    """
    Calculate the min and max preload based on uncertainty percentage.
    
    Args:
        preload: The estimated preload (N)
        uncertainty_percent: The uncertainty percentage
        
    Returns:
        Tuple[float, float]: A tuple containing (min_preload, max_preload)
    """
    uncertainty_factor = uncertainty_percent / 100
    min_preload = preload * (1 - uncertainty_factor)
    max_preload = preload * (1 + uncertainty_factor)
    
    return min_preload, max_preload 