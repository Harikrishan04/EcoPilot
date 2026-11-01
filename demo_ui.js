/**
 * demo_ui.js — EcoPilot Phase 2 Avionics & Flight Log Replay Telemetry
 * Provides flight log data replay, altitude chart rendering, mission status tracking,
 * and dynamic benchmark visualization from empirical evaluation results.
 */

// Embedded Phase 2 Telemetry Flight Logs
const FLIGHT_LOGS = {
  calm: {"scenario": "Calm", "seed": 5001, "terminal_outcome": "success", "total_steps": 21, "simulated_flight_time_s": 42.0, "energy_consumed_wh": 4.0688, "battery_end_soc_pct": 94.57, "telemetry_history": [{"step": 0, "elapsed_time_s": 0.0, "position_3d": [12.0, 17.0, 0.4], "position_meters": [510.0, 330.0, 160.0], "velocity_mps": [0.0, 0.0, 0.0], "ground_speed_mps": 0.0, "airspeed_mps": 0.0, "heading_rad": -1.176, "terrain_clearance_norm": 0.3799, "battery_soc_pct": 100.0, "power_watts": 0.0, "energy_consumed_wh": 0.0, "r_env": 0.3164, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 1, "elapsed_time_s": 2.0, "position_3d": [12.4283, 16.5363, 0.4], "position_meters": [496.09, 317.15, 160.0], "velocity_mps": [-6.956, -6.424, 0.0], "ground_speed_mps": 9.469, "airspeed_mps": 12.248, "heading_rad": 3.927, "terrain_clearance_norm": 0.3799, "battery_soc_pct": 99.73, "power_watts": 364.26, "energy_consumed_wh": 0.2024, "r_env": 0.2194, "dynamic_pressure_pa": 81.77, "outcome": "in_flight"}, {"step": 2, "elapsed_time_s": 4.0, "position_3d": [12.3839, 15.8775, 0.4], "position_meters": [476.33, 318.48, 160.0], "velocity_mps": [-9.881, 0.665, 0.0], "ground_speed_mps": 9.904, "airspeed_mps": 10.808, "heading_rad": 4.7124, "terrain_clearance_norm": 0.3676, "battery_soc_pct": 99.49, "power_watts": 318.26, "energy_consumed_wh": 0.3792, "r_env": 0.2219, "dynamic_pressure_pa": 63.67, "outcome": "in_flight"}, {"step": 3, "elapsed_time_s": 6.0, "position_3d": [12.8134, 15.4136, 0.4], "position_meters": [462.41, 305.6, 160.0], "velocity_mps": [-6.959, -6.442, 0.0], "ground_speed_mps": 9.483, "airspeed_mps": 12.186, "heading_rad": 3.927, "terrain_clearance_norm": 0.3208, "battery_soc_pct": 99.23, "power_watts": 362.02, "energy_consumed_wh": 0.5803, "r_env": 0.217, "dynamic_pressure_pa": 80.94, "outcome": "in_flight"}, {"step": 4, "elapsed_time_s": 8.0, "position_3d": [12.7681, 14.755, 0.4], "position_meters": [442.65, 306.96, 160.0], "velocity_mps": [-9.879, 0.678, 0.0], "ground_speed_mps": 9.902, "airspeed_mps": 10.83, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2792, "battery_soc_pct": 98.99, "power_watts": 318.88, "energy_consumed_wh": 0.7575, "r_env": 0.2237, "dynamic_pressure_pa": 63.93, "outcome": "in_flight"}, {"step": 5, "elapsed_time_s": 10.0, "position_3d": [13.1942, 14.2917, 0.4], "position_meters": [428.75, 294.18, 160.0], "velocity_mps": [-6.95, -6.39, 0.0], "ground_speed_mps": 9.441, "airspeed_mps": 12.371, "heading_rad": 3.927, "terrain_clearance_norm": 0.2752, "battery_soc_pct": 98.72, "power_watts": 368.73, "energy_consumed_wh": 0.9623, "r_env": 0.224, "dynamic_pressure_pa": 83.42, "outcome": "in_flight"}, {"step": 6, "elapsed_time_s": 12.0, "position_3d": [13.1481, 13.6332, 0.4], "position_meters": [409.0, 295.56, 160.0], "velocity_mps": [-9.877, 0.69, 0.0], "ground_speed_mps": 9.901, "airspeed_mps": 10.85, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2762, "battery_soc_pct": 98.48, "power_watts": 319.44, "energy_consumed_wh": 1.1398, "r_env": 0.2253, "dynamic_pressure_pa": 64.16, "outcome": "in_flight"}, {"step": 7, "elapsed_time_s": 14.0, "position_3d": [13.5719, 13.1703, 0.4], "position_meters": [395.11, 282.84, 160.0], "velocity_mps": [-6.944, -6.357, 0.0], "ground_speed_mps": 9.414, "airspeed_mps": 12.492, "heading_rad": 3.927, "terrain_clearance_norm": 0.2675, "battery_soc_pct": 98.2, "power_watts": 373.22, "energy_consumed_wh": 1.3471, "r_env": 0.2286, "dynamic_pressure_pa": 85.06, "outcome": "in_flight"}, {"step": 8, "elapsed_time_s": 16.0, "position_3d": [13.9987, 12.7069, 0.4], "position_meters": [381.21, 270.04, 160.0], "velocity_mps": [-6.952, -6.402, 0.0], "ground_speed_mps": 9.451, "airspeed_mps": 12.328, "heading_rad": 3.927, "terrain_clearance_norm": 0.2587, "battery_soc_pct": 97.93, "power_watts": 367.16, "energy_consumed_wh": 1.5511, "r_env": 0.2224, "dynamic_pressure_pa": 82.84, "outcome": "in_flight"}, {"step": 9, "elapsed_time_s": 18.0, "position_3d": [13.9542, 12.0482, 0.4], "position_meters": [361.44, 271.37, 160.0], "velocity_mps": [-9.881, 0.667, 0.0], "ground_speed_mps": 9.903, "airspeed_mps": 10.811, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2596, "battery_soc_pct": 97.7, "power_watts": 318.35, "energy_consumed_wh": 1.728, "r_env": 0.2222, "dynamic_pressure_pa": 63.71, "outcome": "in_flight"}, {"step": 10, "elapsed_time_s": 20.0, "position_3d": [14.3839, 11.5842, 0.4], "position_meters": [347.53, 258.48, 160.0], "velocity_mps": [-6.959, -6.445, 0.0], "ground_speed_mps": 9.485, "airspeed_mps": 12.173, "heading_rad": 3.927, "terrain_clearance_norm": 0.2588, "battery_soc_pct": 97.43, "power_watts": 361.58, "energy_consumed_wh": 1.9288, "r_env": 0.2166, "dynamic_pressure_pa": 80.77, "outcome": "in_flight"}, {"step": 11, "elapsed_time_s": 22.0, "position_3d": [14.341, 10.9252, 0.4], "position_meters": [327.76, 259.77, 160.0], "velocity_mps": [-9.885, 0.643, 0.0], "ground_speed_mps": 9.906, "airspeed_mps": 10.77, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2589, "battery_soc_pct": 97.19, "power_watts": 317.22, "energy_consumed_wh": 2.1051, "r_env": 0.2189, "dynamic_pressure_pa": 63.23, "outcome": "in_flight"}, {"step": 12, "elapsed_time_s": 24.0, "position_3d": [14.7695, 10.4614, 0.4], "position_meters": [313.84, 246.92, 160.0], "velocity_mps": [-6.956, -6.426, 0.0], "ground_speed_mps": 9.47, "airspeed_mps": 12.241, "heading_rad": 3.927, "terrain_clearance_norm": 0.2589, "battery_soc_pct": 96.92, "power_watts": 363.99, "energy_consumed_wh": 2.3073, "r_env": 0.2191, "dynamic_pressure_pa": 81.67, "outcome": "in_flight"}, {"step": 13, "elapsed_time_s": 26.0, "position_3d": [14.7262, 9.8025, 0.4], "position_meters": [294.07, 248.21, 160.0], "velocity_mps": [-9.884, 0.649, 0.0], "ground_speed_mps": 9.905, "airspeed_mps": 10.781, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2589, "battery_soc_pct": 96.69, "power_watts": 317.51, "energy_consumed_wh": 2.4837, "r_env": 0.2197, "dynamic_pressure_pa": 63.35, "outcome": "in_flight"}, {"step": 14, "elapsed_time_s": 28.0, "position_3d": [15.1508, 9.3394, 0.4], "position_meters": [280.18, 235.48, 160.0], "velocity_mps": [-6.946, -6.369, 0.0], "ground_speed_mps": 9.424, "airspeed_mps": 12.448, "heading_rad": 3.927, "terrain_clearance_norm": 0.2589, "battery_soc_pct": 96.41, "power_watts": 371.57, "energy_consumed_wh": 2.6901, "r_env": 0.2269, "dynamic_pressure_pa": 84.46, "outcome": "in_flight"}, {"step": 15, "elapsed_time_s": 30.0, "position_3d": [15.5748, 8.8765, 0.4], "position_meters": [266.29, 222.76, 160.0], "velocity_mps": [-6.944, -6.361, 0.0], "ground_speed_mps": 9.417, "airspeed_mps": 12.478, "heading_rad": 3.927, "terrain_clearance_norm": 0.2577, "battery_soc_pct": 96.14, "power_watts": 372.69, "energy_consumed_wh": 2.8972, "r_env": 0.228, "dynamic_pressure_pa": 84.87, "outcome": "in_flight"}, {"step": 16, "elapsed_time_s": 32.0, "position_3d": [15.5249, 8.2187, 0.4], "position_meters": [246.56, 224.25, 160.0], "velocity_mps": [-9.867, 0.748, 0.0], "ground_speed_mps": 9.895, "airspeed_mps": 10.95, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2515, "battery_soc_pct": 95.9, "power_watts": 322.31, "energy_consumed_wh": 3.0762, "r_env": 0.2331, "dynamic_pressure_pa": 65.36, "outcome": "in_flight"}, {"step": 17, "elapsed_time_s": 34.0, "position_3d": [15.948, 7.7559, 0.4], "position_meters": [232.68, 211.56, 160.0], "velocity_mps": [-6.942, -6.347, 0.0], "ground_speed_mps": 9.406, "airspeed_mps": 12.529, "heading_rad": 3.927, "terrain_clearance_norm": 0.2495, "battery_soc_pct": 95.62, "power_watts": 374.59, "energy_consumed_wh": 3.2843, "r_env": 0.2299, "dynamic_pressure_pa": 85.56, "outcome": "in_flight"}, {"step": 18, "elapsed_time_s": 36.0, "position_3d": [15.8992, 7.098, 0.4], "position_meters": [212.94, 213.02, 160.0], "velocity_mps": [-9.869, 0.733, 0.0], "ground_speed_mps": 9.896, "airspeed_mps": 10.924, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2495, "battery_soc_pct": 95.38, "power_watts": 321.54, "energy_consumed_wh": 3.463, "r_env": 0.231, "dynamic_pressure_pa": 65.04, "outcome": "in_flight"}, {"step": 19, "elapsed_time_s": 38.0, "position_3d": [16.319, 6.6358, 0.4], "position_meters": [199.07, 200.43, 160.0], "velocity_mps": [-6.933, -6.297, 0.0], "ground_speed_mps": 9.366, "airspeed_mps": 12.707, "heading_rad": 3.927, "terrain_clearance_norm": 0.2495, "battery_soc_pct": 95.1, "power_watts": 381.4, "energy_consumed_wh": 3.6749, "r_env": 0.2366, "dynamic_pressure_pa": 88.01, "outcome": "in_flight"}, {"step": 20, "elapsed_time_s": 40.0, "position_3d": [16.7377, 6.1738, 0.4], "position_meters": [185.21, 187.87, 160.0], "velocity_mps": [-6.93, -6.28, 0.0], "ground_speed_mps": 9.352, "airspeed_mps": 12.77, "heading_rad": 3.927, "terrain_clearance_norm": 0.2495, "battery_soc_pct": 94.82, "power_watts": 383.85, "energy_consumed_wh": 3.8881, "r_env": 0.2389, "dynamic_pressure_pa": 88.88, "outcome": "in_flight"}, {"step": 21, "elapsed_time_s": 42.0, "position_3d": [16.684, 5.5167, 0.4], "position_meters": [165.5, 189.48, 160.0], "velocity_mps": [-9.856, 0.805, 0.0], "ground_speed_mps": 9.889, "airspeed_mps": 11.054, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2499, "battery_soc_pct": 94.57, "power_watts": 325.31, "energy_consumed_wh": 4.0688, "r_env": 0.2408, "dynamic_pressure_pa": 66.6, "outcome": "success"}]},
  moderate: {"scenario": "Moderate", "seed": 5002, "terminal_outcome": "success", "total_steps": 13, "simulated_flight_time_s": 26.0, "energy_consumed_wh": 1.8408, "battery_end_soc_pct": 97.55, "telemetry_history": [{"step": 0, "elapsed_time_s": 0.0, "position_3d": [15.0, 19.0, 0.4], "position_meters": [570.0, 240.0, 160.0], "velocity_mps": [0.0, 0.0, 0.0], "ground_speed_mps": 0.0, "airspeed_mps": 0.0, "heading_rad": -2.1294, "terrain_clearance_norm": 0.3775, "battery_soc_pct": 100.0, "power_watts": 0.0, "energy_consumed_wh": 0.0, "r_env": 0.4025, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 1, "elapsed_time_s": 2.0, "position_3d": [14.5279, 18.4396, 0.4], "position_meters": [553.19, 254.16, 160.0], "velocity_mps": [-8.406, 7.082, 0.0], "ground_speed_mps": 10.991, "airspeed_mps": 7.238, "heading_rad": 5.4978, "terrain_clearance_norm": 0.3529, "battery_soc_pct": 99.81, "power_watts": 253.57, "energy_consumed_wh": 0.1409, "r_env": 0.4143, "dynamic_pressure_pa": 27.74, "outcome": "in_flight"}, {"step": 2, "elapsed_time_s": 4.0, "position_3d": [14.0557, 17.8777, 0.4], "position_meters": [536.33, 268.33, 160.0], "velocity_mps": [-8.428, 7.082, 0.0], "ground_speed_mps": 11.009, "airspeed_mps": 7.216, "heading_rad": 5.4978, "terrain_clearance_norm": 0.3335, "battery_soc_pct": 99.62, "power_watts": 253.3, "energy_consumed_wh": 0.2816, "r_env": 0.4174, "dynamic_pressure_pa": 27.57, "outcome": "in_flight"}, {"step": 3, "elapsed_time_s": 6.0, "position_3d": [13.5836, 17.313, 0.4], "position_meters": [519.39, 282.49, 160.0], "velocity_mps": [-8.47, 7.082, 0.0], "ground_speed_mps": 11.041, "airspeed_mps": 7.178, "heading_rad": 5.4978, "terrain_clearance_norm": 0.3528, "battery_soc_pct": 99.44, "power_watts": 252.83, "energy_consumed_wh": 0.4221, "r_env": 0.423, "dynamic_pressure_pa": 27.28, "outcome": "in_flight"}, {"step": 4, "elapsed_time_s": 8.0, "position_3d": [13.1114, 16.7521, 0.4], "position_meters": [502.56, 296.66, 160.0], "velocity_mps": [-8.414, 7.082, 0.0], "ground_speed_mps": 10.997, "airspeed_mps": 7.23, "heading_rad": 5.4978, "terrain_clearance_norm": 0.3747, "battery_soc_pct": 99.25, "power_watts": 253.48, "energy_consumed_wh": 0.5629, "r_env": 0.4154, "dynamic_pressure_pa": 27.68, "outcome": "in_flight"}, {"step": 5, "elapsed_time_s": 10.0, "position_3d": [12.6393, 16.1922, 0.4], "position_meters": [485.77, 310.82, 160.0], "velocity_mps": [-8.399, 7.082, 0.0], "ground_speed_mps": 10.986, "airspeed_mps": 7.245, "heading_rad": 5.4978, "terrain_clearance_norm": 0.3799, "battery_soc_pct": 99.06, "power_watts": 253.66, "energy_consumed_wh": 0.7038, "r_env": 0.4135, "dynamic_pressure_pa": 27.79, "outcome": "in_flight"}, {"step": 6, "elapsed_time_s": 12.0, "position_3d": [12.1672, 15.6364, 0.4], "position_meters": [469.09, 324.98, 160.0], "velocity_mps": [-8.338, 7.081, 0.0], "ground_speed_mps": 10.939, "airspeed_mps": 7.31, "heading_rad": 5.4978, "terrain_clearance_norm": 0.3433, "battery_soc_pct": 98.87, "power_watts": 254.49, "energy_consumed_wh": 0.8452, "r_env": 0.4053, "dynamic_pressure_pa": 28.29, "outcome": "in_flight"}, {"step": 7, "elapsed_time_s": 14.0, "position_3d": [11.6951, 15.0802, 0.4], "position_meters": [452.41, 339.15, 160.0], "velocity_mps": [-8.343, 7.081, 0.0], "ground_speed_mps": 10.943, "airspeed_mps": 7.304, "heading_rad": 5.4978, "terrain_clearance_norm": 0.2873, "battery_soc_pct": 98.68, "power_watts": 254.41, "energy_consumed_wh": 0.9865, "r_env": 0.406, "dynamic_pressure_pa": 28.25, "outcome": "in_flight"}, {"step": 8, "elapsed_time_s": 16.0, "position_3d": [11.223, 14.5242, 0.4], "position_meters": [435.73, 353.31, 160.0], "velocity_mps": [-8.34, 7.081, 0.0], "ground_speed_mps": 10.941, "airspeed_mps": 7.307, "heading_rad": 5.4978, "terrain_clearance_norm": 0.2792, "battery_soc_pct": 98.5, "power_watts": 254.46, "energy_consumed_wh": 1.1279, "r_env": 0.4056, "dynamic_pressure_pa": 28.27, "outcome": "in_flight"}, {"step": 9, "elapsed_time_s": 18.0, "position_3d": [10.7509, 13.9714, 0.4], "position_meters": [419.14, 367.47, 160.0], "velocity_mps": [-8.292, 7.081, 0.0], "ground_speed_mps": 10.904, "airspeed_mps": 7.363, "heading_rad": 5.4978, "terrain_clearance_norm": 0.2792, "battery_soc_pct": 98.31, "power_watts": 255.18, "energy_consumed_wh": 1.2697, "r_env": 0.3992, "dynamic_pressure_pa": 28.71, "outcome": "in_flight"}, {"step": 10, "elapsed_time_s": 20.0, "position_3d": [10.2789, 13.423, 0.4], "position_meters": [402.69, 381.63, 160.0], "velocity_mps": [-8.226, 7.08, 0.0], "ground_speed_mps": 10.853, "airspeed_mps": 7.449, "heading_rad": 5.4978, "terrain_clearance_norm": 0.2792, "battery_soc_pct": 98.12, "power_watts": 256.3, "energy_consumed_wh": 1.412, "r_env": 0.3904, "dynamic_pressure_pa": 29.37, "outcome": "in_flight"}, {"step": 11, "elapsed_time_s": 22.0, "position_3d": [9.8069, 12.8773, 0.4], "position_meters": [386.32, 395.79, 160.0], "velocity_mps": [-8.186, 7.08, 0.0], "ground_speed_mps": 10.823, "airspeed_mps": 7.504, "heading_rad": 5.4978, "terrain_clearance_norm": 0.293, "battery_soc_pct": 97.93, "power_watts": 257.04, "energy_consumed_wh": 1.5548, "r_env": 0.3851, "dynamic_pressure_pa": 29.81, "outcome": "in_flight"}, {"step": 12, "elapsed_time_s": 24.0, "position_3d": [9.3349, 12.3302, 0.4], "position_meters": [369.91, 409.95, 160.0], "velocity_mps": [-8.206, 7.08, 0.0], "ground_speed_mps": 10.838, "airspeed_mps": 7.476, "heading_rad": 5.4978, "terrain_clearance_norm": 0.3267, "battery_soc_pct": 97.74, "power_watts": 256.67, "energy_consumed_wh": 1.6974, "r_env": 0.3877, "dynamic_pressure_pa": 29.59, "outcome": "in_flight"}, {"step": 13, "elapsed_time_s": 26.0, "position_3d": [9.8057, 11.7845, 0.4], "position_meters": [353.54, 395.83, 160.0], "velocity_mps": [-8.185, -7.062, 0.0], "ground_speed_mps": 10.811, "airspeed_mps": 7.573, "heading_rad": 3.927, "terrain_clearance_norm": 0.2834, "battery_soc_pct": 97.55, "power_watts": 257.99, "energy_consumed_wh": 1.8408, "r_env": 0.385, "dynamic_pressure_pa": 30.37, "outcome": "success"}]},
  emergency: {"scenario": "Severe", "seed": 5003, "terminal_outcome": "timeout", "total_steps": 120, "simulated_flight_time_s": 240.0, "energy_consumed_wh": 22.8253, "battery_end_soc_pct": 69.57, "telemetry_history": [{"step": 0, "elapsed_time_s": 0.0, "position_3d": [7.0, 7.0, 0.4], "position_meters": [210.0, 480.0, 160.0], "velocity_mps": [0.0, 0.0, 0.0], "ground_speed_mps": 0.0, "airspeed_mps": 0.0, "heading_rad": 1.989, "terrain_clearance_norm": 0.2777, "battery_soc_pct": 100.0, "power_watts": 0.0, "energy_consumed_wh": 0.0, "r_env": 0.5141, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 1, "elapsed_time_s": 2.0, "position_3d": [6.368, 7.4707, 0.4], "position_meters": [224.12, 498.96, 160.0], "velocity_mps": [7.06, 9.48, 0.0], "ground_speed_mps": 11.82, "airspeed_mps": 7.564, "heading_rad": 0.7854, "terrain_clearance_norm": 0.2905, "battery_soc_pct": 99.8, "power_watts": 264.4, "energy_consumed_wh": 0.1469, "r_env": 0.8309, "dynamic_pressure_pa": 29.37, "outcome": "in_flight"}, {"step": 2, "elapsed_time_s": 4.0, "position_3d": [6.2083, 8.1366, 0.4], "position_meters": [244.1, 503.75, 160.0], "velocity_mps": [9.989, 2.395, 0.0], "ground_speed_mps": 10.272, "airspeed_mps": 13.881, "heading_rad": 1.5708, "terrain_clearance_norm": 0.2971, "battery_soc_pct": 99.48, "power_watts": 443.73, "energy_consumed_wh": 0.3934, "r_env": 0.829, "dynamic_pressure_pa": 98.91, "outcome": "in_flight"}, {"step": 3, "elapsed_time_s": 6.0, "position_3d": [6.0487, 8.8025, 0.4], "position_meters": [264.07, 508.54, 160.0], "velocity_mps": [9.989, 2.394, 0.0], "ground_speed_mps": 10.272, "airspeed_mps": 13.878, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3201, "battery_soc_pct": 99.15, "power_watts": 443.62, "energy_consumed_wh": 0.6399, "r_env": 0.8289, "dynamic_pressure_pa": 98.87, "outcome": "in_flight"}, {"step": 4, "elapsed_time_s": 8.0, "position_3d": [5.4201, 9.2732, 0.4], "position_meters": [278.19, 527.4, 160.0], "velocity_mps": [7.06, 9.43, 0.0], "ground_speed_mps": 11.78, "airspeed_mps": 7.497, "heading_rad": 0.7854, "terrain_clearance_norm": 0.3282, "battery_soc_pct": 98.95, "power_watts": 263.49, "energy_consumed_wh": 0.7862, "r_env": 0.8241, "dynamic_pressure_pa": 28.85, "outcome": "in_flight"}, {"step": 5, "elapsed_time_s": 10.0, "position_3d": [5.2616, 9.9391, 0.4], "position_meters": [298.17, 532.15, 160.0], "velocity_mps": [9.989, 2.378, 0.0], "ground_speed_mps": 10.268, "airspeed_mps": 13.834, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3282, "battery_soc_pct": 98.62, "power_watts": 441.57, "energy_consumed_wh": 1.0316, "r_env": 0.8267, "dynamic_pressure_pa": 98.24, "outcome": "in_flight"}, {"step": 6, "elapsed_time_s": 12.0, "position_3d": [5.1005, 10.605, 0.4], "position_meters": [318.15, 536.99, 160.0], "velocity_mps": [9.989, 2.416, 0.0], "ground_speed_mps": 10.277, "airspeed_mps": 13.94, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3282, "battery_soc_pct": 98.29, "power_watts": 446.48, "energy_consumed_wh": 1.2796, "r_env": 0.8318, "dynamic_pressure_pa": 99.75, "outcome": "in_flight"}, {"step": 7, "elapsed_time_s": 14.0, "position_3d": [4.9395, 11.2709, 0.4], "position_meters": [338.13, 541.81, 160.0], "velocity_mps": [9.989, 2.414, 0.0], "ground_speed_mps": 10.276, "airspeed_mps": 13.935, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3442, "battery_soc_pct": 97.96, "power_watts": 446.24, "energy_consumed_wh": 1.5275, "r_env": 0.8316, "dynamic_pressure_pa": 99.68, "outcome": "in_flight"}, {"step": 8, "elapsed_time_s": 16.0, "position_3d": [4.7783, 11.9368, 0.4], "position_meters": [358.1, 546.65, 160.0], "velocity_mps": [9.989, 2.418, 0.0], "ground_speed_mps": 10.277, "airspeed_mps": 13.943, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3836, "battery_soc_pct": 97.63, "power_watts": 446.64, "energy_consumed_wh": 1.7757, "r_env": 0.832, "dynamic_pressure_pa": 99.8, "outcome": "in_flight"}, {"step": 9, "elapsed_time_s": 18.0, "position_3d": [4.146, 12.4075, 0.4], "position_meters": [372.22, 565.62, 160.0], "velocity_mps": [7.06, 9.485, 0.0], "ground_speed_mps": 11.824, "airspeed_mps": 7.571, "heading_rad": 0.7854, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 97.44, "power_watts": 264.48, "energy_consumed_wh": 1.9226, "r_env": 0.8314, "dynamic_pressure_pa": 29.42, "outcome": "in_flight"}, {"step": 10, "elapsed_time_s": 20.0, "position_3d": [4.106, 12.4073, 0.4], "position_meters": [372.22, 566.82, 160.0], "velocity_mps": [-0.003, 0.601, 0.0], "ground_speed_mps": 0.601, "airspeed_mps": 11.417, "heading_rad": 0.7854, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 97.27, "power_watts": 229.77, "energy_consumed_wh": 2.0502, "r_env": 0.8301, "dynamic_pressure_pa": 66.92, "outcome": "in_flight"}, {"step": 11, "elapsed_time_s": 22.0, "position_3d": [4.0666, 12.4071, 0.4], "position_meters": [372.21, 568.0, 160.0], "velocity_mps": [-0.003, 0.59, 0.0], "ground_speed_mps": 0.59, "airspeed_mps": 11.218, "heading_rad": 0.7854, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 97.1, "power_watts": 229.77, "energy_consumed_wh": 2.1779, "r_env": 0.8245, "dynamic_pressure_pa": 64.6, "outcome": "in_flight"}, {"step": 12, "elapsed_time_s": 24.0, "position_3d": [4.0272, 12.4069, 0.4], "position_meters": [372.21, 569.18, 160.0], "velocity_mps": [-0.003, 0.591, 0.0], "ground_speed_mps": 0.591, "airspeed_mps": 11.227, "heading_rad": 0.7854, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 96.93, "power_watts": 229.77, "energy_consumed_wh": 2.3055, "r_env": 0.8248, "dynamic_pressure_pa": 64.71, "outcome": "in_flight"}, {"step": 13, "elapsed_time_s": 26.0, "position_3d": [3.987, 12.4067, 0.4], "position_meters": [372.2, 570.39, 160.0], "velocity_mps": [-0.003, 0.604, 0.0], "ground_speed_mps": 0.604, "airspeed_mps": 11.473, "heading_rad": 0.7854, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 96.76, "power_watts": 229.77, "energy_consumed_wh": 2.4332, "r_env": 0.8317, "dynamic_pressure_pa": 67.57, "outcome": "in_flight"}, {"step": 14, "elapsed_time_s": 28.0, "position_3d": [4.2971, 11.9346, 0.4], "position_meters": [358.04, 561.09, 160.0], "velocity_mps": [-7.082, -4.652, 0.0], "ground_speed_mps": 8.474, "airspeed_mps": 18.16, "heading_rad": 3.927, "terrain_clearance_norm": 0.3835, "battery_soc_pct": 96.23, "power_watts": 708.92, "energy_consumed_wh": 2.827, "r_env": 0.8322, "dynamic_pressure_pa": 169.3, "outcome": "in_flight"}, {"step": 15, "elapsed_time_s": 30.0, "position_3d": [4.1355, 12.6005, 0.4], "position_meters": [378.01, 565.94, 160.0], "velocity_mps": [9.989, 2.424, 0.0], "ground_speed_mps": 10.279, "airspeed_mps": 13.963, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 95.9, "power_watts": 447.55, "energy_consumed_wh": 3.0757, "r_env": 0.8329, "dynamic_pressure_pa": 100.08, "outcome": "in_flight"}, {"step": 16, "elapsed_time_s": 32.0, "position_3d": [4.095, 12.6003, 0.4], "position_meters": [378.01, 567.15, 160.0], "velocity_mps": [-0.003, 0.607, 0.0], "ground_speed_mps": 0.607, "airspeed_mps": 11.538, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 95.73, "power_watts": 229.77, "energy_consumed_wh": 3.2033, "r_env": 0.8335, "dynamic_pressure_pa": 68.33, "outcome": "in_flight"}, {"step": 17, "elapsed_time_s": 34.0, "position_3d": [4.0544, 12.6001, 0.4], "position_meters": [378.0, 568.37, 160.0], "velocity_mps": [-0.003, 0.609, 0.0], "ground_speed_mps": 0.609, "airspeed_mps": 11.563, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 95.56, "power_watts": 229.77, "energy_consumed_wh": 3.331, "r_env": 0.8342, "dynamic_pressure_pa": 68.63, "outcome": "in_flight"}, {"step": 18, "elapsed_time_s": 36.0, "position_3d": [4.0133, 12.5999, 0.4], "position_meters": [378.0, 569.6, 160.0], "velocity_mps": [-0.003, 0.617, 0.0], "ground_speed_mps": 0.617, "airspeed_mps": 11.714, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 95.39, "power_watts": 229.77, "energy_consumed_wh": 3.4586, "r_env": 0.8385, "dynamic_pressure_pa": 70.44, "outcome": "in_flight"}, {"step": 19, "elapsed_time_s": 38.0, "position_3d": [3.9727, 12.5997, 0.4], "position_meters": [377.99, 570.82, 160.0], "velocity_mps": [-0.003, 0.609, 0.0], "ground_speed_mps": 0.609, "airspeed_mps": 11.576, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 95.22, "power_watts": 229.77, "energy_consumed_wh": 3.5863, "r_env": 0.8346, "dynamic_pressure_pa": 68.78, "outcome": "in_flight"}, {"step": 20, "elapsed_time_s": 40.0, "position_3d": [4.2774, 12.1275, 0.4], "position_meters": [363.83, 561.68, 160.0], "velocity_mps": [-7.083, -4.57, 0.0], "ground_speed_mps": 8.429, "airspeed_mps": 18.463, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 94.68, "power_watts": 733.23, "energy_consumed_wh": 3.9936, "r_env": 0.8431, "dynamic_pressure_pa": 174.98, "outcome": "in_flight"}, {"step": 21, "elapsed_time_s": 42.0, "position_3d": [4.1083, 12.7934, 0.4], "position_meters": [383.8, 566.75, 160.0], "velocity_mps": [9.988, 2.537, 0.0], "ground_speed_mps": 10.305, "airspeed_mps": 14.28, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 94.33, "power_watts": 462.75, "energy_consumed_wh": 4.2507, "r_env": 0.8479, "dynamic_pressure_pa": 104.68, "outcome": "in_flight"}, {"step": 22, "elapsed_time_s": 44.0, "position_3d": [4.066, 12.7932, 0.4], "position_meters": [383.8, 568.02, 160.0], "velocity_mps": [-0.003, 0.634, 0.0], "ground_speed_mps": 0.634, "airspeed_mps": 12.045, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 94.16, "power_watts": 229.77, "energy_consumed_wh": 4.3784, "r_env": 0.8477, "dynamic_pressure_pa": 74.47, "outcome": "in_flight"}, {"step": 23, "elapsed_time_s": 46.0, "position_3d": [4.0242, 12.793, 0.4], "position_meters": [383.79, 569.27, 160.0], "velocity_mps": [-0.003, 0.627, 0.0], "ground_speed_mps": 0.627, "airspeed_mps": 11.916, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 93.99, "power_watts": 229.77, "energy_consumed_wh": 4.506, "r_env": 0.8441, "dynamic_pressure_pa": 72.89, "outcome": "in_flight"}, {"step": 24, "elapsed_time_s": 48.0, "position_3d": [3.9822, 12.7928, 0.4], "position_meters": [383.78, 570.53, 160.0], "velocity_mps": [-0.003, 0.63, 0.0], "ground_speed_mps": 0.63, "airspeed_mps": 11.971, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 93.82, "power_watts": 229.77, "energy_consumed_wh": 4.6337, "r_env": 0.8457, "dynamic_pressure_pa": 73.56, "outcome": "in_flight"}, {"step": 25, "elapsed_time_s": 50.0, "position_3d": [3.9402, 12.7926, 0.4], "position_meters": [383.78, 571.79, 160.0], "velocity_mps": [-0.003, 0.63, 0.0], "ground_speed_mps": 0.63, "airspeed_mps": 11.964, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 93.65, "power_watts": 229.77, "energy_consumed_wh": 4.7613, "r_env": 0.8455, "dynamic_pressure_pa": 73.48, "outcome": "in_flight"}, {"step": 26, "elapsed_time_s": 52.0, "position_3d": [4.2445, 12.3204, 0.4], "position_meters": [369.61, 562.67, 160.0], "velocity_mps": [-7.083, -4.564, 0.0], "ground_speed_mps": 8.426, "airspeed_mps": 18.485, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 93.11, "power_watts": 735.08, "energy_consumed_wh": 5.1697, "r_env": 0.8439, "dynamic_pressure_pa": 175.4, "outcome": "in_flight"}, {"step": 27, "elapsed_time_s": 54.0, "position_3d": [4.203, 12.3202, 0.4], "position_meters": [369.61, 563.91, 160.0], "velocity_mps": [-0.003, 0.623, 0.0], "ground_speed_mps": 0.623, "airspeed_mps": 11.833, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 92.94, "power_watts": 229.77, "energy_consumed_wh": 5.2974, "r_env": 0.8418, "dynamic_pressure_pa": 71.88, "outcome": "in_flight"}, {"step": 28, "elapsed_time_s": 56.0, "position_3d": [4.1618, 12.32, 0.4], "position_meters": [369.6, 565.15, 160.0], "velocity_mps": [-0.003, 0.618, 0.0], "ground_speed_mps": 0.618, "airspeed_mps": 11.735, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 92.77, "power_watts": 229.77, "energy_consumed_wh": 5.425, "r_env": 0.8391, "dynamic_pressure_pa": 70.7, "outcome": "in_flight"}, {"step": 29, "elapsed_time_s": 58.0, "position_3d": [4.1208, 12.3198, 0.4], "position_meters": [369.59, 566.38, 160.0], "velocity_mps": [-0.003, 0.615, 0.0], "ground_speed_mps": 0.615, "airspeed_mps": 11.691, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 92.6, "power_watts": 229.77, "energy_consumed_wh": 5.5527, "r_env": 0.8378, "dynamic_pressure_pa": 70.16, "outcome": "in_flight"}, {"step": 30, "elapsed_time_s": 60.0, "position_3d": [4.0799, 12.3196, 0.4], "position_meters": [369.59, 567.6, 160.0], "velocity_mps": [-0.003, 0.614, 0.0], "ground_speed_mps": 0.614, "airspeed_mps": 11.662, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 92.43, "power_watts": 229.77, "energy_consumed_wh": 5.6803, "r_env": 0.837, "dynamic_pressure_pa": 69.81, "outcome": "in_flight"}, {"step": 31, "elapsed_time_s": 62.0, "position_3d": [4.391, 11.8475, 0.4], "position_meters": [355.42, 558.27, 160.0], "velocity_mps": [-7.082, -4.667, 0.0], "ground_speed_mps": 8.482, "airspeed_mps": 18.104, "heading_rad": 3.927, "terrain_clearance_norm": 0.3784, "battery_soc_pct": 91.9, "power_watts": 704.5, "energy_consumed_wh": 6.0717, "r_env": 0.8301, "dynamic_pressure_pa": 168.25, "outcome": "in_flight"}, {"step": 32, "elapsed_time_s": 64.0, "position_3d": [4.229, 12.5134, 0.4], "position_meters": [375.4, 563.13, 160.0], "velocity_mps": [9.989, 2.43, 0.0], "ground_speed_mps": 10.28, "airspeed_mps": 13.978, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 91.57, "power_watts": 448.24, "energy_consumed_wh": 6.3207, "r_env": 0.8336, "dynamic_pressure_pa": 100.29, "outcome": "in_flight"}, {"step": 33, "elapsed_time_s": 66.0, "position_3d": [4.1883, 12.5132, 0.4], "position_meters": [375.4, 564.35, 160.0], "velocity_mps": [-0.003, 0.611, 0.0], "ground_speed_mps": 0.611, "airspeed_mps": 11.6, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 91.4, "power_watts": 229.77, "energy_consumed_wh": 6.4484, "r_env": 0.8353, "dynamic_pressure_pa": 69.07, "outcome": "in_flight"}, {"step": 34, "elapsed_time_s": 68.0, "position_3d": [4.1471, 12.513, 0.4], "position_meters": [375.39, 565.59, 160.0], "velocity_mps": [-0.003, 0.619, 0.0], "ground_speed_mps": 0.619, "airspeed_mps": 11.767, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 91.23, "power_watts": 229.77, "energy_consumed_wh": 6.576, "r_env": 0.8399, "dynamic_pressure_pa": 71.08, "outcome": "in_flight"}, {"step": 35, "elapsed_time_s": 70.0, "position_3d": [4.1056, 12.5128, 0.4], "position_meters": [375.38, 566.83, 160.0], "velocity_mps": [-0.003, 0.621, 0.0], "ground_speed_mps": 0.621, "airspeed_mps": 11.808, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 91.06, "power_watts": 229.77, "energy_consumed_wh": 6.7037, "r_env": 0.8411, "dynamic_pressure_pa": 71.57, "outcome": "in_flight"}, {"step": 36, "elapsed_time_s": 72.0, "position_3d": [4.0637, 12.5126, 0.4], "position_meters": [375.38, 568.09, 160.0], "velocity_mps": [-0.003, 0.629, 0.0], "ground_speed_mps": 0.629, "airspeed_mps": 11.945, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 90.89, "power_watts": 229.77, "energy_consumed_wh": 6.8313, "r_env": 0.8449, "dynamic_pressure_pa": 73.24, "outcome": "in_flight"}, {"step": 37, "elapsed_time_s": 74.0, "position_3d": [4.3698, 12.0404, 0.4], "position_meters": [361.21, 558.91, 160.0], "velocity_mps": [-7.083, -4.592, 0.0], "ground_speed_mps": 8.441, "airspeed_mps": 18.384, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 90.35, "power_watts": 726.85, "energy_consumed_wh": 7.2351, "r_env": 0.8403, "dynamic_pressure_pa": 173.49, "outcome": "in_flight"}, {"step": 38, "elapsed_time_s": 76.0, "position_3d": [4.2068, 12.7063, 0.4], "position_meters": [381.19, 563.8, 160.0], "velocity_mps": [9.989, 2.446, 0.0], "ground_speed_mps": 10.284, "airspeed_mps": 14.022, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 90.02, "power_watts": 450.35, "energy_consumed_wh": 7.4853, "r_env": 0.8357, "dynamic_pressure_pa": 100.93, "outcome": "in_flight"}, {"step": 39, "elapsed_time_s": 78.0, "position_3d": [4.1667, 12.7062, 0.4], "position_meters": [381.18, 565.0, 160.0], "velocity_mps": [-0.003, 0.601, 0.0], "ground_speed_mps": 0.601, "airspeed_mps": 11.424, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 89.85, "power_watts": 229.77, "energy_consumed_wh": 7.613, "r_env": 0.8303, "dynamic_pressure_pa": 66.99, "outcome": "in_flight"}, {"step": 40, "elapsed_time_s": 80.0, "position_3d": [4.1268, 12.706, 0.4], "position_meters": [381.18, 566.19, 160.0], "velocity_mps": [-0.003, 0.598, 0.0], "ground_speed_mps": 0.598, "airspeed_mps": 11.354, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 89.68, "power_watts": 229.77, "energy_consumed_wh": 7.7406, "r_env": 0.8284, "dynamic_pressure_pa": 66.18, "outcome": "in_flight"}, {"step": 41, "elapsed_time_s": 82.0, "position_3d": [4.087, 12.7058, 0.4], "position_meters": [381.17, 567.39, 160.0], "velocity_mps": [-0.003, 0.598, 0.0], "ground_speed_mps": 0.598, "airspeed_mps": 11.369, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 89.51, "power_watts": 229.77, "energy_consumed_wh": 7.8683, "r_env": 0.8288, "dynamic_pressure_pa": 66.35, "outcome": "in_flight"}, {"step": 42, "elapsed_time_s": 84.0, "position_3d": [4.0472, 12.7056, 0.4], "position_meters": [381.17, 568.59, 160.0], "velocity_mps": [-0.003, 0.597, 0.0], "ground_speed_mps": 0.597, "airspeed_mps": 11.341, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 89.34, "power_watts": 229.77, "energy_consumed_wh": 7.9959, "r_env": 0.828, "dynamic_pressure_pa": 66.02, "outcome": "in_flight"}, {"step": 43, "elapsed_time_s": 86.0, "position_3d": [4.3564, 12.2334, 0.4], "position_meters": [367.0, 559.31, 160.0], "velocity_mps": [-7.082, -4.638, 0.0], "ground_speed_mps": 8.466, "airspeed_mps": 18.212, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 88.81, "power_watts": 713.02, "energy_consumed_wh": 8.3921, "r_env": 0.834, "dynamic_pressure_pa": 170.26, "outcome": "in_flight"}, {"step": 44, "elapsed_time_s": 88.0, "position_3d": [4.1972, 12.8993, 0.4], "position_meters": [386.98, 564.08, 160.0], "velocity_mps": [9.989, 2.387, 0.0], "ground_speed_mps": 10.27, "airspeed_mps": 13.859, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 88.48, "power_watts": 442.72, "energy_consumed_wh": 8.638, "r_env": 0.8279, "dynamic_pressure_pa": 98.6, "outcome": "in_flight"}, {"step": 45, "elapsed_time_s": 90.0, "position_3d": [4.1583, 12.8992, 0.4], "position_meters": [386.97, 565.25, 160.0], "velocity_mps": [-0.003, 0.585, 0.0], "ground_speed_mps": 0.585, "airspeed_mps": 11.108, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 88.31, "power_watts": 229.77, "energy_consumed_wh": 8.7657, "r_env": 0.8215, "dynamic_pressure_pa": 63.34, "outcome": "in_flight"}, {"step": 46, "elapsed_time_s": 92.0, "position_3d": [4.1189, 12.899, 0.4], "position_meters": [386.97, 566.43, 160.0], "velocity_mps": [-0.003, 0.59, 0.0], "ground_speed_mps": 0.59, "airspeed_mps": 11.209, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 88.14, "power_watts": 229.77, "energy_consumed_wh": 8.8933, "r_env": 0.8243, "dynamic_pressure_pa": 64.49, "outcome": "in_flight"}, {"step": 47, "elapsed_time_s": 94.0, "position_3d": [4.0788, 12.8988, 0.4], "position_meters": [386.96, 567.64, 160.0], "velocity_mps": [-0.003, 0.602, 0.0], "ground_speed_mps": 0.602, "airspeed_mps": 11.442, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 87.97, "power_watts": 229.77, "energy_consumed_wh": 9.021, "r_env": 0.8308, "dynamic_pressure_pa": 67.21, "outcome": "in_flight"}, {"step": 48, "elapsed_time_s": 96.0, "position_3d": [4.0385, 12.8986, 0.4], "position_meters": [386.96, 568.84, 160.0], "velocity_mps": [-0.003, 0.604, 0.0], "ground_speed_mps": 0.604, "airspeed_mps": 11.467, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 87.8, "power_watts": 229.77, "energy_consumed_wh": 9.1486, "r_env": 0.8315, "dynamic_pressure_pa": 67.5, "outcome": "in_flight"}, {"step": 49, "elapsed_time_s": 98.0, "position_3d": [4.3488, 12.4264, 0.4], "position_meters": [372.79, 559.53, 160.0], "velocity_mps": [-7.082, -4.654, 0.0], "ground_speed_mps": 8.475, "airspeed_mps": 18.153, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 87.28, "power_watts": 708.3, "energy_consumed_wh": 9.5421, "r_env": 0.8319, "dynamic_pressure_pa": 169.15, "outcome": "in_flight"}, {"step": 50, "elapsed_time_s": 100.0, "position_3d": [4.3089, 12.4263, 0.4], "position_meters": [372.79, 560.73, 160.0], "velocity_mps": [-0.003, 0.599, 0.0], "ground_speed_mps": 0.599, "airspeed_mps": 11.39, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 87.11, "power_watts": 229.77, "energy_consumed_wh": 9.6698, "r_env": 0.8294, "dynamic_pressure_pa": 66.6, "outcome": "in_flight"}, {"step": 51, "elapsed_time_s": 102.0, "position_3d": [4.2683, 12.4261, 0.4], "position_meters": [372.78, 561.95, 160.0], "velocity_mps": [-0.003, 0.608, 0.0], "ground_speed_mps": 0.608, "airspeed_mps": 11.55, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 86.94, "power_watts": 229.77, "energy_consumed_wh": 9.7974, "r_env": 0.8339, "dynamic_pressure_pa": 68.48, "outcome": "in_flight"}, {"step": 52, "elapsed_time_s": 104.0, "position_3d": [4.2289, 12.4259, 0.4], "position_meters": [372.78, 563.13, 160.0], "velocity_mps": [-0.003, 0.592, 0.0], "ground_speed_mps": 0.592, "airspeed_mps": 11.251, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 86.77, "power_watts": 229.77, "energy_consumed_wh": 9.9251, "r_env": 0.8255, "dynamic_pressure_pa": 64.98, "outcome": "in_flight"}, {"step": 53, "elapsed_time_s": 106.0, "position_3d": [4.1891, 12.4257, 0.4], "position_meters": [372.77, 564.33, 160.0], "velocity_mps": [-0.003, 0.596, 0.0], "ground_speed_mps": 0.596, "airspeed_mps": 11.329, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 86.6, "power_watts": 229.77, "energy_consumed_wh": 10.0527, "r_env": 0.8276, "dynamic_pressure_pa": 65.88, "outcome": "in_flight"}, {"step": 54, "elapsed_time_s": 108.0, "position_3d": [4.4983, 11.9535, 0.4], "position_meters": [358.61, 555.05, 160.0], "velocity_mps": [-7.082, -4.638, 0.0], "ground_speed_mps": 8.466, "airspeed_mps": 18.214, "heading_rad": 3.927, "terrain_clearance_norm": 0.3846, "battery_soc_pct": 86.07, "power_watts": 713.16, "energy_consumed_wh": 10.4489, "r_env": 0.8341, "dynamic_pressure_pa": 170.29, "outcome": "in_flight"}, {"step": 55, "elapsed_time_s": 110.0, "position_3d": [4.3351, 12.6194, 0.4], "position_meters": [378.58, 559.95, 160.0], "velocity_mps": [9.989, 2.447, 0.0], "ground_speed_mps": 10.284, "airspeed_mps": 14.027, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 85.73, "power_watts": 450.55, "energy_consumed_wh": 10.6992, "r_env": 0.836, "dynamic_pressure_pa": 101.0, "outcome": "in_flight"}, {"step": 56, "elapsed_time_s": 112.0, "position_3d": [4.2953, 12.6192, 0.4], "position_meters": [378.58, 561.14, 160.0], "velocity_mps": [-0.003, 0.598, 0.0], "ground_speed_mps": 0.598, "airspeed_mps": 11.36, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 85.56, "power_watts": 229.77, "energy_consumed_wh": 10.8269, "r_env": 0.8285, "dynamic_pressure_pa": 66.24, "outcome": "in_flight"}, {"step": 57, "elapsed_time_s": 114.0, "position_3d": [4.2556, 12.6191, 0.4], "position_meters": [378.57, 562.33, 160.0], "velocity_mps": [-0.003, 0.596, 0.0], "ground_speed_mps": 0.596, "airspeed_mps": 11.316, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 85.39, "power_watts": 229.77, "energy_consumed_wh": 10.9545, "r_env": 0.8273, "dynamic_pressure_pa": 65.74, "outcome": "in_flight"}, {"step": 58, "elapsed_time_s": 116.0, "position_3d": [4.2168, 12.6189, 0.4], "position_meters": [378.57, 563.5, 160.0], "velocity_mps": [-0.003, 0.582, 0.0], "ground_speed_mps": 0.582, "airspeed_mps": 11.064, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 85.22, "power_watts": 229.77, "energy_consumed_wh": 11.0822, "r_env": 0.8202, "dynamic_pressure_pa": 62.84, "outcome": "in_flight"}, {"step": 59, "elapsed_time_s": 118.0, "position_3d": [4.1784, 12.6187, 0.4], "position_meters": [378.56, 564.65, 160.0], "velocity_mps": [-0.003, 0.575, 0.0], "ground_speed_mps": 0.575, "airspeed_mps": 10.934, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 85.05, "power_watts": 229.77, "energy_consumed_wh": 11.2099, "r_env": 0.8166, "dynamic_pressure_pa": 61.37, "outcome": "in_flight"}, {"step": 60, "elapsed_time_s": 120.0, "position_3d": [4.4978, 12.1466, 0.4], "position_meters": [364.4, 555.07, 160.0], "velocity_mps": [-7.082, -4.791, 0.0], "ground_speed_mps": 8.55, "airspeed_mps": 17.65, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 84.56, "power_watts": 669.62, "energy_consumed_wh": 11.5819, "r_env": 0.8136, "dynamic_pressure_pa": 159.91, "outcome": "in_flight"}, {"step": 61, "elapsed_time_s": 122.0, "position_3d": [4.3443, 12.8125, 0.4], "position_meters": [384.38, 559.67, 160.0], "velocity_mps": [9.989, 2.303, 0.0], "ground_speed_mps": 10.251, "airspeed_mps": 13.628, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 84.24, "power_watts": 432.27, "energy_consumed_wh": 11.822, "r_env": 0.8167, "dynamic_pressure_pa": 95.34, "outcome": "in_flight"}, {"step": 62, "elapsed_time_s": 124.0, "position_3d": [3.5443, 12.8118, 0.4], "position_meters": [384.35, 583.67, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.489, "heading_rad": 0.0, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 84.07, "power_watts": 229.78, "energy_consumed_wh": 11.9497, "r_env": 0.8167, "dynamic_pressure_pa": 0.12, "outcome": "in_flight"}, {"step": 63, "elapsed_time_s": 126.0, "position_3d": [3.5059, 12.8116, 0.4], "position_meters": [384.35, 584.82, 160.0], "velocity_mps": [-0.003, 0.576, 0.0], "ground_speed_mps": 0.576, "airspeed_mps": 10.947, "heading_rad": 0.0, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 83.9, "power_watts": 229.77, "energy_consumed_wh": 12.0773, "r_env": 0.8169, "dynamic_pressure_pa": 61.52, "outcome": "in_flight"}, {"step": 64, "elapsed_time_s": 128.0, "position_3d": [3.4663, 12.8115, 0.4], "position_meters": [384.34, 586.01, 160.0], "velocity_mps": [-0.003, 0.593, 0.0], "ground_speed_mps": 0.593, "airspeed_mps": 11.269, "heading_rad": 0.0, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 83.73, "power_watts": 229.77, "energy_consumed_wh": 12.205, "r_env": 0.826, "dynamic_pressure_pa": 65.19, "outcome": "in_flight"}, {"step": 65, "elapsed_time_s": 130.0, "position_3d": [3.4266, 12.8113, 0.4], "position_meters": [384.34, 587.2, 160.0], "velocity_mps": [-0.003, 0.597, 0.0], "ground_speed_mps": 0.597, "airspeed_mps": 11.338, "heading_rad": 0.0, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 83.56, "power_watts": 229.77, "energy_consumed_wh": 12.3326, "r_env": 0.8279, "dynamic_pressure_pa": 65.99, "outcome": "in_flight"}, {"step": 66, "elapsed_time_s": 132.0, "position_3d": [3.3871, 12.8111, 0.4], "position_meters": [384.33, 588.39, 160.0], "velocity_mps": [-0.003, 0.592, 0.0], "ground_speed_mps": 0.592, "airspeed_mps": 11.25, "heading_rad": 0.0, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 83.39, "power_watts": 229.77, "energy_consumed_wh": 12.4603, "r_env": 0.8254, "dynamic_pressure_pa": 64.97, "outcome": "in_flight"}, {"step": 67, "elapsed_time_s": 134.0, "position_3d": [3.6985, 12.3389, 0.4], "position_meters": [370.17, 579.05, 160.0], "velocity_mps": [-7.082, -4.671, 0.0], "ground_speed_mps": 8.484, "airspeed_mps": 18.09, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 82.87, "power_watts": 703.39, "energy_consumed_wh": 12.8511, "r_env": 0.8296, "dynamic_pressure_pa": 167.99, "outcome": "in_flight"}, {"step": 68, "elapsed_time_s": 136.0, "position_3d": [3.6584, 12.3387, 0.4], "position_meters": [370.16, 580.25, 160.0], "velocity_mps": [-0.003, 0.602, 0.0], "ground_speed_mps": 0.602, "airspeed_mps": 11.439, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 82.7, "power_watts": 229.77, "energy_consumed_wh": 12.9787, "r_env": 0.8307, "dynamic_pressure_pa": 67.17, "outcome": "in_flight"}, {"step": 69, "elapsed_time_s": 138.0, "position_3d": [3.618, 12.3386, 0.4], "position_meters": [370.16, 581.46, 160.0], "velocity_mps": [-0.003, 0.606, 0.0], "ground_speed_mps": 0.606, "airspeed_mps": 11.508, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 82.52, "power_watts": 229.77, "energy_consumed_wh": 13.1064, "r_env": 0.8327, "dynamic_pressure_pa": 67.98, "outcome": "in_flight"}, {"step": 70, "elapsed_time_s": 140.0, "position_3d": [3.5779, 12.3384, 0.4], "position_meters": [370.15, 582.66, 160.0], "velocity_mps": [-0.003, 0.602, 0.0], "ground_speed_mps": 0.602, "airspeed_mps": 11.432, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 82.35, "power_watts": 229.77, "energy_consumed_wh": 13.234, "r_env": 0.8306, "dynamic_pressure_pa": 67.09, "outcome": "in_flight"}, {"step": 71, "elapsed_time_s": 142.0, "position_3d": [3.5379, 12.3382, 0.4], "position_meters": [370.15, 583.86, 160.0], "velocity_mps": [-0.003, 0.599, 0.0], "ground_speed_mps": 0.599, "airspeed_mps": 11.382, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 82.18, "power_watts": 229.77, "energy_consumed_wh": 13.3617, "r_env": 0.8292, "dynamic_pressure_pa": 66.51, "outcome": "in_flight"}, {"step": 72, "elapsed_time_s": 144.0, "position_3d": [3.8478, 11.866, 0.4], "position_meters": [355.98, 574.57, 160.0], "velocity_mps": [-7.082, -4.648, 0.0], "ground_speed_mps": 8.471, "airspeed_mps": 18.177, "heading_rad": 3.927, "terrain_clearance_norm": 0.3795, "battery_soc_pct": 81.66, "power_watts": 710.25, "energy_consumed_wh": 13.7562, "r_env": 0.8328, "dynamic_pressure_pa": 169.61, "outcome": "in_flight"}, {"step": 73, "elapsed_time_s": 146.0, "position_3d": [3.6872, 12.5319, 0.4], "position_meters": [375.96, 579.38, 160.0], "velocity_mps": [9.989, 2.409, 0.0], "ground_speed_mps": 10.275, "airspeed_mps": 13.919, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 81.33, "power_watts": 445.51, "energy_consumed_wh": 14.0037, "r_env": 0.8308, "dynamic_pressure_pa": 99.45, "outcome": "in_flight"}, {"step": 74, "elapsed_time_s": 148.0, "position_3d": [3.6481, 12.5317, 0.4], "position_meters": [375.95, 580.56, 160.0], "velocity_mps": [-0.003, 0.586, 0.0], "ground_speed_mps": 0.586, "airspeed_mps": 11.135, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 81.16, "power_watts": 229.77, "energy_consumed_wh": 14.1314, "r_env": 0.8222, "dynamic_pressure_pa": 63.64, "outcome": "in_flight"}, {"step": 75, "elapsed_time_s": 150.0, "position_3d": [3.6096, 12.5316, 0.4], "position_meters": [375.95, 581.71, 160.0], "velocity_mps": [-0.003, 0.578, 0.0], "ground_speed_mps": 0.578, "airspeed_mps": 10.985, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 80.99, "power_watts": 229.77, "energy_consumed_wh": 14.2591, "r_env": 0.818, "dynamic_pressure_pa": 61.94, "outcome": "in_flight"}, {"step": 76, "elapsed_time_s": 152.0, "position_3d": [3.5707, 12.5314, 0.4], "position_meters": [375.94, 582.88, 160.0], "velocity_mps": [-0.003, 0.584, 0.0], "ground_speed_mps": 0.584, "airspeed_mps": 11.093, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 80.82, "power_watts": 229.77, "energy_consumed_wh": 14.3867, "r_env": 0.821, "dynamic_pressure_pa": 63.17, "outcome": "in_flight"}, {"step": 77, "elapsed_time_s": 154.0, "position_3d": [3.5318, 12.5312, 0.4], "position_meters": [375.94, 584.05, 160.0], "velocity_mps": [-0.003, 0.583, 0.0], "ground_speed_mps": 0.583, "airspeed_mps": 11.076, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 80.65, "power_watts": 229.77, "energy_consumed_wh": 14.5144, "r_env": 0.8206, "dynamic_pressure_pa": 62.98, "outcome": "in_flight"}, {"step": 78, "elapsed_time_s": 156.0, "position_3d": [3.8486, 12.0591, 0.4], "position_meters": [361.77, 574.54, 160.0], "velocity_mps": [-7.082, -4.751, 0.0], "ground_speed_mps": 8.528, "airspeed_mps": 17.796, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 80.14, "power_watts": 680.63, "energy_consumed_wh": 14.8925, "r_env": 0.8189, "dynamic_pressure_pa": 162.57, "outcome": "in_flight"}, {"step": 79, "elapsed_time_s": 158.0, "position_3d": [3.6949, 12.725, 0.4], "position_meters": [381.75, 579.15, 160.0], "velocity_mps": [9.989, 2.305, 0.0], "ground_speed_mps": 10.252, "airspeed_mps": 13.634, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 79.82, "power_watts": 432.54, "energy_consumed_wh": 15.1328, "r_env": 0.817, "dynamic_pressure_pa": 95.43, "outcome": "in_flight"}, {"step": 80, "elapsed_time_s": 160.0, "position_3d": [3.6567, 12.7248, 0.4], "position_meters": [381.75, 580.3, 160.0], "velocity_mps": [-0.003, 0.572, 0.0], "ground_speed_mps": 0.572, "airspeed_mps": 10.868, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 79.65, "power_watts": 229.77, "energy_consumed_wh": 15.2604, "r_env": 0.8147, "dynamic_pressure_pa": 60.63, "outcome": "in_flight"}, {"step": 81, "elapsed_time_s": 162.0, "position_3d": [3.618, 12.7247, 0.4], "position_meters": [381.74, 581.46, 160.0], "velocity_mps": [-0.003, 0.58, 0.0], "ground_speed_mps": 0.581, "airspeed_mps": 11.03, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 79.48, "power_watts": 229.77, "energy_consumed_wh": 15.3881, "r_env": 0.8192, "dynamic_pressure_pa": 62.45, "outcome": "in_flight"}, {"step": 82, "elapsed_time_s": 164.0, "position_3d": [3.5791, 12.7245, 0.4], "position_meters": [381.73, 582.63, 160.0], "velocity_mps": [-0.003, 0.585, 0.0], "ground_speed_mps": 0.585, "airspeed_mps": 11.114, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 79.31, "power_watts": 229.77, "energy_consumed_wh": 15.5157, "r_env": 0.8216, "dynamic_pressure_pa": 63.4, "outcome": "in_flight"}, {"step": 83, "elapsed_time_s": 166.0, "position_3d": [3.5394, 12.7243, 0.4], "position_meters": [381.73, 583.82, 160.0], "velocity_mps": [-0.003, 0.594, 0.0], "ground_speed_mps": 0.594, "airspeed_mps": 11.294, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 79.14, "power_watts": 229.77, "energy_consumed_wh": 15.6434, "r_env": 0.8267, "dynamic_pressure_pa": 65.47, "outcome": "in_flight"}, {"step": 84, "elapsed_time_s": 168.0, "position_3d": [3.8526, 12.2521, 0.4], "position_meters": [367.56, 574.42, 160.0], "velocity_mps": [-7.082, -4.698, 0.0], "ground_speed_mps": 8.499, "airspeed_mps": 17.993, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 78.63, "power_watts": 695.82, "energy_consumed_wh": 16.03, "r_env": 0.8261, "dynamic_pressure_pa": 166.2, "outcome": "in_flight"}, {"step": 85, "elapsed_time_s": 170.0, "position_3d": [3.8133, 12.252, 0.4], "position_meters": [367.56, 575.6, 160.0], "velocity_mps": [-0.003, 0.589, 0.0], "ground_speed_mps": 0.589, "airspeed_mps": 11.193, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 78.46, "power_watts": 229.77, "energy_consumed_wh": 16.1576, "r_env": 0.8238, "dynamic_pressure_pa": 64.31, "outcome": "in_flight"}, {"step": 86, "elapsed_time_s": 172.0, "position_3d": [3.7739, 12.2518, 0.4], "position_meters": [367.55, 576.78, 160.0], "velocity_mps": [-0.003, 0.592, 0.0], "ground_speed_mps": 0.592, "airspeed_mps": 11.239, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 78.29, "power_watts": 229.77, "energy_consumed_wh": 16.2853, "r_env": 0.8251, "dynamic_pressure_pa": 64.84, "outcome": "in_flight"}, {"step": 87, "elapsed_time_s": 174.0, "position_3d": [3.7349, 12.2516, 0.4], "position_meters": [367.55, 577.95, 160.0], "velocity_mps": [-0.003, 0.585, 0.0], "ground_speed_mps": 0.585, "airspeed_mps": 11.123, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 78.12, "power_watts": 229.77, "energy_consumed_wh": 16.4129, "r_env": 0.8219, "dynamic_pressure_pa": 63.51, "outcome": "in_flight"}, {"step": 88, "elapsed_time_s": 176.0, "position_3d": [3.6964, 12.2514, 0.4], "position_meters": [367.54, 579.11, 160.0], "velocity_mps": [-0.003, 0.577, 0.0], "ground_speed_mps": 0.577, "airspeed_mps": 10.955, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 77.95, "power_watts": 229.77, "energy_consumed_wh": 16.5406, "r_env": 0.8171, "dynamic_pressure_pa": 61.6, "outcome": "in_flight"}, {"step": 89, "elapsed_time_s": 178.0, "position_3d": [4.0165, 11.7793, 0.4], "position_meters": [353.38, 569.5, 160.0], "velocity_mps": [-7.082, -4.801, 0.0], "ground_speed_mps": 8.556, "airspeed_mps": 17.613, "heading_rad": 3.927, "terrain_clearance_norm": 0.3743, "battery_soc_pct": 77.45, "power_watts": 666.92, "energy_consumed_wh": 16.9111, "r_env": 0.8123, "dynamic_pressure_pa": 159.25, "outcome": "in_flight"}, {"step": 90, "elapsed_time_s": 180.0, "position_3d": [3.8653, 12.4453, 0.4], "position_meters": [373.36, 574.04, 160.0], "velocity_mps": [9.989, 2.269, 0.0], "ground_speed_mps": 10.244, "airspeed_mps": 13.536, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 77.13, "power_watts": 428.16, "energy_consumed_wh": 17.1489, "r_env": 0.8122, "dynamic_pressure_pa": 94.05, "outcome": "in_flight"}, {"step": 91, "elapsed_time_s": 182.0, "position_3d": [3.8268, 12.4451, 0.4], "position_meters": [373.35, 575.2, 160.0], "velocity_mps": [-0.003, 0.577, 0.0], "ground_speed_mps": 0.577, "airspeed_mps": 10.955, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 76.96, "power_watts": 229.77, "energy_consumed_wh": 17.2766, "r_env": 0.8172, "dynamic_pressure_pa": 61.61, "outcome": "in_flight"}, {"step": 92, "elapsed_time_s": 184.0, "position_3d": [3.7886, 12.4449, 0.4], "position_meters": [373.35, 576.34, 160.0], "velocity_mps": [-0.003, 0.574, 0.0], "ground_speed_mps": 0.574, "airspeed_mps": 10.9, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 76.79, "power_watts": 229.77, "energy_consumed_wh": 17.4042, "r_env": 0.8156, "dynamic_pressure_pa": 60.98, "outcome": "in_flight"}, {"step": 93, "elapsed_time_s": 186.0, "position_3d": [3.7506, 12.4447, 0.4], "position_meters": [373.34, 577.48, 160.0], "velocity_mps": [-0.003, 0.57, 0.0], "ground_speed_mps": 0.57, "airspeed_mps": 10.835, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 76.62, "power_watts": 229.77, "energy_consumed_wh": 17.5319, "r_env": 0.8138, "dynamic_pressure_pa": 60.27, "outcome": "in_flight"}, {"step": 94, "elapsed_time_s": 188.0, "position_3d": [3.7119, 12.4445, 0.4], "position_meters": [373.34, 578.64, 160.0], "velocity_mps": [-0.003, 0.579, 0.0], "ground_speed_mps": 0.579, "airspeed_mps": 11.008, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 76.45, "power_watts": 229.77, "energy_consumed_wh": 17.6596, "r_env": 0.8186, "dynamic_pressure_pa": 62.2, "outcome": "in_flight"}, {"step": 95, "elapsed_time_s": 190.0, "position_3d": [4.0295, 11.9724, 0.4], "position_meters": [359.17, 569.11, 160.0], "velocity_mps": [-7.082, -4.764, 0.0], "ground_speed_mps": 8.535, "airspeed_mps": 17.75, "heading_rad": 3.927, "terrain_clearance_norm": 0.3858, "battery_soc_pct": 75.95, "power_watts": 677.12, "energy_consumed_wh": 18.0357, "r_env": 0.8172, "dynamic_pressure_pa": 161.72, "outcome": "in_flight"}, {"step": 96, "elapsed_time_s": 192.0, "position_3d": [3.8723, 12.6383, 0.4], "position_meters": [379.15, 573.83, 160.0], "velocity_mps": [9.989, 2.359, 0.0], "ground_speed_mps": 10.264, "airspeed_mps": 13.781, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 75.63, "power_watts": 439.15, "energy_consumed_wh": 18.2797, "r_env": 0.8242, "dynamic_pressure_pa": 97.49, "outcome": "in_flight"}, {"step": 97, "elapsed_time_s": 194.0, "position_3d": [3.8339, 12.6382, 0.4], "position_meters": [379.14, 574.98, 160.0], "velocity_mps": [-0.003, 0.576, 0.0], "ground_speed_mps": 0.576, "airspeed_mps": 10.942, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 75.46, "power_watts": 229.77, "energy_consumed_wh": 18.4074, "r_env": 0.8168, "dynamic_pressure_pa": 61.46, "outcome": "in_flight"}, {"step": 98, "elapsed_time_s": 196.0, "position_3d": [3.7945, 12.638, 0.4], "position_meters": [379.14, 576.17, 160.0], "velocity_mps": [-0.003, 0.591, 0.0], "ground_speed_mps": 0.591, "airspeed_mps": 11.236, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 75.29, "power_watts": 229.77, "energy_consumed_wh": 18.535, "r_env": 0.825, "dynamic_pressure_pa": 64.81, "outcome": "in_flight"}, {"step": 99, "elapsed_time_s": 198.0, "position_3d": [3.7542, 12.6378, 0.4], "position_meters": [379.13, 577.37, 160.0], "velocity_mps": [-0.003, 0.604, 0.0], "ground_speed_mps": 0.604, "airspeed_mps": 11.47, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 75.12, "power_watts": 229.77, "energy_consumed_wh": 18.6627, "r_env": 0.8316, "dynamic_pressure_pa": 67.53, "outcome": "in_flight"}, {"step": 100, "elapsed_time_s": 200.0, "position_3d": [3.7145, 12.6376, 0.4], "position_meters": [379.13, 578.56, 160.0], "velocity_mps": [-0.003, 0.595, 0.0], "ground_speed_mps": 0.595, "airspeed_mps": 11.308, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 74.95, "power_watts": 229.77, "energy_consumed_wh": 18.7903, "r_env": 0.8271, "dynamic_pressure_pa": 65.64, "outcome": "in_flight"}, {"step": 101, "elapsed_time_s": 202.0, "position_3d": [4.027, 12.1654, 0.4], "position_meters": [364.96, 569.19, 160.0], "velocity_mps": [-7.082, -4.687, 0.0], "ground_speed_mps": 8.493, "airspeed_mps": 18.033, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 74.43, "power_watts": 698.91, "energy_consumed_wh": 19.1786, "r_env": 0.8275, "dynamic_pressure_pa": 166.93, "outcome": "in_flight"}, {"step": 102, "elapsed_time_s": 204.0, "position_3d": [3.987, 12.1653, 0.4], "position_meters": [364.96, 570.39, 160.0], "velocity_mps": [-0.003, 0.6, 0.0], "ground_speed_mps": 0.6, "airspeed_mps": 11.4, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 74.26, "power_watts": 229.77, "energy_consumed_wh": 19.3063, "r_env": 0.8297, "dynamic_pressure_pa": 66.72, "outcome": "in_flight"}, {"step": 103, "elapsed_time_s": 206.0, "position_3d": [3.9464, 12.1651, 0.4], "position_meters": [364.95, 571.61, 160.0], "velocity_mps": [-0.003, 0.608, 0.0], "ground_speed_mps": 0.608, "airspeed_mps": 11.558, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 74.09, "power_watts": 229.77, "energy_consumed_wh": 19.4339, "r_env": 0.8341, "dynamic_pressure_pa": 68.58, "outcome": "in_flight"}, {"step": 104, "elapsed_time_s": 208.0, "position_3d": [3.906, 12.1649, 0.4], "position_meters": [364.95, 572.82, 160.0], "velocity_mps": [-0.003, 0.606, 0.0], "ground_speed_mps": 0.606, "airspeed_mps": 11.523, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 73.92, "power_watts": 229.77, "energy_consumed_wh": 19.5616, "r_env": 0.8331, "dynamic_pressure_pa": 68.16, "outcome": "in_flight"}, {"step": 105, "elapsed_time_s": 210.0, "position_3d": [3.8646, 12.1647, 0.4], "position_meters": [364.94, 574.06, 160.0], "velocity_mps": [-0.003, 0.621, 0.0], "ground_speed_mps": 0.621, "airspeed_mps": 11.795, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 73.75, "power_watts": 229.77, "energy_consumed_wh": 19.6892, "r_env": 0.8407, "dynamic_pressure_pa": 71.42, "outcome": "in_flight"}, {"step": 106, "elapsed_time_s": 212.0, "position_3d": [4.1697, 11.6925, 0.4], "position_meters": [350.78, 564.91, 160.0], "velocity_mps": [-7.083, -4.576, 0.0], "ground_speed_mps": 8.432, "airspeed_mps": 18.443, "heading_rad": 3.927, "terrain_clearance_norm": 0.3692, "battery_soc_pct": 73.21, "power_watts": 731.6, "energy_consumed_wh": 20.0957, "r_env": 0.8424, "dynamic_pressure_pa": 174.6, "outcome": "in_flight"}, {"step": 107, "elapsed_time_s": 214.0, "position_3d": [4.0049, 12.3584, 0.4], "position_meters": [370.75, 569.85, 160.0], "velocity_mps": [9.988, 2.472, 0.0], "ground_speed_mps": 10.29, "airspeed_mps": 14.097, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 72.87, "power_watts": 453.88, "energy_consumed_wh": 20.3478, "r_env": 0.8393, "dynamic_pressure_pa": 102.01, "outcome": "in_flight"}, {"step": 108, "elapsed_time_s": 216.0, "position_3d": [3.9632, 12.3582, 0.4], "position_meters": [370.75, 571.1, 160.0], "velocity_mps": [-0.003, 0.624, 0.0], "ground_speed_mps": 0.624, "airspeed_mps": 11.859, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 72.7, "power_watts": 229.77, "energy_consumed_wh": 20.4755, "r_env": 0.8425, "dynamic_pressure_pa": 72.19, "outcome": "in_flight"}, {"step": 109, "elapsed_time_s": 218.0, "position_3d": [3.9219, 12.358, 0.4], "position_meters": [370.74, 572.34, 160.0], "velocity_mps": [-0.003, 0.621, 0.0], "ground_speed_mps": 0.621, "airspeed_mps": 11.798, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 72.53, "power_watts": 229.77, "energy_consumed_wh": 20.6031, "r_env": 0.8408, "dynamic_pressure_pa": 71.45, "outcome": "in_flight"}, {"step": 110, "elapsed_time_s": 220.0, "position_3d": [3.88, 12.3578, 0.4], "position_meters": [370.73, 573.6, 160.0], "velocity_mps": [-0.003, 0.627, 0.0], "ground_speed_mps": 0.627, "airspeed_mps": 11.917, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 72.36, "power_watts": 229.77, "energy_consumed_wh": 20.7308, "r_env": 0.8442, "dynamic_pressure_pa": 72.91, "outcome": "in_flight"}, {"step": 111, "elapsed_time_s": 222.0, "position_3d": [3.8385, 12.3576, 0.4], "position_meters": [370.73, 574.85, 160.0], "velocity_mps": [-0.003, 0.623, 0.0], "ground_speed_mps": 0.623, "airspeed_mps": 11.842, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 72.19, "power_watts": 229.77, "energy_consumed_wh": 20.8584, "r_env": 0.842, "dynamic_pressure_pa": 71.98, "outcome": "in_flight"}, {"step": 112, "elapsed_time_s": 224.0, "position_3d": [4.1421, 11.8854, 0.4], "position_meters": [356.56, 565.74, 160.0], "velocity_mps": [-7.083, -4.554, 0.0], "ground_speed_mps": 8.421, "airspeed_mps": 18.522, "heading_rad": 3.927, "terrain_clearance_norm": 0.3806, "battery_soc_pct": 71.64, "power_watts": 738.08, "energy_consumed_wh": 21.2685, "r_env": 0.8452, "dynamic_pressure_pa": 176.1, "outcome": "in_flight"}, {"step": 113, "elapsed_time_s": 226.0, "position_3d": [3.9744, 12.5513, 0.4], "position_meters": [376.54, 570.77, 160.0], "velocity_mps": [9.988, 2.516, 0.0], "ground_speed_mps": 10.3, "airspeed_mps": 14.22, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 71.3, "power_watts": 459.79, "energy_consumed_wh": 21.5239, "r_env": 0.8451, "dynamic_pressure_pa": 103.79, "outcome": "in_flight"}, {"step": 114, "elapsed_time_s": 228.0, "position_3d": [3.9323, 12.5511, 0.4], "position_meters": [376.53, 572.03, 160.0], "velocity_mps": [-0.003, 0.631, 0.0], "ground_speed_mps": 0.631, "airspeed_mps": 11.986, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 71.13, "power_watts": 229.77, "energy_consumed_wh": 21.6516, "r_env": 0.8461, "dynamic_pressure_pa": 73.75, "outcome": "in_flight"}, {"step": 115, "elapsed_time_s": 230.0, "position_3d": [3.8907, 12.5509, 0.4], "position_meters": [376.53, 573.28, 160.0], "velocity_mps": [-0.003, 0.624, 0.0], "ground_speed_mps": 0.624, "airspeed_mps": 11.864, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 70.96, "power_watts": 229.77, "energy_consumed_wh": 21.7792, "r_env": 0.8427, "dynamic_pressure_pa": 72.25, "outcome": "in_flight"}, {"step": 116, "elapsed_time_s": 232.0, "position_3d": [3.8492, 12.5507, 0.4], "position_meters": [376.52, 574.52, 160.0], "velocity_mps": [-0.003, 0.622, 0.0], "ground_speed_mps": 0.622, "airspeed_mps": 11.82, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 70.79, "power_watts": 229.77, "energy_consumed_wh": 21.9069, "r_env": 0.8414, "dynamic_pressure_pa": 71.72, "outcome": "in_flight"}, {"step": 117, "elapsed_time_s": 234.0, "position_3d": [3.8077, 12.5505, 0.4], "position_meters": [376.52, 575.77, 160.0], "velocity_mps": [-0.003, 0.622, 0.0], "ground_speed_mps": 0.622, "airspeed_mps": 11.826, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 70.62, "power_watts": 229.77, "energy_consumed_wh": 22.0345, "r_env": 0.8416, "dynamic_pressure_pa": 71.79, "outcome": "in_flight"}, {"step": 118, "elapsed_time_s": 236.0, "position_3d": [4.1114, 12.0783, 0.4], "position_meters": [362.35, 566.66, 160.0], "velocity_mps": [-7.083, -4.555, 0.0], "ground_speed_mps": 8.421, "airspeed_mps": 18.521, "heading_rad": 3.927, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 70.07, "power_watts": 738.01, "energy_consumed_wh": 22.4445, "r_env": 0.8452, "dynamic_pressure_pa": 176.08, "outcome": "in_flight"}, {"step": 119, "elapsed_time_s": 238.0, "position_3d": [3.9457, 12.7442, 0.4], "position_meters": [382.33, 571.63, 160.0], "velocity_mps": [9.988, 2.485, 0.0], "ground_speed_mps": 10.293, "airspeed_mps": 14.134, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 69.74, "power_watts": 455.66, "energy_consumed_wh": 22.6977, "r_env": 0.841, "dynamic_pressure_pa": 102.55, "outcome": "in_flight"}, {"step": 120, "elapsed_time_s": 240.0, "position_3d": [3.904, 12.744, 0.4], "position_meters": [382.32, 572.88, 160.0], "velocity_mps": [-0.003, 0.626, 0.0], "ground_speed_mps": 0.626, "airspeed_mps": 11.885, "heading_rad": 1.5708, "terrain_clearance_norm": 0.3874, "battery_soc_pct": 69.57, "power_watts": 229.77, "energy_consumed_wh": 22.8253, "r_env": 0.8433, "dynamic_pressure_pa": 72.51, "outcome": "timeout"}]}
};

// Embedded Empirical Benchmark Summary from evaluation_summary.csv
const EVALUATION_SUMMARY = [{"bucket": "Calm", "agent": "AdaptiveAgent", "trials": "100", "success_rate_pct": "97.0", "ci_95_pct": "3.3", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "3.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "25.9", "mean_flight_time_s": "51.9", "mean_path_length_m": "516.0", "mean_energy_wh": "4.469", "mean_min_clearance": "0.258", "mean_interventions": "1.18", "mean_reward": "169.7", "mean_wind_speed_mps": "2.21", "mean_r_env": "0.189"}, {"bucket": "Calm", "agent": "StaticBaseline", "trials": "100", "success_rate_pct": "95.0", "ci_95_pct": "4.3", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "5.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "35.7", "mean_flight_time_s": "71.3", "mean_path_length_m": "710.5", "mean_energy_wh": "6.125", "mean_min_clearance": "0.257", "mean_interventions": "2.76", "mean_reward": "161.4", "mean_wind_speed_mps": "2.21", "mean_r_env": "0.189"}, {"bucket": "Calm", "agent": "RuleBasedPlanner", "trials": "100", "success_rate_pct": "100.0", "ci_95_pct": "0.0", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "0.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "19.3", "mean_flight_time_s": "38.6", "mean_path_length_m": "384.3", "mean_energy_wh": "3.332", "mean_min_clearance": "0.265", "mean_interventions": "0.0", "mean_reward": "179.5", "mean_wind_speed_mps": "2.21", "mean_r_env": "0.189"}, {"bucket": "Moderate", "agent": "AdaptiveAgent", "trials": "100", "success_rate_pct": "66.0", "ci_95_pct": "9.3", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "34.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "58.7", "mean_flight_time_s": "117.4", "mean_path_length_m": "747.2", "mean_energy_wh": "10.251", "mean_min_clearance": "0.271", "mean_interventions": "32.5", "mean_reward": "38.9", "mean_wind_speed_mps": "7.01", "mean_r_env": "0.472"}, {"bucket": "Moderate", "agent": "StaticBaseline", "trials": "100", "success_rate_pct": "65.0", "ci_95_pct": "9.3", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "35.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "59.0", "mean_flight_time_s": "118.1", "mean_path_length_m": "802.8", "mean_energy_wh": "10.581", "mean_min_clearance": "0.27", "mean_interventions": "31.49", "mean_reward": "64.5", "mean_wind_speed_mps": "7.01", "mean_r_env": "0.472"}, {"bucket": "Moderate", "agent": "RuleBasedPlanner", "trials": "100", "success_rate_pct": "74.0", "ci_95_pct": "8.6", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "26.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "48.9", "mean_flight_time_s": "97.7", "mean_path_length_m": "630.2", "mean_energy_wh": "8.614", "mean_min_clearance": "0.278", "mean_interventions": "26.3", "mean_reward": "91.3", "mean_wind_speed_mps": "7.01", "mean_r_env": "0.472"}, {"bucket": "Severe", "agent": "AdaptiveAgent", "trials": "100", "success_rate_pct": "3.0", "ci_95_pct": "3.3", "safe_rth_rate_pct": "95.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "2.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "5.9", "mean_flight_time_s": "11.8", "mean_path_length_m": "49.4", "mean_energy_wh": "1.108", "mean_min_clearance": "0.318", "mean_interventions": "4.57", "mean_reward": "15.1", "mean_wind_speed_mps": "13.76", "mean_r_env": "0.904"}, {"bucket": "Severe", "agent": "StaticBaseline", "trials": "100", "success_rate_pct": "0.0", "ci_95_pct": "0.0", "safe_rth_rate_pct": "96.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "4.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "7.7", "mean_flight_time_s": "15.4", "mean_path_length_m": "93.2", "mean_energy_wh": "1.715", "mean_min_clearance": "0.319", "mean_interventions": "5.08", "mean_reward": "21.1", "mean_wind_speed_mps": "13.76", "mean_r_env": "0.904"}, {"bucket": "Severe", "agent": "RuleBasedPlanner", "trials": "100", "success_rate_pct": "4.0", "ci_95_pct": "3.8", "safe_rth_rate_pct": "96.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "0.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "4.3", "mean_flight_time_s": "8.7", "mean_path_length_m": "25.4", "mean_energy_wh": "0.659", "mean_min_clearance": "0.318", "mean_interventions": "3.61", "mean_reward": "35.2", "mean_wind_speed_mps": "13.76", "mean_r_env": "0.904"}];

// Replay State
let activeMode = 'live'; // 'live' | 'replay' | 'eval' | 'specs'
let activeLogKey = 'calm';
let replayStep = 0;
let isReplayPlaying = false;
let replayTimer = null;
let replaySpeed = 1;

// Latest Safety Intervention State
let lastSafetyEvent = {
  step: 0,
  trigger: 'None (Nominal Flight)',
  originalAction: 'None',
  overriddenAction: 'None',
  recoveryMode: 'None',
  active: false
};

// ── Tab Management ──────────────────────────────────────────────────────────
function switchTab(mode) {
  activeMode = mode;
  const tabs = ['live', 'replay', 'eval', 'specs'];
  tabs.forEach(t => {
    const btn = document.getElementById('tabBtn' + t.charAt(0).toUpperCase() + t.slice(1));
    const section = document.getElementById('section' + t.charAt(0).toUpperCase() + t.slice(1));
    if (btn) {
      if (t === mode) {
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
      } else {
        btn.classList.remove('active');
        btn.setAttribute('aria-selected', 'false');
      }
    }
    if (section) {
      section.style.display = (t === mode) ? 'block' : 'none';
    }
  });

  const modeLabel = document.getElementById('activeModeLabel');
  if (modeLabel) {
    if (mode === 'live') modeLabel.textContent = 'LIVE SIMULATOR';
    else if (mode === 'replay') modeLabel.textContent = 'LOG REPLAY';
    else if (mode === 'eval') modeLabel.textContent = 'BENCHMARK EVAL';
    else if (mode === 'specs') modeLabel.textContent = 'MODEL SPECS';
  }

  // Adjust center/left layout visibility
  const liveControls = document.getElementById('liveAtmosphericControls');
  const replayControls = document.getElementById('replayScenarioControls');
  const liveBtnRow = document.getElementById('liveBtnRow');
  const replayBtnRow = document.getElementById('replayBtnRow');
  const canvasCard = document.getElementById('canvasCard');
  const rightTelemetryCard = document.getElementById('rightTelemetryCard');

  if (mode === 'live') {
    if (liveControls) liveControls.style.display = 'block';
    if (replayControls) replayControls.style.display = 'none';
    if (liveBtnRow) liveBtnRow.style.display = 'flex';
    if (replayBtnRow) replayBtnRow.style.display = 'none';
    if (canvasCard) canvasCard.style.display = 'flex';
    if (rightTelemetryCard) rightTelemetryCard.style.display = 'flex';
    pauseReplay();
    if (typeof drawScene === 'function') drawScene();
  } else if (mode === 'replay') {
    if (liveControls) liveControls.style.display = 'none';
    if (replayControls) replayControls.style.display = 'block';
    if (liveBtnRow) liveBtnRow.style.display = 'none';
    if (replayBtnRow) replayBtnRow.style.display = 'flex';
    if (canvasCard) canvasCard.style.display = 'flex';
    if (rightTelemetryCard) rightTelemetryCard.style.display = 'flex';
    if (typeof stopFlight === 'function') stopFlight();
    loadFlightLog(activeLogKey);
  } else {
    // Benchmark or Specs view
    if (canvasCard) canvasCard.style.display = 'none';
    if (rightTelemetryCard) rightTelemetryCard.style.display = 'none';
    if (liveControls) liveControls.style.display = 'none';
    if (replayControls) replayControls.style.display = 'none';
    pauseReplay();
    if (typeof stopFlight === 'function') stopFlight();
  }
}

// ── Flight Log Replay Engine ────────────────────────────────────────────────
function loadFlightLog(logKey) {
  activeLogKey = logKey;
  const logData = FLIGHT_LOGS[logKey];
  if (!logData) return;

  replayStep = 0;
  pauseReplay();

  // Update scenario selector buttons styling
  ['calm', 'moderate', 'emergency'].forEach(k => {
    const b = document.getElementById('btnLog_' + k);
    if (b) {
      if (k === logKey) {
        b.classList.add('primary');
      } else {
        b.classList.remove('primary');
      }
    }
  });

  // Metadata card
  const metaBox = document.getElementById('replayMetaBox');
  if (metaBox) {
    metaBox.innerHTML = `
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:0.75rem;">
        <div><strong>Scenario:</strong> ${logData.scenario} (Seed ${logData.seed})</div>
        <div><strong>Outcome:</strong> <span class="status-badge ${getOutcomeClass(logData.terminal_outcome)}">${logData.terminal_outcome.toUpperCase()}</span></div>
        <div><strong>Steps:</strong> ${logData.total_steps} (${logData.simulated_flight_time_s}s)</div>
        <div><strong>Energy:</strong> ${logData.energy_consumed_wh.toFixed(2)} Wh</div>
        <div><strong>End SoC:</strong> ${logData.battery_end_soc_pct.toFixed(1)}%</div>
        <div><strong>Start:</strong> (${logData.telemetry_history[0].position_3d[0].toFixed(1)}, ${logData.telemetry_history[0].position_3d[1].toFixed(1)})</div>
      </div>
    `;
  }

  // Scrubber setup
  const scrubber = document.getElementById('replayScrubber');
  if (scrubber) {
    scrubber.min = 0;
    scrubber.max = logData.telemetry_history.length - 1;
    scrubber.value = 0;
  }

  applyReplayStep(0);
}

function getOutcomeClass(outcome) {
  if (outcome === 'success') return 'status-nominal';
  if (outcome === 'safe_rth') return 'status-override';
  if (outcome === 'controlled_landing') return 'status-warn';
  if (outcome === 'timeout') return 'status-warn';
  return 'status-override';
}

function applyReplayStep(idx) {
  const logData = FLIGHT_LOGS[activeLogKey];
  if (!logData || !logData.telemetry_history[idx]) return;

  replayStep = idx;
  const rec = logData.telemetry_history[idx];

  // Update scrubber and step counters
  const scrubber = document.getElementById('replayScrubber');
  if (scrubber) scrubber.value = idx;

  const stepCountEl = document.getElementById('stepCounter');
  if (stepCountEl) stepCountEl.textContent = `Step: ${rec.step} / ${logData.total_steps}`;

  const replayStepLabel = document.getElementById('replayStepLabel');
  if (replayStepLabel) replayStepLabel.textContent = `Step ${rec.step} / ${logData.total_steps} (${rec.elapsed_time_s.toFixed(1)}s)`;

  // Clock
  const clockEl = document.getElementById('missionClock');
  if (clockEl) clockEl.textContent = `T+${rec.elapsed_time_s.toFixed(1)}s`;

  // Continuous drone coordinates
  const r = rec.position_3d[0];
  const c = rec.position_3d[1];
  const altNorm = rec.position_3d[2];

  const posEl = document.getElementById('valDronePos');
  if (posEl) posEl.textContent = `(${r.toFixed(1)}, ${c.toFixed(1)})`;

  // Flight dynamics metrics
  const altMeters = 780.8 + altNorm * (827.5 - 780.8);
  const clearanceM = rec.terrain_clearance_norm * (827.5 - 780.8);

  const altEl = document.getElementById('valAltitude');
  if (altEl) altEl.textContent = `${altMeters.toFixed(1)} m ASL`;

  const clearEl = document.getElementById('valClearance');
  if (clearEl) {
    let tag = 'SAFE';
    let color = 'var(--accent-green)';
    if (clearanceM < 15.0) {
      tag = 'CRITICAL';
      color = 'var(--accent-red)';
    } else if (clearanceM < 25.0) {
      tag = 'CAUTION';
      color = 'var(--accent-yellow)';
    }
    clearEl.innerHTML = `<span style="color:${color}">${clearanceM.toFixed(1)} m [${tag}]</span>`;
  }

  const airEl = document.getElementById('valAirspeed');
  if (airEl) airEl.textContent = `${rec.airspeed_mps.toFixed(1)} m/s`;

  const gndEl = document.getElementById('valGroundSpeed');
  if (gndEl) gndEl.textContent = `${rec.ground_speed_mps.toFixed(1)} m/s`;

  // Battery & Energy
  const batEl = document.getElementById('valBattery');
  if (batEl) batEl.textContent = `${rec.battery_soc_pct.toFixed(1)}%`;

  const batBar = document.getElementById('batteryBar');
  if (batBar) {
    batBar.style.width = `${rec.battery_soc_pct}%`;
    if (rec.battery_soc_pct > 50) batBar.style.background = 'var(--accent-green)';
    else if (rec.battery_soc_pct > 20) batBar.style.background = 'var(--accent-yellow)';
    else batBar.style.background = 'var(--accent-red)';
  }

  const nrgEl = document.getElementById('valEnergy');
  if (nrgEl) nrgEl.textContent = `${rec.energy_consumed_wh.toFixed(2)} Wh`;

  const pwrEl = document.getElementById('valPower');
  if (pwrEl) pwrEl.textContent = `${rec.power_watts.toFixed(0)} W`;

  // Physics display updates
  const rEnvEl = document.getElementById('valREnv');
  if (rEnvEl) {
    rEnvEl.textContent = rec.r_env.toFixed(3);
    if (rec.r_env > 0.85) rEnvEl.style.color = 'var(--accent-red)';
    else if (rec.r_env > 0.45) rEnvEl.style.color = 'var(--accent-yellow)';
    else rEnvEl.style.color = 'var(--accent-green)';
  }

  const riskBar = document.getElementById('riskBar');
  if (riskBar) {
    const pct = Math.min(100, Math.round(rec.r_env * 100));
    riskBar.style.width = `${pct}%`;
    if (rec.r_env > 0.85) riskBar.style.background = 'var(--accent-red)';
    else if (rec.r_env > 0.45) riskBar.style.background = 'var(--accent-yellow)';
    else riskBar.style.background = 'var(--accent-green)';
  }

  const qEl = document.getElementById('valQ');
  if (qEl) qEl.textContent = `${rec.dynamic_pressure_pa.toFixed(1)} Pa`;

  // Mission State & Safety Badge
  const stateBadge = document.getElementById('missionState');
  const safetyBadge = document.getElementById('safetyBadge');
  const isSafetyIntervention = rec.r_env > 0.85 || rec.dynamic_pressure_pa > 120.0 || rec.outcome === 'safe_rth';

  if (isSafetyIntervention) {
    if (safetyBadge) {
      safetyBadge.className = 'status-badge status-override';
      safetyBadge.textContent = 'OVERRIDE ACTIVE';
    }
    recordSafetyEvent(rec.step, `High Risk (R_env=${rec.r_env.toFixed(2)}, q=${rec.dynamic_pressure_pa.toFixed(1)}Pa)`, 'Route to Goal', 'Execute Safe Return-to-Home', 'Safety Intercept Active');
  } else {
    if (safetyBadge) {
      safetyBadge.className = 'status-badge status-nominal';
      safetyBadge.textContent = 'ENVELOPE: NOMINAL';
    }
  }

  if (stateBadge) {
    if (rec.outcome === 'success') {
      stateBadge.className = 'chip-val status-success';
      stateBadge.textContent = 'MISSION SUCCESS';
    } else if (rec.outcome === 'safe_rth') {
      stateBadge.className = 'chip-val status-rth';
      stateBadge.textContent = 'RETURNING TO BASE';
    } else if (rec.outcome === 'timeout') {
      stateBadge.className = 'chip-val status-warn';
      stateBadge.textContent = 'MISSION TIMEOUT';
    } else if (rec.outcome === 'controlled_landing') {
      stateBadge.className = 'chip-val status-land';
      stateBadge.textContent = 'CONTROLLED LANDING';
    } else if (isSafetyIntervention) {
      stateBadge.className = 'chip-val status-hold';
      stateBadge.textContent = 'SAFETY HOLD / RTH';
    } else {
      stateBadge.className = 'chip-val status-flying';
      stateBadge.textContent = 'FLYING (NOMINAL)';
    }
  }

  // Draw Replay on Canvas
  drawReplayScene(logData, idx);

  // Render Altitude Mini-Chart
  renderAltitudeChart(logData.telemetry_history, idx);
}

function drawReplayScene(logData, currentIdx) {
  if (typeof CTX === 'undefined' || !CTX) return;

  CTX.clearRect(0, 0, CANVAS.width, CANVAS.height);

  // Draw Terrain Cells
  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      const elev = ELEV_MATRIX[r][c];
      CTX.fillStyle = getElevationColor(elev);
      CTX.fillRect(c * CELL_PX, r * CELL_PX, CELL_PX, CELL_PX);
      CTX.strokeStyle = '#ffffff08';
      CTX.strokeRect(c * CELL_PX, r * CELL_PX, CELL_PX, CELL_PX);
    }
  }

  const hist = logData.telemetry_history;

  // Planned / Full Trail (faint dashed cyan)
  CTX.beginPath();
  CTX.strokeStyle = '#38bdf844';
  CTX.lineWidth = 2;
  CTX.setLineDash([4, 4]);
  for (let i = 0; i < hist.length; i++) {
    const pt = hist[i].position_3d;
    const px = pt[1] * CELL_PX + CELL_PX / 2;
    const py = pt[0] * CELL_PX + CELL_PX / 2;
    if (i === 0) CTX.moveTo(px, py);
    else CTX.lineTo(px, py);
  }
  CTX.stroke();
  CTX.setLineDash([]);

  // Elapsed Travelled Trail (Solid cyan glow)
  CTX.beginPath();
  CTX.strokeStyle = '#38bdf8';
  CTX.lineWidth = 3;
  CTX.lineCap = 'round';
  for (let i = 0; i <= currentIdx; i++) {
    const pt = hist[i].position_3d;
    const px = pt[1] * CELL_PX + CELL_PX / 2;
    const py = pt[0] * CELL_PX + CELL_PX / 2;
    if (i === 0) CTX.moveTo(px, py);
    else CTX.lineTo(px, py);
  }
  CTX.stroke();

  // Draw Override / High Risk Markers
  for (let i = 0; i <= currentIdx; i++) {
    if (hist[i].r_env > 0.85 || hist[i].outcome === 'safe_rth') {
      const pt = hist[i].position_3d;
      const px = pt[1] * CELL_PX + CELL_PX / 2;
      const py = pt[0] * CELL_PX + CELL_PX / 2;
      CTX.fillStyle = '#ef4444';
      CTX.beginPath();
      CTX.arc(px, py, 4, 0, 2 * Math.PI);
      CTX.fill();
    }
  }

  // Draw Home / Start Beacon
  const startPt = hist[0].position_3d;
  const sx = startPt[1] * CELL_PX + CELL_PX / 2;
  const sy = startPt[0] * CELL_PX + CELL_PX / 2;
  CTX.strokeStyle = '#38bdf8';
  CTX.lineWidth = 2;
  CTX.beginPath();
  CTX.arc(sx, sy, 8, 0, 2 * Math.PI);
  CTX.stroke();

  // Draw Goal Beacon (Target)
  const lastPt = hist[hist.length - 1].position_3d;
  const gx = lastPt[1] * CELL_PX + CELL_PX / 2;
  const gy = lastPt[0] * CELL_PX + CELL_PX / 2;
  CTX.strokeStyle = '#22c55e';
  CTX.lineWidth = 2;
  CTX.beginPath();
  CTX.arc(gx, gy, 10, 0, 2 * Math.PI);
  CTX.stroke();
  CTX.beginPath();
  CTX.arc(gx, gy, 4, 0, 2 * Math.PI);
  CTX.fillStyle = '#22c55e';
  CTX.fill();

  // Draw Current Drone Position & Heading
  const curr = hist[currentIdx];
  const dx = curr.position_3d[1] * CELL_PX + CELL_PX / 2;
  const dy = curr.position_3d[0] * CELL_PX + CELL_PX / 2;

  CTX.save();
  CTX.translate(dx, dy);

  // Pulsing halo
  CTX.beginPath();
  CTX.arc(0, 0, 14, 0, 2 * Math.PI);
  CTX.fillStyle = '#38bdf833';
  CTX.fill();

  // Heading vector arrow
  if (curr.heading_rad !== undefined) {
    CTX.rotate(curr.heading_rad);
    CTX.strokeStyle = '#ffffff';
    CTX.lineWidth = 2;
    CTX.beginPath();
    CTX.moveTo(0, 0);
    CTX.lineTo(14, 0);
    CTX.lineTo(10, -4);
    CTX.moveTo(14, 0);
    CTX.lineTo(10, 4);
    CTX.stroke();
  }

  // Drone quadcopter body
  CTX.fillStyle = '#38bdf8';
  CTX.beginPath();
  CTX.arc(0, 0, 5, 0, 2 * Math.PI);
  CTX.fill();
  CTX.strokeStyle = '#ffffff';
  CTX.lineWidth = 1.5;
  CTX.stroke();

  CTX.restore();

  // Wind direction compass in top-right
  if (typeof drawWindIndicator === 'function') drawWindIndicator();
}

// ── Replay Playback Controls ────────────────────────────────────────────────
function toggleReplayPlay() {
  if (isReplayPlaying) {
    pauseReplay();
  } else {
    playReplay();
  }
}

function playReplay() {
  const logData = FLIGHT_LOGS[activeLogKey];
  if (!logData) return;

  if (replayStep >= logData.telemetry_history.length - 1) {
    replayStep = 0;
  }

  isReplayPlaying = true;
  const btn = document.getElementById('btnReplayPlay');
  if (btn) {
    btn.textContent = '⏸ Pause';
    btn.classList.add('danger');
    btn.classList.remove('primary');
  }

  clearInterval(replayTimer);
  const intervalMs = Math.max(50, 200 / replaySpeed);
  replayTimer = setInterval(() => {
    if (replayStep < logData.telemetry_history.length - 1) {
      applyReplayStep(replayStep + 1);
    } else {
      pauseReplay();
    }
  }, intervalMs);
}

function pauseReplay() {
  isReplayPlaying = false;
  clearInterval(replayTimer);
  const btn = document.getElementById('btnReplayPlay');
  if (btn) {
    btn.textContent = '▶ Play';
    btn.classList.remove('danger');
    btn.classList.add('primary');
  }
}

function stepReplay(delta) {
  pauseReplay();
  const logData = FLIGHT_LOGS[activeLogKey];
  if (!logData) return;
  const next = Math.max(0, Math.min(logData.telemetry_history.length - 1, replayStep + delta));
  applyReplayStep(next);
}

function setReplaySpeed(spd) {
  replaySpeed = spd;
  ['1', '2', '5'].forEach(s => {
    const b = document.getElementById('btnSpeed_' + s);
    if (b) {
      if (parseInt(s) === spd) b.classList.add('primary');
      else b.classList.remove('primary');
    }
  });
  if (isReplayPlaying) {
    playReplay();
  }
}

// ── SVG Mini Altitude Profile Chart ─────────────────────────────────────────
function renderAltitudeChart(history, currentStepIdx) {
  const svg = document.getElementById('altitudeSvg');
  if (!svg || !history || history.length === 0) return;

  const width = 576;
  const height = 90;
  const padding = { top: 10, bottom: 20, left: 38, right: 15 };
  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;

  const totalSteps = history.length - 1 || 1;

  const minASL = 775.0;
  const maxASL = 835.0;

  let altPath = '';
  let groundPath = '';
  let groundArea = `M ${padding.left} ${height - padding.bottom} `;

  history.forEach((h, i) => {
    const x = padding.left + (i / totalSteps) * plotW;

    // Drone Altitude ASL
    const alt = 780.8 + h.position_3d[2] * (827.5 - 780.8);
    const yAlt = padding.top + plotH * (1 - (alt - minASL) / (maxASL - minASL));

    // Ground elevation under drone
    const groundAlt = alt - (h.terrain_clearance_norm * (827.5 - 780.8));
    const yGround = padding.top + plotH * (1 - (groundAlt - minASL) / (maxASL - minASL));

    if (i === 0) {
      altPath += `M ${x.toFixed(1)} ${yAlt.toFixed(1)} `;
      groundPath += `M ${x.toFixed(1)} ${yGround.toFixed(1)} `;
    } else {
      altPath += `L ${x.toFixed(1)} ${yAlt.toFixed(1)} `;
      groundPath += `L ${x.toFixed(1)} ${yGround.toFixed(1)} `;
    }
    groundArea += `L ${x.toFixed(1)} ${yGround.toFixed(1)} `;
  });

  groundArea += `L ${padding.left + plotW} ${height - padding.bottom} Z`;

  const cursorX = padding.left + (currentStepIdx / totalSteps) * plotW;
  const currH = history[currentStepIdx];
  const currAlt = 780.8 + currH.position_3d[2] * (827.5 - 780.8);
  const cursorY = padding.top + plotH * (1 - (currAlt - minASL) / (maxASL - minASL));

  svg.innerHTML = `
    <!-- Background Guidelines -->
    <line x1="${padding.left}" y1="${padding.top}" x2="${padding.left + plotW}" y2="${padding.top}" stroke="#334155" stroke-dasharray="2,4" />
    <line x1="${padding.left}" y1="${padding.top + plotH/2}" x2="${padding.left + plotW}" y2="${padding.top + plotH/2}" stroke="#334155" stroke-dasharray="2,4" />
    <line x1="${padding.left}" y1="${height - padding.bottom}" x2="${padding.left + plotW}" y2="${height - padding.bottom}" stroke="#475569" />

    <!-- Y-Axis Labels -->
    <text x="${padding.left - 4}" y="${padding.top + 4}" fill="#94a3b8" font-size="8" text-anchor="end">835m</text>
    <text x="${padding.left - 4}" y="${padding.top + plotH/2 + 3}" fill="#94a3b8" font-size="8" text-anchor="end">805m</text>
    <text x="${padding.left - 4}" y="${height - padding.bottom}" fill="#94a3b8" font-size="8" text-anchor="end">775m</text>

    <!-- Ground Terrain Silhouette Area -->
    <path d="${groundArea}" fill="#1e293b" />
    <path d="${groundPath}" fill="none" stroke="#a16207" stroke-width="1.5" />

    <!-- Drone Flight Altitude Line -->
    <path d="${altPath}" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" />

    <!-- Scrub Cursor -->
    <line x1="${cursorX.toFixed(1)}" y1="${padding.top}" x2="${cursorX.toFixed(1)}" y2="${height - padding.bottom}" stroke="#f59e0b" stroke-width="1.5" />
    <circle cx="${cursorX.toFixed(1)}" cy="${cursorY.toFixed(1)}" r="4" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />

    <!-- Legend & Labels -->
    <text x="${padding.left + 5}" y="${padding.top + 10}" fill="#38bdf8" font-size="8" font-weight="bold">Altitude: ${currAlt.toFixed(1)}m</text>
    <text x="${padding.left + 110}" y="${padding.top + 10}" fill="#a16207" font-size="8">Ground: ${(currAlt - currH.terrain_clearance_norm * (827.5 - 780.8)).toFixed(1)}m</text>
    <text x="${padding.left}" y="${height - 4}" fill="#64748b" font-size="8">T=0s</text>
    <text x="${padding.left + plotW}" y="${height - 4}" fill="#64748b" font-size="8" text-anchor="end">T=${currH.elapsed_time_s.toFixed(0)}s</text>
    <text x="${padding.left + plotW/2}" y="${height - 4}" fill="#64748b" font-size="8" text-anchor="middle">Altitude & Terrain Profile (ASL)</text>
  `;
}

// ── Safety Event Card ───────────────────────────────────────────────────────
function recordSafetyEvent(step, trigger, originalAction, overriddenAction, recoveryMode) {
  lastSafetyEvent = { step, trigger, originalAction, overriddenAction, recoveryMode, active: true };
  const card = document.getElementById('safetyEventCard');
  if (!card) return;

  const content = document.getElementById('safetyEventContent');
  if (content) {
    content.innerHTML = `
      <div style="font-size:0.75rem; line-height:1.4;">
        <div style="color:var(--accent-red); font-weight:600; margin-bottom:2px;">⚠️ Step T+${step}: ${trigger}</div>
        <div style="color:var(--text-dim);"><strong>Intended Action:</strong> ${originalAction}</div>
        <div style="color:var(--accent-yellow);"><strong>Overridden To:</strong> ${overriddenAction}</div>
        <div style="color:var(--accent-blue);"><strong>Failsafe Mode:</strong> ${recoveryMode}</div>
      </div>
    `;
  }
}

// ── Multi-Agent Evaluation Benchmark Table & Charts ─────────────────────────
function renderBenchmarkTable() {
  const container = document.getElementById('benchmarkTableContainer');
  if (!container) return;

  let html = `
    <table class="eval-table" role="table" aria-label="Empirical Evaluation Results">
      <thead>
        <tr>
          <th>Condition</th>
          <th>Agent Architecture</th>
          <th>Trials</th>
          <th>Success</th>
          <th>Safe RTH</th>
          <th>Controlled Land</th>
          <th>Crash</th>
          <th>Timeout</th>
          <th>Mean Energy</th>
          <th>Interventions</th>
        </tr>
      </thead>
      <tbody>
  `;

  EVALUATION_SUMMARY.forEach(row => {
    const isAdaptive = row.agent === 'AdaptiveAgent';
    const rowClass = isAdaptive ? 'row-adaptive' : '';

    html += `
      <tr class="${rowClass}">
        <td><strong>${row.bucket}</strong></td>
        <td>${row.agent}</td>
        <td>${row.trials}</td>
        <td><span class="badge-rate ${parseFloat(row.success_rate_pct) > 50 ? 'rate-good' : 'rate-low'}">${row.success_rate_pct}%</span></td>
        <td><span class="badge-rate ${parseFloat(row.safe_rth_rate_pct) > 0 ? 'rate-rth' : ''}">${row.safe_rth_rate_pct}%</span></td>
        <td>${row.controlled_landing_rate_pct}%</td>
        <td><span class="badge-rate rate-zero-crash">${row.crash_rate_pct}%</span></td>
        <td>${row.timeout_rate_pct}%</td>
        <td><strong>${parseFloat(row.mean_energy_wh).toFixed(2)} Wh</strong></td>
        <td>${parseFloat(row.mean_interventions).toFixed(1)}</td>
      </tr>
    `;
  });

  html += `
      </tbody>
    </table>
  `;

  container.innerHTML = html;
}

// Populate UI on load
document.addEventListener('DOMContentLoaded', () => {
  renderBenchmarkTable();
  // Also populate initial altitude chart with calm log
  if (FLIGHT_LOGS.calm) {
    renderAltitudeChart(FLIGHT_LOGS.calm.telemetry_history, 0);
  }
});
