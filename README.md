# Chandur-Hess-Preload-Calculator

A comprehensive web application for accurately calculating and measuring preload in dental implants using the Wadhwani-Hess theoretical model.

## Overview

This project implements the preload calculation formulas from the paper: "A novel approach to achieve preload in dental implant systems" by Chandur P.K. Wadhwani and Thomas D. Hess.

The key features include:

- **Accurate Preload Calculation**: Using the Wadhwani-Hess model for precise preload determination
- **Final Torque Calculation**: Determining the required torque to achieve a desired preload
- **Comparative Analysis**: Comparing the Wadhwani-Hess method with conventional methods
- **Risk Assessment**: Evaluating safety factors and risk levels
- **Implant Systems Database**: Support for major implant systems and their specifications

## Theoretical Model

The Wadhwani-Hess model provides a more accurate method for calculating preload by measuring both tightening and removal torque. The key equations implemented are:

### Equation 3: Preload Calculation
```
P = (Tt - Tr) * π / p
```
Where:
- P: Preload (N)
- Tt: Tightening torque (N-cm)
- Tr: Removal torque (N-cm)
- p: Thread pitch (cm)
- π: Pi (3.14159...)

### Equation 6: Final Tightening Torque
```
Ti = (p * Tt * P_desired) / (π * (Tt - Tr))
```
Where:
- Ti: Final tightening torque (N-cm)
- P_desired: Desired preload (N)

## Project Structure

```
chandur-hess-preload-calculator/
├── app/
│   ├── app.py                          # Main Streamlit application
│   └── components/                     # UI components
│       ├── welcome.py                  # Welcome page
│       ├── preload_calculator.py       # Preload calculator component
│       ├── final_torque_calculator.py  # Final torque calculator component
│       ├── compare_methods.py          # Methods comparison component
│       ├── implant_systems_analysis.py # Implant systems analysis component
│       └── generate_report.py          # PDF report generation
├── src/
│   ├── core/
│   │   ├── preload.py                  # Core preload calculation module
│   │   ├── torque.py                   # Torque and stress calculations
│   │   └── example.py                  # Example script demonstrating usage
│   └── __init__.py
├── tests/
│   ├── test_preload.py                 # Test suite for the preload module
│   ├── test_torque.py                  # Tests for torque calculations
│   └── test_implant_systems.py         # Tests for implant systems calculations
├── data/
│   └── implant_systems/                # Implant systems specifications
│       └── sample_systems.json         # Database of implant systems
└── README.md
```

## Usage Examples

### Calculating Preload

```python
from src.core.preload import calculate_preload

# Example values
tightening_torque = 35  # N-cm
removal_torque = 29.5   # N-cm
thread_pitch = 0.04     # cm

# Calculate preload
preload = calculate_preload(tightening_torque, removal_torque, thread_pitch)
print(f"Calculated preload: {preload:.2f} N")
```

### Calculating Final Torque for Desired Preload

```python
from src.core.preload import calculate_preload, calculate_final_torque

# Example values
initial_torque = 25     # N-cm
removal_torque = 21.4   # N-cm
thread_pitch = 0.04     # cm
desired_preload = 400   # N

# First calculate initial preload
initial_preload = calculate_preload(initial_torque, removal_torque, thread_pitch)

# Then calculate final torque needed
final_torque = calculate_final_torque(
    initial_torque, removal_torque, initial_preload, desired_preload, thread_pitch
)
print(f"Final torque required: {final_torque:.2f} N-cm")
```

## Web Application

The project includes a Streamlit web application that provides an easy-to-use interface for the preload calculation formulas.

### Features

- **Preload Calculator**: Calculate preload using the Wadhwani-Hess method
- **Final Torque Calculator**: Determine the required torque to achieve a desired preload
- **Method Comparison**: Compare the Wadhwani-Hess method with conventional methods
- **Implant Systems Analysis**: Analyze different implant systems
- **PDF Report Generation**: Generate comprehensive PDF reports of calculations

### Running the App

To run the Streamlit app:

```bash
# Install requirements
pip install -r requirements.txt

# Run the app
streamlit run app/app.py
```

The app will open in your default web browser at http://localhost:8501

## Key Benefits

1. **Improved Accuracy**: The Wadhwani-Hess method reduces uncertainty to approximately ±9% compared to ±35% for conventional methods
2. **Scientific Foundation**: Based on rigorous scientific research with experimental validation
3. **Practical Application**: Directly applicable to clinical settings for improved implant stability

## Implant Systems Comparison

The toolkit was tested with specifications from major implant systems, including:

- Nobel Biocare (Branemark, Replace)
- Straumann (BoneLevel, TissueLevel)
- Dentsply Astra (OsseoSpeed)
- Camlog (Screw_Line)

### Conventional vs. Wadhwani-Hess Method

Analysis across implant systems shows significant differences between conventional and Wadhwani-Hess preload calculations:

| Implant System          | Conventional Preload | W-H Preload | Uncertainty Reduction |
|-------------------------|----------------------|-------------|------------------------|
| Nobel Biocare Branemark | 583.33 N (±35%)      | 412.33 N (±9%) | 81.8% |
| Nobel Biocare Replace   | 875.00 N (±35%)      | 412.33 N (±9%) | 87.9% |
| Straumann BoneLevel     | 994.32 N (±35%)      | 471.24 N (±9%) | 87.8% |
| Straumann TissueLevel   | 925.93 N (±35%)      | 471.24 N (±9%) | 86.9% |
| Dentsply Astra OsseoSpeed | 694.44 N (±35%)    | 336.60 N (±9%) | 87.5% |
| Camlog Screw_Line       | 560.22 N (±35%)      | 269.28 N (±9%) | 87.6% |

### Safety Factors Analysis

Assessment of safety factors for different implant systems based on conventional preload estimates:

| Implant System          | Stress (MPa) | Safety Factor | Risk Level |
|-------------------------|--------------|---------------|------------|
| Nobel Biocare Branemark | 281.36       | 3.02          | Low        |
| Nobel Biocare Replace   | 422.05       | 2.25          | Medium     |
| Straumann BoneLevel     | 782.91       | 1.21          | High       |
| Straumann TissueLevel   | 544.36       | 1.75          | Medium     |
| Dentsply Astra OsseoSpeed | 408.27     | 2.33          | Medium     |
| Camlog Screw_Line       | 379.14       | 2.51          | Medium     |

This analysis highlights the importance of accurate preload calculation, as higher preload values can lead to excessive stress and potential implant failure.

## Running Tests

```bash
# Run all tests
python -m unittest discover -s tests

# Run a specific test file
python -m unittest tests/test_preload.py

# Run implant systems tests
python -m unittest tests/test_implant_systems.py
```

## Example Output

The example script demonstrates:

1. **Wadhwani-Hess Method**: Calculating preload, final torque, self-loosening, and primary locking
2. **Conventional Method**: Estimating preload, stress, and safety factors
3. **Comparison**: Showing the improved accuracy of the Wadhwani-Hess method

To run the example script:

```bash
python src/core/example.py
```

## Future Enhancements

- Web-based UI for easy calculations
- Mobile application for clinical use
- Database integration for tracking implant metrics
- Machine learning for predictive preload analysis
- Expansion of implant systems database with more manufacturers

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dr. Chandur P.K. Wadhwani and Dr. Thomas D. Hess for their groundbreaking research
- The dental implant community for supporting evidence-based approaches to implant stability
- Implant manufacturers for providing technical specifications 