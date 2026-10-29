"""
tests/test_environment_model.py — Unit Tests for EcoPilot Environmental Physics
==============================================================================

Verifies physical formulas, SI unit consistency, and monotonicity of the
composite environmental risk score R_env across calm, moderate, windy, and severe conditions.
"""

import math
import os
import sys
import unittest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from environment_model import (
    AtmosphericState,
    EnvironmentalRiskWeights,
    adaptive_lambda,
    air_density,
    dynamic_pressure,
    fetch_live_weather_snapshot,
    saturation_vapor_pressure,
    thrust_compensation,
    vapor_pressure,
    virtual_temperature,
    water_vapor_mixing_ratio,
    wind_components,
    calculate_R_env,
    calculate_R_env_from_state,
    RD_DRY_AIR,
    RHO_0_STANDARD,
    KELVIN_OFFSET,
)


class TestEnvironmentalPhysics(unittest.TestCase):
    """Test suite for atmospheric physics and aerodynamic calculations."""

    def test_standard_sea_level_dry_air_density(self):
        """Standard dry sea level conditions: T=15C (288.15K), P=101325 Pa, RH=0%."""
        temp_k = 15.0 + KELVIN_OFFSET
        pressure_pa = 101325.0
        rh = 0.0

        rho = air_density(temp_k, pressure_pa, rh)
        # Expected ISA sea-level density is ~1.2250 kg/m^3
        self.assertAlmostEqual(rho, 1.2250, delta=0.002)

    def test_moist_air_less_dense_than_dry_air(self):
        """Physics axiom: Moist air is less dense than dry air at identical T and P."""
        temp_k = 30.0 + KELVIN_OFFSET
        pressure_pa = 95000.0

        rho_dry = air_density(temp_k, pressure_pa, 0.0)
        rho_humid = air_density(temp_k, pressure_pa, 0.95)

        self.assertLess(rho_humid, rho_dry)
        # Virtual temperature must be strictly greater than thermodynamic temperature
        w = water_vapor_mixing_ratio(temp_k, pressure_pa, 0.95)
        tv = virtual_temperature(temp_k, w)
        self.assertGreater(tv, temp_k)

    def test_thrust_compensation(self):
        """Thrust compensation factor should increase as density decreases."""
        k_standard = thrust_compensation(RHO_0_STANDARD)
        self.assertAlmostEqual(k_standard, 1.0, places=4)

        # High altitude / warm valley air (lower density) requires more thrust
        low_rho = 1.05
        k_compensated = thrust_compensation(low_rho)
        self.assertGreater(k_compensated, 1.0)
        self.assertAlmostEqual(k_compensated, 1.225 / 1.05, places=4)

    def test_wind_vector_decomposition(self):
        """Test headwind, tailwind, and crosswinds against drone heading."""
        # Drone flying North (psi = 0)
        drone_heading = 0.0

        # 1. Pure North wind (blowing from North -> directly into drone face -> headwind)
        wind_from_north = 0.0
        w_along, w_cross = wind_components(10.0, wind_from_north, drone_heading)
        # In our convention, cos(0) = +1 (aligned along axis), sin(0) = 0
        self.assertAlmostEqual(w_along, 10.0, places=4)
        self.assertAlmostEqual(w_cross, 0.0, places=4)

        # 2. Pure East wind (blowing from East -> 90 deg -> crosswind)
        wind_from_east = math.pi / 2.0
        w_along, w_cross = wind_components(10.0, wind_from_east, drone_heading)
        self.assertAlmostEqual(w_along, 0.0, places=4)
        self.assertAlmostEqual(w_cross, 10.0, places=4)

    def test_dynamic_pressure_and_critical_gust(self):
        """Verify dynamic pressure formula q = 0.5 * rho * v^2 and gust threshold."""
        rho = 1.20  # kg/m^3
        v_moderate = 10.0  # m/s -> q = 0.5 * 1.2 * 100 = 60 Pa
        q_mod, is_crit_mod = dynamic_pressure(rho, v_moderate, q_max=120.0)
        self.assertAlmostEqual(q_mod, 60.0, places=3)
        self.assertFalse(is_crit_mod)

        # Severe gust relative airspeed: 16 m/s -> q = 0.5 * 1.2 * 256 = 153.6 Pa
        v_severe = 16.0
        q_sev, is_crit_sev = dynamic_pressure(rho, v_severe, q_max=120.0)
        self.assertAlmostEqual(q_sev, 153.6, places=3)
        self.assertTrue(is_crit_sev)

    def test_environmental_risk_monotonicity_across_scenarios(self):
        """
        DONE CONDITION: R_env must clearly rise monotonically from
        calm -> moderate -> windy -> severe storm conditions.
        """
        # Profile 1: Calm valley morning
        # Mild temp, stable pressure, gentle breeze (1.5 m/s), low turbulence
        calm_state = AtmosphericState(
            temperature_k=20.0 + KELVIN_OFFSET,
            pressure_pa=92500.0,
            relative_humidity=0.50,
            wind_speed=1.5,
            wind_direction_rad=0.0,
            gust_variance=0.2,
            pressure_trend_hpa_h=0.1
        )
        r_calm = calculate_R_env_from_state(calm_state)

        # Profile 2: Moderate afternoon
        # 28C, breezy (5.5 m/s), modest gusts, slight pressure decline
        mod_state = AtmosphericState(
            temperature_k=28.0 + KELVIN_OFFSET,
            pressure_pa=92200.0,
            relative_humidity=0.65,
            wind_speed=5.5,
            wind_direction_rad=math.pi / 4.0,
            gust_variance=1.5,
            pressure_trend_hpa_h=-0.8
        )
        r_moderate = calculate_R_env_from_state(mod_state)

        # Profile 3: Windy front approaching
        # 31C, strong wind (10.0 m/s), gusty (3.0 m^2/s^2), falling barometer (-1.8 hPa/h)
        windy_state = AtmosphericState(
            temperature_k=31.0 + KELVIN_OFFSET,
            pressure_pa=91500.0,
            relative_humidity=0.80,
            wind_speed=10.0,
            wind_direction_rad=math.pi / 2.0,
            gust_variance=3.2,
            pressure_trend_hpa_h=-1.9
        )
        r_windy = calculate_R_env_from_state(windy_state)

        # Profile 4: Severe storm / squall
        # Near gale wind (14.5 m/s), extreme turbulence, rapid pressure drop (-2.8 hPa/h)
        storm_state = AtmosphericState(
            temperature_k=33.0 + KELVIN_OFFSET,
            pressure_pa=90500.0,
            relative_humidity=0.92,
            wind_speed=14.5,
            wind_direction_rad=math.pi,
            gust_variance=4.8,
            pressure_trend_hpa_h=-2.9
        )
        r_storm = calculate_R_env_from_state(storm_state)

        print("\n--- R_env Scenario Progression ---")
        print(f"1. Calm Valley    : R_env = {r_calm:.4f}")
        print(f"2. Moderate Breeze: R_env = {r_moderate:.4f}")
        print(f"3. Windy Front    : R_env = {r_windy:.4f}")
        print(f"4. Severe Storm   : R_env = {r_storm:.4f}")

        # Assert strict monotonic progression
        self.assertLess(r_calm, r_moderate)
        self.assertLess(r_moderate, r_windy)
        self.assertLess(r_windy, r_storm)

        # Check expected range bounds
        self.assertLess(r_calm, 0.20)
        self.assertGreater(r_storm, 0.80)

    def test_adaptive_lambda_behavior(self):
        """Verify adaptive lambda scaling: lambda = lambda0 * (1 + beta * R_env^2)."""
        l_calm = adaptive_lambda(0.0, lambda0=1.0, beta=3.0)
        self.assertAlmostEqual(l_calm, 1.0, places=4)

        l_mid = adaptive_lambda(0.5, lambda0=1.0, beta=3.0)
        # 1.0 * (1 + 3 * 0.25) = 1.75
        self.assertAlmostEqual(l_mid, 1.75, places=4)

        l_storm = adaptive_lambda(1.0, lambda0=1.0, beta=3.0)
        # 1.0 * (1 + 3 * 1.0) = 4.0
        self.assertAlmostEqual(l_storm, 4.0, places=4)


if __name__ == "__main__":
    unittest.main()

