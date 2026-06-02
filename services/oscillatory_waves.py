"""
Oscillatory Waves - Analytical Solution
========================================

This module implements the EXACT mathematical model from vypocet.txt.
No simplifications or numerical approximations are allowed without explicit justification.

Mathematical Foundation (from vypocet.txt):
------------------------------------------

Simplified activator equation (Riccati ODE):
    da/dt = k·a² - r_a·a + b_a

where:
    k = s / (s_b + b₀) > 0

Equilibrium points (setting da/dt = 0):
    k·a² - r_a·a + b_a = 0

Discriminant:
    D = r_a² - 4·k·b_a

Roots (equilibrium points):
    a₁* = (r_a - √D) / (2k)  (lower stable point)
    a₂* = (r_a + √D) / (2k)  (upper boundary point)

Analytical solution via partial fraction decomposition:
    a(t) = (a₁* - a₂*·C₀·exp(λt)) / (1 - C₀·exp(λt))

where:
    λ = k·(a₂* - a₁*)  (growth rate)
    C₀ = (a₀ - a₁*) / (a₀ - a₂*)  (integration constant)
    a₀ = initial condition at t=0

Asymptotic behavior:
    t → ∞: a(t) → a₁*  (saturation to lower equilibrium)
"""

import numpy as np
from typing import Dict, Tuple, List
import os


class OscillatoryWavesCalculator:
    """
    Implements exact analytical solution of the Riccati ODE from vypocet.txt.

    This class is the SOURCE OF TRUTH - all calculations must match
    the mathematical derivation in vypocet.txt step by step.
    """

    def __init__(self, params: Dict[str, float]):
        """
        Initialize calculator with physical parameters.

        Args:
            params: Dictionary containing:
                - s: autocatalysis strength
                - s_b: inhibitor baseline parameter
                - b_0: inhibitor concentration (assumed constant)
                - r_a: activator decay rate
                - b_a: activator baseline production
                - a_0: initial activator concentration
                - t_max: maximum simulation time
                - dt: time step for output generation
        """
        self.params = params

        # Extract parameters (following vypocet.txt notation)
        self.s = params['s']
        self.s_b = params['s_b']
        self.b_0 = params['b_0']
        self.r_a = params['r_a']
        self.b_a = params['b_a']
        self.a_0 = params['a_0']
        self.t_max = params.get('t_max', 100.0)
        self.dt = params.get('dt', 0.1)

        # Calculate derived parameter k (equation from vypocet.txt line 50, 116)
        # k = s / (s_b + b₀)
        self.k = self.s / (self.s_b + self.b_0)

        # Calculate discriminant (vypocet.txt line 133)
        # D = r_a² - 4·k·b_a
        self.D = self.r_a**2 - 4 * self.k * self.b_a

        # Equilibrium points (vypocet.txt line 141)
        if self.D >= 0:
            sqrt_D = np.sqrt(self.D)
            # a₁* = (r_a - √D) / (2k)  - lower equilibrium
            self.a1_star = (self.r_a - sqrt_D) / (2 * self.k)
            # a₂* = (r_a + √D) / (2k)  - upper equilibrium
            self.a2_star = (self.r_a + sqrt_D) / (2 * self.k)

            # Growth rate parameter (vypocet.txt line 217, 225)
            # λ = k·(a₂* - a₁*)
            self.lambda_param = self.k * (self.a2_star - self.a1_star)

            # Integration constant C₀ (vypocet.txt line 267-269)
            # C₀ = (a₀ - a₁*) / (a₀ - a₂*)
            denominator = self.a_0 - self.a2_star
            if abs(denominator) < 1e-12:
                # Initial condition exactly at upper equilibrium
                self.C_0 = 1e10  # Effectively infinity
            else:
                self.C_0 = (self.a_0 - self.a1_star) / denominator

            self.valid_solution = True
        else:
            # D < 0: No real equilibrium points (vypocet.txt line 147)
            self.a1_star = None
            self.a2_star = None
            self.lambda_param = None
            self.C_0 = None
            self.valid_solution = False

    def compute_a_t(self, t: float) -> float:
        """
        Compute a(t) using exact analytical formula from vypocet.txt.

        Formula (vypocet.txt lines 250-261):
            a(t) = (a₁* - a₂*·C₀·exp(λt)) / (1 - C₀·exp(λt))

        Args:
            t: time value

        Returns:
            Activator concentration a(t)
        """
        if not self.valid_solution:
            # Fallback: numerical integration (not in vypocet.txt, emergency only)
            return self._numerical_fallback(t)

        # Compute exp(λt) once (vypocet.txt line 225)
        exp_term = np.exp(self.lambda_param * t)

        # Numerator: a₁* - a₂*·C₀·exp(λt)  (vypocet.txt line 255-256)
        numerator = self.a1_star - self.a2_star * self.C_0 * exp_term

        # Denominator: 1 - C₀·exp(λt)  (vypocet.txt line 259-260)
        denominator = 1 - self.C_0 * exp_term

        # Check for division by zero (singularity)
        if abs(denominator) < 1e-12:
            # At singularity, a(t) → ∞ (theoretically)
            # Clamp to large value for numerical stability
            return 1e6

        # Final formula (vypocet.txt line 251-261)
        a_t = numerator / denominator

        return a_t

    def _numerical_fallback(self, t: float) -> float:
        """
        Emergency fallback: Euler integration when D < 0.
        This is NOT in vypocet.txt and should be avoided.
        """
        a = self.a_0
        dt_internal = 0.001
        steps = int(t / dt_internal)

        for _ in range(steps):
            # da/dt = k·a² - r_a·a + b_a
            da_dt = self.k * a**2 - self.r_a * a + self.b_a
            a += da_dt * dt_internal

            # Prevent runaway
            if a > 1e6 or a < -1e6:
                break

        return a

    def simulate(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate time series a(t) over [0, t_max].

        Returns:
            (t_values, a_values): Arrays of time points and corresponding a(t)
        """
        # Create time array
        t_values = np.arange(0, self.t_max + self.dt, self.dt)

        # Compute a(t) for each time point using analytical formula
        a_values = np.array([self.compute_a_t(t) for t in t_values])

        return t_values, a_values

    def generate_verification_file(self, output_dir: str = ".") -> str:
        """
        Generate vypocet_output.txt for manual verification.

        This file contains:
        - All input parameters
        - Derived quantities (k, D, a₁*, a₂*, λ, C₀)
        - Time series data for manual checking

        Args:
            output_dir: Directory to save the file

        Returns:
            Path to generated file
        """
        output_path = os.path.join(output_dir, "vypocet_output.txt")

        t_values, a_values = self.simulate()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("OSCILAČNÍ VLNY - Verifikační výstup\n")
            f.write("=" * 80 + "\n\n")

            f.write("VSTUPNÍ PARAMETRY (z vypocet.txt):\n")
            f.write("-" * 80 + "\n")
            for key, value in self.params.items():
                f.write(f"  {key:10s} = {value:12.6f}\n")
            f.write("\n")

            f.write("ODVOZENÉ VELIČINY:\n")
            f.write("-" * 80 + "\n")
            f.write(f"  k (s/(s_b+b₀))       = {self.k:12.6f}\n")
            f.write(f"  D (r_a² - 4kb_a)     = {self.D:12.6f}\n")

            if self.valid_solution:
                f.write(f"  √D                    = {np.sqrt(self.D):12.6f}\n")
                f.write(f"  a₁* (dolní rovnováha) = {self.a1_star:12.6f}\n")
                f.write(f"  a₂* (horní rovnováha) = {self.a2_star:12.6f}\n")
                f.write(f"  λ = k(a₂*-a₁*)        = {self.lambda_param:12.6f}\n")
                f.write(f"  C₀ = (a₀-a₁*)/(a₀-a₂*)= {self.C_0:12.6f}\n")
            else:
                f.write("  POZOR: D < 0 → žádné reálné rovnovážné body!\n")
                f.write("         (viz vypocet.txt řádek 147)\n")
            f.write("\n")

            f.write("ANALYTICKÉ ŘEŠENÍ:\n")
            f.write("-" * 80 + "\n")
            if self.valid_solution:
                f.write("  a(t) = (a₁* - a₂*·C₀·exp(λt)) / (1 - C₀·exp(λt))\n")
                f.write("  (viz vypocet.txt řádky 250-261)\n")
            else:
                f.write("  Použita numerická integrace (D < 0)\n")
            f.write("\n")

            f.write("ČASOVÝ PRŮBĚH:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'t':>10s}  {'a(t)':>15s}  {'da/dt':>15s}\n")
            f.write("-" * 80 + "\n")

            for t, a in zip(t_values, a_values):
                # Calculate derivative for verification
                # da/dt = k·a² - r_a·a + b_a
                da_dt = self.k * a**2 - self.r_a * a + self.b_a

                f.write(f"{t:10.3f}  {a:15.8f}  {da_dt:15.8e}\n")

            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("ASYMPTOTICKÉ CHOVÁNÍ (vypocet.txt řádek 273):\n")
            f.write("=" * 80 + "\n")
            if self.valid_solution:
                f.write(f"  t → ∞: a(t) → a₁* = {self.a1_star:.6f}\n")
                final_value = a_values[-1]
                error = abs(final_value - self.a1_star) / self.a1_star * 100
                f.write(f"  a(t_max={self.t_max}) = {final_value:.6f}\n")
                f.write(f"  Relativní chyba: {error:.2f}%\n")
            f.write("\n")

        return output_path

    def get_equilibrium_info(self) -> Dict:
        """
        Get equilibrium point analysis for frontend display.

        Returns:
            Dictionary with equilibrium information
        """
        if self.valid_solution:
            return {
                'valid': True,
                'discriminant': self.D,
                'a1_star': self.a1_star,
                'a2_star': self.a2_star,
                'lambda': self.lambda_param,
                'C_0': self.C_0,
                'message': f"Dva rovnovážné body: a₁*={self.a1_star:.4f}, a₂*={self.a2_star:.4f}"
            }
        else:
            return {
                'valid': False,
                'discriminant': self.D,
                'message': f"D={self.D:.4f} < 0: Žádné reálné rovnovážné body (nestabilní systém)"
            }


def simulate_oscillatory_waves(params: Dict[str, float]) -> Dict:
    """
    Main entry point for oscillatory waves simulation.

    Follows EXACT methodology from vypocet.txt.

    Args:
        params: Physical parameters dictionary

    Returns:
        Dictionary containing:
            - t_values: time points
            - a_values: activator concentration a(t)
            - equilibrium_info: analysis of equilibrium points
            - verification_file: path to vypocet_output.txt
    """
    # Initialize calculator with exact equations from vypocet.txt
    calculator = OscillatoryWavesCalculator(params)

    # Generate analytical solution
    t_values, a_values = calculator.simulate()

    # Generate verification file for manual checking
    verification_file = calculator.generate_verification_file()

    # Get equilibrium analysis
    equilibrium_info = calculator.get_equilibrium_info()

    return {
        't_values': t_values.tolist(),
        'a_values': a_values.tolist(),
        'equilibrium_info': equilibrium_info,
        'verification_file': verification_file,
        'parameters': params
    }


# Example usage for testing
if __name__ == '__main__':
    import sys
    import io
    # Fix encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Test parameters (biologically plausible values)
    test_params = {
        's': 0.11,       # autocatalysis strength
        's_b': 1.0,      # inhibitor baseline
        'b_0': 1.0,      # inhibitor concentration
        'r_a': 0.10,     # activator decay
        'b_a': 0.01,     # activator baseline production
        'a_0': 0.5,      # initial activator concentration
        't_max': 100.0,  # simulation time
        'dt': 0.5        # output time step
    }

    print("Testing Oscillatory Waves Calculator")
    print("=" * 80)

    result = simulate_oscillatory_waves(test_params)

    print(f"\nEquilibrium info: {result['equilibrium_info']['message']}")
    print(f"Verification file: {result['verification_file']}")
    print(f"\nFirst 10 time points:")
    for i in range(min(10, len(result['t_values']))):
        t = result['t_values'][i]
        a = result['a_values'][i]
        print(f"  t={t:6.2f}, a(t)={a:10.6f}")
