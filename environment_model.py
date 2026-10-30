"""
environment_model.py — EcoPilot Phase 2: Environmental Physics Module
=====================================================================

Implements atmospheric physics and dynamic aerodynamic effects on an autonomous
drone operating in the Imphal Valley (Mantripukhri, Manipur).

Every formula is documented with its mathematical formulation and physical SI units
for full report traceability and grading compliance.

Formulas implemented:
  1. Virtual Temperature:  Tv = T * (1 + 0.61 * w)                      [K]
  2. Air Density:          rho = P / (Rd * Tv)                          [kg/m^3]
  3. Thrust Compensation:  k_thrust = rho0 / rho                        [-]
  4. Wind Decomposition:   W_along = |W| * cos(theta_w - psi)           [m/s]
                           W_cross = |W| * sin(theta_w - psi)           [m/s]
  5. Dynamic Pressure:     q = 0.5 * rho * v_rel^2                      [Pa]
  6. Environmental Risk:   R_env = w1*norm(|W|) + w2*norm(sigma_w^2) +
                                   w3*norm(|dP/dt|) + w4*norm(|rho-rho0|/rho0)  [0, 1]
  7. Adaptive Penalty:     lambda(R_env) = lambda0 * (1 + beta * R_env^2) [-]
"""

from __future__ import annotations

import json
import math
import os
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# Physical Constants (SI Units)
# ──────────────────────────────────────────────────────────────────────────────
RD_DRY_AIR: float = 287.05       # Specific gas constant for dry air [J / (kg * K)]
RHO_0_STANDARD: float = 1.225    # Standard sea-level air density [kg / m^3]
KELVIN_OFFSET: float = 273.15    # 0 degrees Celsius in Kelvin [K]
DEFAULT_Q_MAX: float = 120.0     # Maximum allowable dynamic pressure threshold [Pa]


@dataclass
class AtmosphericState:
    """Represents a discrete atmospheric state snapshot at the drone's position."""
    temperature_k: float        # Ambient temperature [K]
    pressure_pa: float          # Ambient atmospheric pressure [Pa]
    relative_humidity: float    # Relative humidity as fraction in [0.0, 1.0] [-]
    wind_speed: float           # Wind speed magnitude |W| [m/s]
    wind_direction_rad: float   # Wind azimuth theta_w (direction from which wind blows) [rad]
    gust_variance: float = 0.0  # Wind turbulence variance sigma_w^2 [m^2 / s^2]
    pressure_trend_hpa_h: float = 0.0  # Barometric pressure time rate of change dP/dt [hPa / h]


@dataclass
class EnvironmentalRiskWeights:
    """Weights for the composite environmental risk score R_env."""
    w_wind: float = 0.40      # Weight for sustained wind speed
    w_gust: float = 0.25      # Weight for gust variance / turbulence
    w_pressure: float = 0.20  # Weight for barometric pressure change rate (storm indicator)
    w_density: float = 0.15   # Weight for air density deviation from standard sea-level


# ──────────────────────────────────────────────────────────────────────────────
# 1. Atmospheric Physics Calculations
# ──────────────────────────────────────────────────────────────────────────────

def saturation_vapor_pressure(temperature_k: float) -> float:
    """
    Computes the saturation vapor pressure e_s over liquid water using the
    Magnus-Tetens empirical equation.

    Formula:
        T_c = T_k - 273.15                                    [deg C]
        e_s(T_c) = 610.78 * exp((17.27 * T_c) / (T_c + 237.3)) [Pa]

    Args:
        temperature_k: Ambient absolute temperature [K].

    Returns:
        Saturation vapor pressure e_s [Pa].
    """
    temp_c = temperature_k - KELVIN_OFFSET
    # Magnus-Tetens parameterization
    e_sat = 610.78 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    return float(e_sat)


def vapor_pressure(temperature_k: float, relative_humidity: float) -> float:
    """
    Computes actual water vapor partial pressure e from relative humidity.

    Formula:
        e = RH * e_s(T)  [Pa]

    Args:
        temperature_k: Ambient temperature [K].
        relative_humidity: Fractional relative humidity in [0.0, 1.0] [-].

    Returns:
        Water vapor partial pressure e [Pa].
    """
    rh_clamped = max(0.0, min(1.0, relative_humidity))
    e_sat = saturation_vapor_pressure(temperature_k)
    return float(rh_clamped * e_sat)


def water_vapor_mixing_ratio(
    temperature_k: float,
    pressure_pa: float,
    relative_humidity: float
) -> float:
    """
    Computes the dimensionless water vapor mixing ratio w (mass of water vapor
    per unit mass of dry air).

    Formula:
        e = vapor_pressure(T, RH)                      [Pa]
        w = 0.622 * e / (P - e)                        [kg / kg]

    Args:
        temperature_k: Ambient temperature [K].
        pressure_pa: Total barometric atmospheric pressure [Pa].
        relative_humidity: Fractional relative humidity in [0.0, 1.0] [-].

    Returns:
        Mixing ratio w [kg / kg].
    """
    e = vapor_pressure(temperature_k, relative_humidity)
    dry_pressure = max(1.0, pressure_pa - e)
    w = 0.622 * (e / dry_pressure)
    return float(max(0.0, w))


def virtual_temperature(temperature_k: float, mixing_ratio: float) -> float:
    """
    Computes virtual temperature Tv — the temperature at which dry air would
    have the same density and pressure as moist air.

    Formula:
        Tv = T * (1 + 0.61 * w)  [K]

    Args:
        temperature_k: Ambient absolute temperature T [K].
        mixing_ratio: Water vapor mixing ratio w [kg / kg].

    Returns:
        Virtual temperature Tv [K].
    """
    tv = temperature_k * (1.0 + 0.61 * mixing_ratio)
    return float(tv)


def air_density(
    temperature_k: float,
    pressure_pa: float,
    relative_humidity: float
) -> float:
    """
    Computes moist air density rho using the virtual temperature correction
    and the ideal gas law.

    Formula:
        w = mixing_ratio(T, P, RH)                     [kg / kg]
        Tv = T * (1 + 0.61 * w)                        [K]
        rho = P / (Rd * Tv)                            [kg / m^3]
        where Rd = 287.05 J / (kg * K)

    Args:
        temperature_k: Ambient temperature [K].
        pressure_pa: Atmospheric barometric pressure [Pa].
        relative_humidity: Relative humidity in range [0.0, 1.0] [-].

    Returns:
        Air density rho [kg / m^3].
    """
    w = water_vapor_mixing_ratio(temperature_k, pressure_pa, relative_humidity)
    tv = virtual_temperature(temperature_k, w)
    rho = pressure_pa / (RD_DRY_AIR * tv)
    return float(rho)


# ──────────────────────────────────────────────────────────────────────────────
# 2. Aerodynamic Interactions
# ──────────────────────────────────────────────────────────────────────────────

def thrust_compensation(rho: float, rho0: float = RHO_0_STANDARD) -> float:
    """
    Calculates the thrust compensation factor k_thrust required to produce
    equivalent hover lift in lower-density air.

    Formula:
        k_thrust = rho0 / rho  [-]

    Physical rationale:
        Rotor blade aerodynamic lift scales linearly with air density (L = Cl * 0.5 * rho * v^2 * A).
        At lower densities (high altitude, heat, humidity), the propulsion system
        must spin faster or consume more current to maintain steady hover.

    Args:
        rho: Local air density [kg / m^3].
        rho0: Reference standard sea-level density (default 1.225) [kg / m^3].

    Returns:
        Compensation scalar k_thrust [-].
    """
    rho_safe = max(0.1, rho)
    return float(rho0 / rho_safe)


def wind_components(
    wind_speed: float,
    wind_direction_rad: float,
    drone_heading_rad: float
) -> Tuple[float, float]:
    """
    Decomposes the ambient horizontal wind vector into along-track (head/tail)
    and cross-track (lateral drift) components relative to the drone's heading.

    Formulas:
        delta = theta_w - psi                         [rad]
        W_along = |W| * cos(delta)                    [m/s]
        W_cross = |W| * sin(delta)                    [m/s]

    Conventions:
        - theta_w: direction wind is blowing FROM [rad]
        - psi: drone course / heading angle [rad]
        - W_along > 0: Tailwind pushing drone forward
        - W_along < 0: Headwind resisting drone motion
        - W_cross > 0: Crosswind pushing to the right
        - W_cross < 0: Crosswind pushing to the left

    Args:
        wind_speed: Wind magnitude |W| [m/s].
        wind_direction_rad: Wind vector azimuth theta_w [rad].
        drone_heading_rad: Drone heading / forward direction psi [rad].

    Returns:
        Tuple of (W_along, W_cross) in [m/s].
    """
    delta = wind_direction_rad - drone_heading_rad
    w_along = wind_speed * math.cos(delta)
    w_cross = wind_speed * math.sin(delta)
    return float(w_along), float(w_cross)


def dynamic_pressure(
    rho: float,
    relative_airspeed: float,
    q_max: float = DEFAULT_Q_MAX
) -> Tuple[float, bool]:
    """
    Calculates the aerodynamic dynamic pressure (gust loading) on the airframe.

    Formula:
        q = 0.5 * rho * v_rel^2  [Pa]
        is_gust_critical = (q > q_max)

    Args:
        rho: Local air density [kg / m^3].
        relative_airspeed: Drone airspeed relative to surrounding moving air v_rel [m/s].
        q_max: Critical dynamic pressure limit [Pa] (default 120.0 Pa).

    Returns:
        Tuple of (dynamic_pressure q [Pa], is_gust_critical [bool]).
    """
    q = 0.5 * rho * (relative_airspeed ** 2)
    is_critical = bool(q > q_max)
    return float(q), is_critical


def compute_relative_airspeed(
    ground_velocity_mps: Tuple[float, float, float],
    wind_speed_mps: float,
    wind_dir_rad: float,
) -> float:
    """
    Computes aerodynamic relative airspeed magnitude from actual ground velocity
    and ambient wind vector:
        air_velocity = ground_velocity - wind_velocity
        airspeed = |air_velocity|

    Conventions:
        - ground_velocity: (vx, vy, vz) in world frame [East, North, Up] in m/s.
        - wind_dir_rad: azimuth theta_w wind is blowing FROM [rad] (0=North, pi/2=East).
        - wind_velocity: w_x = -wind_speed * sin(wind_dir), w_y = -wind_speed * cos(wind_dir).
        - air_velocity: (vx_g - w_x, vy_g - w_y, vz_g).

    Args:
        ground_velocity_mps: 3D ground velocity vector (vx, vy, vz) [m/s].
        wind_speed_mps: Sustained ambient wind speed [m/s].
        wind_dir_rad: Wind vector origin azimuth [rad].

    Returns:
        Scalar relative airspeed v_rel in [m/s].
    """
    vx_g, vy_g, vz_g = ground_velocity_mps
    w_x = -wind_speed_mps * math.sin(wind_dir_rad)
    w_y = -wind_speed_mps * math.cos(wind_dir_rad)
    v_air_x = vx_g - w_x
    v_air_y = vy_g - w_y
    v_air_z = vz_g
    return float(math.sqrt(v_air_x ** 2 + v_air_y ** 2 + v_air_z ** 2))


# ──────────────────────────────────────────────────────────────────────────────
# 3. Composite Environmental Risk Score & Adaptive Reward Factor
# ──────────────────────────────────────────────────────────────────────────────

def calculate_R_env(
    wind_speed: float,
    gust_variance: float,
    dP_dt_hpa_h: float,
    rho: float,
    weights: Optional[EnvironmentalRiskWeights] = None,
    rho0: float = RHO_0_STANDARD
) -> float:
    """
    Calculates the composite Environmental Risk Score R_env in [0.0, 1.0].

    Combines 4 normalized physical stressors:
      1. Sustained wind speed |W| (threshold: 15 m/s, ~54 km/h)
      2. Gust variance sigma_w^2 (threshold: 5.0 m^2/s^2)
      3. Barometric pressure trend |dP/dt| (threshold: 3.0 hPa/h, indicates storm front)
      4. Density deviation |rho - rho0| / rho0 (threshold: 0.15, ~15% deviation)

    Formula:
        R_env = w1*norm(|W|) + w2*norm(sigma_w^2) + w3*norm(|dP/dt|) + w4*norm(|rho-rho0|/rho0)

    Args:
        wind_speed: Sustained wind magnitude |W| [m/s].
        gust_variance: Wind turbulence variance sigma_w^2 [m^2 / s^2].
        dP_dt_hpa_h: Rate of barometric pressure change dP/dt [hPa / h].
        rho: Current moist air density [kg / m^3].
        weights: Custom EnvironmentalRiskWeights or None for defaults.
        rho0: Reference standard sea-level density [kg / m^3].

    Returns:
        Composite risk score R_env normalized to [0.0, 1.0].
    """
    if weights is None:
        weights = EnvironmentalRiskWeights()

    # Upper thresholds for normalization
    W_MAX = 15.0         # [m/s]
    GUST_VAR_MAX = 5.0   # [m^2 / s^2]
    DP_DT_MAX = 3.0      # [hPa / h]
    RHO_DEV_MAX = 0.15   # [-]

    # Individual normalized components clamped to [0, 1]
    norm_wind = max(0.0, min(1.0, abs(wind_speed) / W_MAX))
    norm_gust = max(0.0, min(1.0, abs(gust_variance) / GUST_VAR_MAX))
    norm_pressure = max(0.0, min(1.0, abs(dP_dt_hpa_h) / DP_DT_MAX))

    rho_rel_diff = abs(rho - rho0) / rho0
    norm_density = max(0.0, min(1.0, rho_rel_diff / RHO_DEV_MAX))

    # Weighted sum
    r_env = (
        weights.w_wind * norm_wind
        + weights.w_gust * norm_gust
        + weights.w_pressure * norm_pressure
        + weights.w_density * norm_density
    )

    return float(max(0.0, min(1.0, r_env)))


def calculate_R_env_from_state(
    state: AtmosphericState,
    weights: Optional[EnvironmentalRiskWeights] = None
) -> float:
    """Convenience helper computing R_env directly from an AtmosphericState instance."""
    rho = air_density(state.temperature_k, state.pressure_pa, state.relative_humidity)
    return calculate_R_env(
        wind_speed=state.wind_speed,
        gust_variance=state.gust_variance,
        dP_dt_hpa_h=state.pressure_trend_hpa_h,
        rho=rho,
        weights=weights
    )


def adaptive_lambda(
    r_env: float,
    lambda0: float = 1.0,
    beta: float = 3.0
) -> float:
    """
    Computes the adaptive risk penalty multiplier lambda(R_env).

    Formula:
        lambda(R_env) = lambda0 * (1 + beta * R_env^2)  [-]

    Physical behavior:
        - Calm conditions (R_env -> 0): lambda -> lambda0 (1.0)
          Agent focuses on shortest path and task progress.
        - Hazardous conditions (R_env -> 1): lambda -> lambda0 * (1 + beta) (4.0)
          Agent strongly prioritizes risk aversion and safe corridors.

    Args:
        r_env: Environmental risk score in [0.0, 1.0] [-].
        lambda0: Base baseline risk coefficient [-] (default 1.0).
        beta: Environmental scaling sensitivity parameter [-] (default 3.0).

    Returns:
        Adaptive penalty multiplier lambda [-].
    """
    r_clamped = max(0.0, min(1.0, r_env))
    return float(lambda0 * (1.0 + beta * (r_clamped ** 2)))


# ──────────────────────────────────────────────────────────────────────────────
# 3b. Energy Dynamics & Battery Physics
# ──────────────────────────────────────────────────────────────────────────────

NOMINAL_HOVER_POWER_W: float = 180.0    # Baseline hover electrical power at standard rho0 [W]
AVIONICS_BASE_POWER_W: float = 15.0     # Flight computer, GNSS, telemetry base load [W]
DRONE_MASS_KG: float = 1.5              # Total flight mass of quadrotor [kg]
GRAVITY_MPS2: float = 9.80665           # Gravitational acceleration constant [m/s^2]
BATTERY_CAPACITY_WH: float = 75.0       # 4S 5000 mAh LiPo nominal pack capacity [W * h]
AERODYNAMIC_DRAG_COEFF: float = 0.08    # Lumped parasitic aerodynamic drag coefficient [N / (m/s)^2]


def battery_power_consumption(
    rho: float,
    airspeed_mps: float,
    vertical_speed_mps: float = 0.0,
    is_hover: bool = False,
    rho0: float = RHO_0_STANDARD,
) -> float:
    """
    Computes total electrical power draw from the battery considering air density,
    aerodynamic parasitic drag, and vertical climb power.

    Formulas:
        k_thrust = rho0 / rho                                            [-]
        P_hover = k_thrust * P_hover0                                    [W]
        P_drag = c_drag * airspeed^3                                     [W]
        P_climb = max(0.0, m * g * v_z)                                  [W]
        P_total = P_avionics + P_hover + P_drag + P_climb               [W]

    Args:
        rho: Ambient moist air density [kg / m^3].
        airspeed_mps: Relative airspeed through the air mass [m/s].
        vertical_speed_mps: Vertical ascent/descent rate [m/s] (positive = climb).
        is_hover: Whether the drone is maintaining position without translational airspeed.
        rho0: Reference standard air density [kg / m^3].

    Returns:
        Total electrical power consumption P_total in Watts [W].
    """
    k_th = thrust_compensation(rho, rho0)
    p_hover = k_th * NOMINAL_HOVER_POWER_W

    if is_hover:
        p_drag = 0.0
    else:
        p_drag = AERODYNAMIC_DRAG_COEFF * (max(0.0, airspeed_mps) ** 3)

    p_climb = max(0.0, DRONE_MASS_KG * GRAVITY_MPS2 * vertical_speed_mps)

    p_total = AVIONICS_BASE_POWER_W + p_hover + p_drag + p_climb
    return float(p_total)


def compute_soc_drain(
    power_watts: float,
    duration_seconds: float,
    battery_capacity_wh: float = BATTERY_CAPACITY_WH
) -> float:
    """
    Computes battery State of Charge (SoC) drain percentage over a time delta.

    Formula:
        energy_used_wh = power_watts * (duration_seconds / 3600.0)       [W * h]
        soc_drain_pct = (energy_used_wh / battery_capacity_wh) * 100.0   [%]

    Args:
        power_watts: Total electrical power draw [W].
        duration_seconds: Elapsed duration in seconds [s].
        battery_capacity_wh: Total battery pack energy capacity [W * h].

    Returns:
        State of charge percentage drain in [0.0, 100.0] [%].
    """
    energy_wh = power_watts * (duration_seconds / 3600.0)
    drain_pct = (energy_wh / max(1.0, battery_capacity_wh)) * 100.0
    return float(max(0.0, drain_pct))


def compute_3d_kinematic_drift(
    commanded_velocity_mps: Tuple[float, float, float],
    wind_speed_mps: float,
    wind_dir_rad: float,
    drift_coupling_factor: float = 0.35,
) -> Tuple[float, float, float]:
    """
    Computes effective 3D ground velocity accounting for wind vector drift coupling.

    Formulas:
        W_x = -wind_speed * sin(wind_dir)                                [m/s]
        W_y = -wind_speed * cos(wind_dir)                                [m/s]
        v_ground_x = v_cmd_x + gamma_drift * W_x                         [m/s]
        v_ground_y = v_cmd_y + gamma_drift * W_y                         [m/s]
        v_ground_z = v_cmd_z                                             [m/s]

    Args:
        commanded_velocity_mps: Commanded velocity tuple (vx, vy, vz) [m/s].
        wind_speed_mps: Sustained wind speed [m/s].
        wind_dir_rad: Wind vector origin azimuth theta_w [rad].
        drift_coupling_factor: Aero coupling scalar gamma in [0.0, 1.0] [-].

    Returns:
        Effective ground velocity tuple (vx_g, vy_g, vz_g) [m/s].
    """
    vx_cmd, vy_cmd, vz_cmd = commanded_velocity_mps
    # Wind vector blowing direction is opposite of origin angle theta_w
    # By convention: 0 = North (from North -> blows South: -y), pi/2 = East (from East -> blows West: -x)
    w_x = -wind_speed_mps * math.sin(wind_dir_rad)
    w_y = -wind_speed_mps * math.cos(wind_dir_rad)

    vx_ground = vx_cmd + (drift_coupling_factor * w_x)
    vy_ground = vy_cmd + (drift_coupling_factor * w_y)
    vz_ground = vz_cmd

    return float(vx_ground), float(vy_ground), float(vz_ground)



# ──────────────────────────────────────────────────────────────────────────────
# 4. Reference Live Weather Acquisition (Open-Meteo API)
# ──────────────────────────────────────────────────────────────────────────────

def fetch_live_weather_snapshot(
    lat: float = 24.8491,
    lon: float = 93.9372,
    save_path: Optional[str] = None
) -> Optional[Dict]:
    """
    Fetches a real-time weather snapshot for Mantripukhri (Imphal West) via
    the free Open-Meteo REST API (no API key required).

    Grounds the simulation with real measured local atmospheric conditions.

    Args:
        lat: Latitude of Mantripukhri (default 24.8491).
        lon: Longitude of Mantripukhri (default 93.9372).
        save_path: Optional file path to persist the reference JSON snapshot.

    Returns:
        Dictionary with parsed atmospheric parameters and derived physics,
        or None if network request is unavailable.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current="
        f"temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m"
    )

    print(f"[weather] Querying live atmospheric observation for Mantripukhri ({lat}, {lon}) …")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EcoPilot-Drone-Sim/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        current = data.get("current", {})
        temp_c = current.get("temperature_2m", 25.0)
        temp_k = temp_c + KELVIN_OFFSET
        pressure_hpa = current.get("surface_pressure", 925.0)
        pressure_pa = pressure_hpa * 100.0  # hPa to Pa
        rh_pct = current.get("relative_humidity_2m", 60.0)
        rh_frac = rh_pct / 100.0
        wind_speed_kmh = current.get("wind_speed_10m", 10.0)
        wind_speed_mps = wind_speed_kmh / 3.6  # km/h to m/s
        wind_dir_deg = current.get("wind_direction_10m", 180.0)
        wind_dir_rad = math.radians(wind_dir_deg)

        # Estimate gust variance from reported wind gusts
        wind_gusts_kmh = current.get("wind_gusts_10m", wind_speed_kmh * 1.3)
        wind_gusts_mps = wind_gusts_kmh / 3.6
        gust_diff = max(0.0, wind_gusts_mps - wind_speed_mps)
        gust_var = gust_diff ** 2

        # Derived physics metrics
        rho = air_density(temp_k, pressure_pa, rh_frac)
        k_thrust = thrust_compensation(rho)
        r_env = calculate_R_env(
            wind_speed=wind_speed_mps,
            gust_variance=gust_var,
            dP_dt_hpa_h=0.0,
            rho=rho
        )
        l_factor = adaptive_lambda(r_env)

        snapshot = {
            "location": "Mantripukhri, Imphal West, Manipur, India",
            "coordinates": {"latitude": lat, "longitude": lon},
            "timestamp": current.get("time", "unknown"),
            "measured": {
                "temperature_degC": temp_c,
                "temperature_K": round(temp_k, 2),
                "surface_pressure_hPa": pressure_hpa,
                "surface_pressure_Pa": round(pressure_pa, 1),
                "relative_humidity_pct": rh_pct,
                "wind_speed_mps": round(wind_speed_mps, 2),
                "wind_direction_deg": wind_dir_deg,
                "wind_gusts_mps": round(wind_gusts_mps, 2),
            },
            "derived_physics": {
                "air_density_kg_m3": round(rho, 4),
                "thrust_compensation_factor": round(k_thrust, 4),
                "environmental_risk_R_env": round(r_env, 4),
                "adaptive_lambda": round(l_factor, 4)
            }
        }

        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            with open(save_path, "w") as f:
                json.dump(snapshot, f, indent=2)
            print(f"[weather] Saved live reference snapshot → {save_path}")

        return snapshot

    except Exception as exc:
        print(f"[weather] Live fetch failed ({exc}). Using offline reference model.")
        # Grounded climatological baseline for Mantripukhri (elevation ~780m ASL, typical afternoon)
        temp_c = 24.0
        temp_k = temp_c + KELVIN_OFFSET
        pressure_hpa = 925.0
        pressure_pa = pressure_hpa * 100.0
        rh_pct = 65.0
        rh_frac = rh_pct / 100.0
        wind_speed_mps = 3.2
        wind_dir_deg = 190.0
        wind_gusts_mps = 4.8
        gust_var = (wind_gusts_mps - wind_speed_mps) ** 2

        rho = air_density(temp_k, pressure_pa, rh_frac)
        k_thrust = thrust_compensation(rho)
        r_env = calculate_R_env(
            wind_speed=wind_speed_mps,
            gust_variance=gust_var,
            dP_dt_hpa_h=0.0,
            rho=rho
        )
        l_factor = adaptive_lambda(r_env)

        snapshot = {
            "source": "Local Climatological Baseline (Mantripukhri, Imphal Valley)",
            "location": "Mantripukhri, Imphal West, Manipur, India",
            "coordinates": {"latitude": lat, "longitude": lon},
            "timestamp": "Climatological Reference Standard",
            "measured": {
                "temperature_degC": temp_c,
                "temperature_K": round(temp_k, 2),
                "surface_pressure_hPa": pressure_hpa,
                "surface_pressure_Pa": round(pressure_pa, 1),
                "relative_humidity_pct": rh_pct,
                "wind_speed_mps": round(wind_speed_mps, 2),
                "wind_direction_deg": wind_dir_deg,
                "wind_gusts_mps": round(wind_gusts_mps, 2),
            },
            "derived_physics": {
                "air_density_kg_m3": round(rho, 4),
                "thrust_compensation_factor": round(k_thrust, 4),
                "environmental_risk_R_env": round(r_env, 4),
                "adaptive_lambda": round(l_factor, 4)
            }
        }

        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            with open(save_path, "w") as f:
                json.dump(snapshot, f, indent=2)
            print(f"[weather] Saved offline reference snapshot → {save_path}")

        return snapshot
