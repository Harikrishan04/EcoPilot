/**
 * demo_ui.js — EcoPilot Phase 2 Avionics & Flight Log Replay Telemetry
 * Provides flight log data replay, altitude chart rendering, mission status tracking,
 * and dynamic benchmark visualization from empirical evaluation results.
 */

// Embedded Phase 2 Telemetry Flight Logs
const FLIGHT_LOGS = {
  calm: {"scenario": "Calm", "seed": 5001, "terminal_outcome": "success", "total_steps": 23, "simulated_flight_time_s": 46.0, "energy_consumed_wh": 4.4939, "battery_end_soc_pct": 94.01, "telemetry_history": [{"step": 0, "elapsed_time_s": 0.0, "position_3d": [12.0, 17.0, 0.4], "position_meters": [510.0, 330.0, 160.0], "velocity_mps": [0.0, 0.0, 0.0], "ground_speed_mps": 0.0, "airspeed_mps": 0.0, "heading_rad": -1.176, "terrain_clearance_norm": 0.3799, "battery_soc_pct": 100.0, "power_watts": 0.0, "energy_consumed_wh": 0.0, "r_env": 0.3164, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 1, "elapsed_time_s": 2.0, "position_3d": [12.4283, 16.5363, 0.4], "position_meters": [496.09, 317.15, 160.0], "velocity_mps": [-6.956, -6.424, 0.0], "ground_speed_mps": 9.469, "airspeed_mps": 12.248, "heading_rad": 3.927, "terrain_clearance_norm": 0.3799, "battery_soc_pct": 99.73, "power_watts": 364.26, "energy_consumed_wh": 0.2024, "r_env": 0.2194, "dynamic_pressure_pa": 81.77, "outcome": "in_flight"}, {"step": 2, "elapsed_time_s": 4.0, "position_3d": [12.8553, 16.0728, 0.4], "position_meters": [482.18, 304.34, 160.0], "velocity_mps": [-6.952, -6.406, 0.0], "ground_speed_mps": 9.453, "airspeed_mps": 12.316, "heading_rad": 3.927, "terrain_clearance_norm": 0.3799, "battery_soc_pct": 99.46, "power_watts": 366.7, "energy_consumed_wh": 0.4061, "r_env": 0.2219, "dynamic_pressure_pa": 82.67, "outcome": "in_flight"}, {"step": 3, "elapsed_time_s": 6.0, "position_3d": [13.2848, 15.6089, 0.4], "position_meters": [468.27, 291.46, 160.0], "velocity_mps": [-6.959, -6.442, 0.0], "ground_speed_mps": 9.483, "airspeed_mps": 12.186, "heading_rad": 3.927, "terrain_clearance_norm": 0.3302, "battery_soc_pct": 99.19, "power_watts": 362.02, "energy_consumed_wh": 0.6072, "r_env": 0.217, "dynamic_pressure_pa": 80.94, "outcome": "in_flight"}, {"step": 4, "elapsed_time_s": 8.0, "position_3d": [13.711, 15.1455, 0.4], "position_meters": [454.37, 278.67, 160.0], "velocity_mps": [-6.95, -6.393, 0.0], "ground_speed_mps": 9.443, "airspeed_mps": 12.362, "heading_rad": 3.927, "terrain_clearance_norm": 0.2766, "battery_soc_pct": 98.92, "power_watts": 368.41, "energy_consumed_wh": 0.8119, "r_env": 0.2237, "dynamic_pressure_pa": 83.3, "outcome": "in_flight"}, {"step": 5, "elapsed_time_s": 10.0, "position_3d": [14.137, 14.6822, 0.4], "position_meters": [440.47, 265.89, 160.0], "velocity_mps": [-6.95, -6.39, 0.0], "ground_speed_mps": 9.441, "airspeed_mps": 12.371, "heading_rad": 3.927, "terrain_clearance_norm": 0.2587, "battery_soc_pct": 98.64, "power_watts": 368.73, "energy_consumed_wh": 1.0167, "r_env": 0.224, "dynamic_pressure_pa": 83.42, "outcome": "in_flight"}, {"step": 6, "elapsed_time_s": 12.0, "position_3d": [14.5623, 14.219, 0.4], "position_meters": [426.57, 253.13, 160.0], "velocity_mps": [-6.948, -6.381, 0.0], "ground_speed_mps": 9.433, "airspeed_mps": 12.405, "heading_rad": 3.927, "terrain_clearance_norm": 0.2587, "battery_soc_pct": 98.37, "power_watts": 369.98, "energy_consumed_wh": 1.2223, "r_env": 0.2253, "dynamic_pressure_pa": 83.88, "outcome": "in_flight"}, {"step": 7, "elapsed_time_s": 14.0, "position_3d": [14.9861, 13.7561, 0.4], "position_meters": [412.68, 240.42, 160.0], "velocity_mps": [-6.944, -6.357, 0.0], "ground_speed_mps": 9.414, "airspeed_mps": 12.492, "heading_rad": 3.927, "terrain_clearance_norm": 0.2587, "battery_soc_pct": 98.09, "power_watts": 373.22, "energy_consumed_wh": 1.4296, "r_env": 0.2286, "dynamic_pressure_pa": 85.06, "outcome": "in_flight"}, {"step": 8, "elapsed_time_s": 16.0, "position_3d": [15.4129, 13.2927, 0.4], "position_meters": [398.78, 227.61, 160.0], "velocity_mps": [-6.952, -6.402, 0.0], "ground_speed_mps": 9.451, "airspeed_mps": 12.328, "heading_rad": 3.927, "terrain_clearance_norm": 0.2587, "battery_soc_pct": 97.82, "power_watts": 367.16, "energy_consumed_wh": 1.6336, "r_env": 0.2224, "dynamic_pressure_pa": 82.84, "outcome": "in_flight"}, {"step": 9, "elapsed_time_s": 18.0, "position_3d": [15.8398, 12.8292, 0.4], "position_meters": [384.88, 214.8, 160.0], "velocity_mps": [-6.952, -6.404, 0.0], "ground_speed_mps": 9.452, "airspeed_mps": 12.322, "heading_rad": 3.927, "terrain_clearance_norm": 0.2587, "battery_soc_pct": 97.55, "power_watts": 366.95, "energy_consumed_wh": 1.8375, "r_env": 0.2222, "dynamic_pressure_pa": 82.76, "outcome": "in_flight"}, {"step": 10, "elapsed_time_s": 20.0, "position_3d": [16.2695, 12.3652, 0.4], "position_meters": [370.96, 201.91, 160.0], "velocity_mps": [-6.959, -6.445, 0.0], "ground_speed_mps": 9.485, "airspeed_mps": 12.173, "heading_rad": 3.927, "terrain_clearance_norm": 0.2587, "battery_soc_pct": 97.28, "power_watts": 361.58, "energy_consumed_wh": 2.0383, "r_env": 0.2166, "dynamic_pressure_pa": 80.77, "outcome": "in_flight"}, {"step": 11, "elapsed_time_s": 22.0, "position_3d": [16.6981, 11.9015, 0.4], "position_meters": [357.04, 189.06, 160.0], "velocity_mps": [-6.956, -6.428, 0.0], "ground_speed_mps": 9.472, "airspeed_mps": 12.235, "heading_rad": 3.927, "terrain_clearance_norm": 0.2587, "battery_soc_pct": 97.01, "power_watts": 363.78, "energy_consumed_wh": 2.2404, "r_env": 0.2189, "dynamic_pressure_pa": 81.59, "outcome": "in_flight"}, {"step": 12, "elapsed_time_s": 24.0, "position_3d": [17.1265, 11.4377, 0.4], "position_meters": [343.13, 176.21, 160.0], "velocity_mps": [-6.956, -6.426, 0.0], "ground_speed_mps": 9.47, "airspeed_mps": 12.241, "heading_rad": 3.927, "terrain_clearance_norm": 0.2546, "battery_soc_pct": 96.74, "power_watts": 363.99, "energy_consumed_wh": 2.4427, "r_env": 0.2191, "dynamic_pressure_pa": 81.67, "outcome": "in_flight"}, {"step": 13, "elapsed_time_s": 26.0, "position_3d": [17.5546, 10.9741, 0.4], "position_meters": [329.22, 163.36, 160.0], "velocity_mps": [-6.955, -6.422, 0.0], "ground_speed_mps": 9.467, "airspeed_mps": 12.257, "heading_rad": 3.927, "terrain_clearance_norm": 0.2464, "battery_soc_pct": 96.47, "power_watts": 364.59, "energy_consumed_wh": 2.6452, "r_env": 0.2197, "dynamic_pressure_pa": 81.89, "outcome": "in_flight"}, {"step": 14, "elapsed_time_s": 28.0, "position_3d": [17.9792, 10.511, 0.4], "position_meters": [315.33, 150.62, 160.0], "velocity_mps": [-6.946, -6.369, 0.0], "ground_speed_mps": 9.424, "airspeed_mps": 12.448, "heading_rad": 3.927, "terrain_clearance_norm": 0.2369, "battery_soc_pct": 96.2, "power_watts": 371.57, "energy_consumed_wh": 2.8516, "r_env": 0.2269, "dynamic_pressure_pa": 84.46, "outcome": "in_flight"}, {"step": 15, "elapsed_time_s": 30.0, "position_3d": [18.4032, 10.0481, 0.4], "position_meters": [301.44, 137.9, 160.0], "velocity_mps": [-6.944, -6.361, 0.0], "ground_speed_mps": 9.417, "airspeed_mps": 12.478, "heading_rad": 3.927, "terrain_clearance_norm": 0.2364, "battery_soc_pct": 95.92, "power_watts": 372.69, "energy_consumed_wh": 3.0587, "r_env": 0.228, "dynamic_pressure_pa": 84.87, "outcome": "in_flight"}, {"step": 16, "elapsed_time_s": 32.0, "position_3d": [18.8248, 9.5855, 0.4], "position_meters": [287.57, 125.26, 160.0], "velocity_mps": [-6.938, -6.323, 0.0], "ground_speed_mps": 9.387, "airspeed_mps": 12.613, "heading_rad": 3.927, "terrain_clearance_norm": 0.2364, "battery_soc_pct": 95.64, "power_watts": 377.8, "energy_consumed_wh": 3.2686, "r_env": 0.2331, "dynamic_pressure_pa": 86.72, "outcome": "in_flight"}, {"step": 17, "elapsed_time_s": 34.0, "position_3d": [19.2479, 9.1228, 0.4], "position_meters": [273.68, 112.56, 160.0], "velocity_mps": [-6.942, -6.347, 0.0], "ground_speed_mps": 9.406, "airspeed_mps": 12.529, "heading_rad": 3.927, "terrain_clearance_norm": 0.2364, "battery_soc_pct": 95.36, "power_watts": 374.59, "energy_consumed_wh": 3.4767, "r_env": 0.2299, "dynamic_pressure_pa": 85.56, "outcome": "in_flight"}, {"step": 18, "elapsed_time_s": 36.0, "position_3d": [18.7276, 8.6601, 0.4], "position_meters": [259.8, 128.17, 160.0], "velocity_mps": [-6.94, 7.804, 0.0], "ground_speed_mps": 10.444, "airspeed_mps": 8.649, "heading_rad": 5.4978, "terrain_clearance_norm": 0.2468, "battery_soc_pct": 95.17, "power_watts": 269.03, "energy_consumed_wh": 3.6261, "r_env": 0.231, "dynamic_pressure_pa": 40.77, "outcome": "in_flight"}, {"step": 19, "elapsed_time_s": 38.0, "position_3d": [18.2046, 8.1979, 0.4], "position_meters": [245.94, 143.86, 160.0], "velocity_mps": [-6.933, 7.845, 0.0], "ground_speed_mps": 10.469, "airspeed_mps": 8.598, "heading_rad": 5.4978, "terrain_clearance_norm": 0.2608, "battery_soc_pct": 94.97, "power_watts": 268.11, "energy_consumed_wh": 3.7751, "r_env": 0.2366, "dynamic_pressure_pa": 40.29, "outcome": "in_flight"}, {"step": 20, "elapsed_time_s": 40.0, "position_3d": [18.1519, 7.5406, 0.4], "position_meters": [226.22, 145.44, 160.0], "velocity_mps": [-9.859, 0.791, 0.0], "ground_speed_mps": 9.891, "airspeed_mps": 11.028, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2668, "battery_soc_pct": 94.73, "power_watts": 324.57, "energy_consumed_wh": 3.9554, "r_env": 0.2389, "dynamic_pressure_pa": 66.29, "outcome": "in_flight"}, {"step": 21, "elapsed_time_s": 42.0, "position_3d": [18.0982, 6.8835, 0.4], "position_meters": [206.51, 147.05, 160.0], "velocity_mps": [-9.856, 0.805, 0.0], "ground_speed_mps": 9.889, "airspeed_mps": 11.054, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2668, "battery_soc_pct": 94.49, "power_watts": 325.31, "energy_consumed_wh": 4.1361, "r_env": 0.2408, "dynamic_pressure_pa": 66.6, "outcome": "in_flight"}, {"step": 22, "elapsed_time_s": 44.0, "position_3d": [18.0489, 6.2256, 0.4], "position_meters": [186.77, 148.53, 160.0], "velocity_mps": [-9.868, 0.74, 0.0], "ground_speed_mps": 9.896, "airspeed_mps": 10.936, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2668, "battery_soc_pct": 94.25, "power_watts": 321.9, "energy_consumed_wh": 4.315, "r_env": 0.232, "dynamic_pressure_pa": 65.19, "outcome": "in_flight"}, {"step": 23, "elapsed_time_s": 46.0, "position_3d": [17.9992, 5.5678, 0.4], "position_meters": [167.03, 150.02, 160.0], "velocity_mps": [-9.867, 0.745, 0.0], "ground_speed_mps": 9.895, "airspeed_mps": 10.945, "heading_rad": 4.7124, "terrain_clearance_norm": 0.288, "battery_soc_pct": 94.01, "power_watts": 322.15, "energy_consumed_wh": 4.4939, "r_env": 0.2327, "dynamic_pressure_pa": 65.29, "outcome": "success"}]},
  moderate: {"scenario": "Moderate", "seed": 5002, "terminal_outcome": "success", "total_steps": 14, "simulated_flight_time_s": 28.0, "energy_consumed_wh": 2.0462, "battery_end_soc_pct": 97.27, "telemetry_history": [{"step": 0, "elapsed_time_s": 0.0, "position_3d": [15.0, 19.0, 0.4], "position_meters": [570.0, 240.0, 160.0], "velocity_mps": [0.0, 0.0, 0.0], "ground_speed_mps": 0.0, "airspeed_mps": 0.0, "heading_rad": -2.1294, "terrain_clearance_norm": 0.3775, "battery_soc_pct": 100.0, "power_watts": 0.0, "energy_consumed_wh": 0.0, "r_env": 0.4025, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 1, "elapsed_time_s": 2.0, "position_3d": [14.3326, 18.911, 0.4], "position_meters": [567.33, 260.02, 160.0], "velocity_mps": [-1.334, 10.011, 0.0], "ground_speed_mps": 10.099, "airspeed_mps": 11.297, "heading_rad": 0.0, "terrain_clearance_norm": 0.3736, "battery_soc_pct": 99.75, "power_watts": 338.58, "energy_consumed_wh": 0.1881, "r_env": 0.4143, "dynamic_pressure_pa": 67.57, "outcome": "in_flight"}, {"step": 2, "elapsed_time_s": 4.0, "position_3d": [13.6652, 18.8206, 0.4], "position_meters": [564.62, 280.04, 160.0], "velocity_mps": [-1.357, 10.011, 0.0], "ground_speed_mps": 10.103, "airspeed_mps": 11.34, "heading_rad": 0.0, "terrain_clearance_norm": 0.3664, "battery_soc_pct": 99.5, "power_watts": 339.89, "energy_consumed_wh": 0.3769, "r_env": 0.4174, "dynamic_pressure_pa": 68.08, "outcome": "in_flight"}, {"step": 3, "elapsed_time_s": 6.0, "position_3d": [12.9978, 18.7273, 0.4], "position_meters": [561.82, 300.07, 160.0], "velocity_mps": [-1.399, 10.011, 0.0], "ground_speed_mps": 10.109, "airspeed_mps": 11.42, "heading_rad": 0.0, "terrain_clearance_norm": 0.3623, "battery_soc_pct": 99.24, "power_watts": 342.39, "energy_consumed_wh": 0.5671, "r_env": 0.423, "dynamic_pressure_pa": 69.05, "outcome": "in_flight"}, {"step": 4, "elapsed_time_s": 8.0, "position_3d": [12.997, 17.9711, 0.4], "position_meters": [539.13, 300.09, 160.0], "velocity_mps": [-11.343, 0.011, 0.0], "ground_speed_mps": 11.343, "airspeed_mps": 4.63, "heading_rad": 4.7124, "terrain_clearance_norm": 0.3799, "battery_soc_pct": 99.07, "power_watts": 231.18, "energy_consumed_wh": 0.6956, "r_env": 0.4154, "dynamic_pressure_pa": 11.35, "outcome": "in_flight"}, {"step": 5, "elapsed_time_s": 10.0, "position_3d": [12.5249, 17.4112, 0.4], "position_meters": [522.33, 314.25, 160.0], "velocity_mps": [-8.399, 7.082, 0.0], "ground_speed_mps": 10.986, "airspeed_mps": 7.245, "heading_rad": 5.4978, "terrain_clearance_norm": 0.3799, "battery_soc_pct": 98.88, "power_watts": 253.66, "energy_consumed_wh": 0.8365, "r_env": 0.4135, "dynamic_pressure_pa": 27.79, "outcome": "in_flight"}, {"step": 6, "elapsed_time_s": 12.0, "position_3d": [12.5242, 16.6601, 0.4], "position_meters": [499.8, 314.27, 160.0], "velocity_mps": [-11.267, 0.01, 0.0], "ground_speed_mps": 11.267, "airspeed_mps": 4.934, "heading_rad": 4.7124, "terrain_clearance_norm": 0.3799, "battery_soc_pct": 98.71, "power_watts": 232.85, "energy_consumed_wh": 0.9659, "r_env": 0.4053, "dynamic_pressure_pa": 12.89, "outcome": "in_flight"}, {"step": 7, "elapsed_time_s": 14.0, "position_3d": [12.0521, 16.1039, 0.4], "position_meters": [483.12, 328.44, 160.0], "velocity_mps": [-8.343, 7.081, 0.0], "ground_speed_mps": 10.943, "airspeed_mps": 7.304, "heading_rad": 5.4978, "terrain_clearance_norm": 0.3799, "battery_soc_pct": 98.52, "power_watts": 254.41, "energy_consumed_wh": 1.1072, "r_env": 0.406, "dynamic_pressure_pa": 28.25, "outcome": "in_flight"}, {"step": 8, "elapsed_time_s": 16.0, "position_3d": [12.0514, 15.3526, 0.4], "position_meters": [460.58, 328.46, 160.0], "velocity_mps": [-11.269, 0.01, 0.0], "ground_speed_mps": 11.269, "airspeed_mps": 4.925, "heading_rad": 4.7124, "terrain_clearance_norm": 0.3147, "battery_soc_pct": 98.35, "power_watts": 232.79, "energy_consumed_wh": 1.2365, "r_env": 0.4056, "dynamic_pressure_pa": 12.84, "outcome": "in_flight"}, {"step": 9, "elapsed_time_s": 18.0, "position_3d": [11.5794, 14.7998, 0.4], "position_meters": [443.99, 342.62, 160.0], "velocity_mps": [-8.292, 7.081, 0.0], "ground_speed_mps": 10.904, "airspeed_mps": 7.363, "heading_rad": 5.4978, "terrain_clearance_norm": 0.2792, "battery_soc_pct": 98.16, "power_watts": 255.18, "energy_consumed_wh": 1.3783, "r_env": 0.3992, "dynamic_pressure_pa": 28.71, "outcome": "in_flight"}, {"step": 10, "elapsed_time_s": 20.0, "position_3d": [11.1073, 14.2514, 0.4], "position_meters": [427.54, 356.78, 160.0], "velocity_mps": [-8.226, 7.08, 0.0], "ground_speed_mps": 10.853, "airspeed_mps": 7.449, "heading_rad": 5.4978, "terrain_clearance_norm": 0.2792, "battery_soc_pct": 97.97, "power_watts": 256.3, "energy_consumed_wh": 1.5207, "r_env": 0.3904, "dynamic_pressure_pa": 29.37, "outcome": "in_flight"}, {"step": 11, "elapsed_time_s": 22.0, "position_3d": [11.1067, 13.5104, 0.4], "position_meters": [405.31, 356.8, 160.0], "velocity_mps": [-11.115, 0.009, 0.0], "ground_speed_mps": 11.115, "airspeed_mps": 5.54, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2792, "battery_soc_pct": 97.8, "power_watts": 236.84, "energy_consumed_wh": 1.6523, "r_env": 0.3851, "dynamic_pressure_pa": 16.25, "outcome": "in_flight"}, {"step": 12, "elapsed_time_s": 24.0, "position_3d": [11.1061, 12.7681, 0.4], "position_meters": [383.04, 356.82, 160.0], "velocity_mps": [-11.135, 0.009, 0.0], "ground_speed_mps": 11.135, "airspeed_mps": 5.461, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2792, "battery_soc_pct": 97.62, "power_watts": 236.27, "energy_consumed_wh": 1.7835, "r_env": 0.3877, "dynamic_pressure_pa": 15.79, "outcome": "in_flight"}, {"step": 13, "elapsed_time_s": 26.0, "position_3d": [11.1055, 12.0272, 0.4], "position_meters": [360.82, 356.83, 160.0], "velocity_mps": [-11.114, 0.009, 0.0], "ground_speed_mps": 11.114, "airspeed_mps": 5.544, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2792, "battery_soc_pct": 97.45, "power_watts": 236.87, "energy_consumed_wh": 1.9151, "r_env": 0.385, "dynamic_pressure_pa": 16.27, "outcome": "in_flight"}, {"step": 14, "elapsed_time_s": 28.0, "position_3d": [11.1049, 11.2841, 0.4], "position_meters": [338.52, 356.85, 160.0], "velocity_mps": [-11.146, 0.009, 0.0], "ground_speed_mps": 11.146, "airspeed_mps": 5.416, "heading_rad": 4.7124, "terrain_clearance_norm": 0.2515, "battery_soc_pct": 97.27, "power_watts": 235.95, "energy_consumed_wh": 2.0462, "r_env": 0.3892, "dynamic_pressure_pa": 15.53, "outcome": "success"}]},
  emergency: {"scenario": "Severe", "seed": 5003, "terminal_outcome": "timeout", "total_steps": 120, "simulated_flight_time_s": 240.0, "energy_consumed_wh": 38.528, "battery_end_soc_pct": 48.63, "telemetry_history": [{"step": 0, "elapsed_time_s": 0.0, "position_3d": [7.0, 7.0, 0.4], "position_meters": [210.0, 480.0, 160.0], "velocity_mps": [0.0, 0.0, 0.0], "ground_speed_mps": 0.0, "airspeed_mps": 0.0, "heading_rad": 1.989, "terrain_clearance_norm": 0.2777, "battery_soc_pct": 100.0, "power_watts": 0.0, "energy_consumed_wh": 0.0, "r_env": 0.5141, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 1, "elapsed_time_s": 2.0, "position_3d": [6.2, 6.9993, 0.4], "position_meters": [209.98, 504.0, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.064, "heading_rad": 0.0, "terrain_clearance_norm": 0.2939, "battery_soc_pct": 99.83, "power_watts": 229.77, "energy_consumed_wh": 0.1277, "r_env": 0.8309, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 2, "elapsed_time_s": 4.0, "position_3d": [5.4, 6.9985, 0.4], "position_meters": [209.96, 528.0, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.052, "heading_rad": 0.0, "terrain_clearance_norm": 0.298, "battery_soc_pct": 99.66, "power_watts": 229.77, "energy_consumed_wh": 0.2553, "r_env": 0.829, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 3, "elapsed_time_s": 6.0, "position_3d": [4.6, 6.9978, 0.4], "position_meters": [209.93, 552.0, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.054, "heading_rad": 0.0, "terrain_clearance_norm": 0.298, "battery_soc_pct": 99.49, "power_watts": 229.77, "energy_consumed_wh": 0.383, "r_env": 0.8289, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 4, "elapsed_time_s": 8.0, "position_3d": [3.8, 6.9971, 0.4], "position_meters": [209.91, 576.0, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.212, "heading_rad": 0.0, "terrain_clearance_norm": 0.298, "battery_soc_pct": 99.32, "power_watts": 229.77, "energy_consumed_wh": 0.5106, "r_env": 0.8241, "dynamic_pressure_pa": 0.02, "outcome": "in_flight"}, {"step": 5, "elapsed_time_s": 10.0, "position_3d": [3.0, 6.9964, 0.4], "position_meters": [209.89, 600.0, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.119, "heading_rad": 0.0, "terrain_clearance_norm": 0.298, "battery_soc_pct": 99.15, "power_watts": 229.77, "energy_consumed_wh": 0.6383, "r_env": 0.8267, "dynamic_pressure_pa": 0.01, "outcome": "in_flight"}, {"step": 6, "elapsed_time_s": 12.0, "position_3d": [2.2, 6.9957, 0.4], "position_meters": [209.87, 624.0, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.093, "heading_rad": 0.0, "terrain_clearance_norm": 0.3247, "battery_soc_pct": 98.98, "power_watts": 229.77, "energy_consumed_wh": 0.7659, "r_env": 0.8318, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 7, "elapsed_time_s": 14.0, "position_3d": [1.4, 6.9949, 0.4], "position_meters": [209.85, 648.0, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.085, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 98.81, "power_watts": 229.77, "energy_consumed_wh": 0.8936, "r_env": 0.8316, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 8, "elapsed_time_s": 16.0, "position_3d": [0.6, 6.9942, 0.4], "position_meters": [209.83, 672.0, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.099, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 98.64, "power_watts": 229.77, "energy_consumed_wh": 1.0212, "r_env": 0.832, "dynamic_pressure_pa": 0.01, "outcome": "in_flight"}, {"step": 9, "elapsed_time_s": 18.0, "position_3d": [1.1058, 6.9934, 0.4], "position_meters": [209.8, 656.83, 160.0], "velocity_mps": [-0.011, -7.587, 0.0], "ground_speed_mps": 7.587, "airspeed_mps": 19.654, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 98.02, "power_watts": 837.12, "energy_consumed_wh": 1.4863, "r_env": 0.8314, "dynamic_pressure_pa": 198.29, "outcome": "in_flight"}, {"step": 10, "elapsed_time_s": 20.0, "position_3d": [0.3058, 6.9927, 0.4], "position_meters": [209.78, 680.83, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.049, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 97.85, "power_watts": 229.77, "energy_consumed_wh": 1.6139, "r_env": 0.8301, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 11, "elapsed_time_s": 22.0, "position_3d": [0.815, 6.992, 0.4], "position_meters": [209.76, 665.55, 160.0], "velocity_mps": [-0.011, -7.638, 0.0], "ground_speed_mps": 7.638, "airspeed_mps": 19.447, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 97.24, "power_watts": 818.11, "energy_consumed_wh": 2.0684, "r_env": 0.8245, "dynamic_pressure_pa": 194.13, "outcome": "in_flight"}, {"step": 12, "elapsed_time_s": 24.0, "position_3d": [1.3241, 6.9912, 0.4], "position_meters": [209.74, 650.28, 160.0], "velocity_mps": [-0.011, -7.636, 0.0], "ground_speed_mps": 7.636, "airspeed_mps": 19.454, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 96.64, "power_watts": 818.82, "energy_consumed_wh": 2.5233, "r_env": 0.8248, "dynamic_pressure_pa": 194.28, "outcome": "in_flight"}, {"step": 13, "elapsed_time_s": 26.0, "position_3d": [0.5241, 6.9905, 0.4], "position_meters": [209.72, 674.28, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.089, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 96.47, "power_watts": 229.77, "energy_consumed_wh": 2.651, "r_env": 0.8317, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 14, "elapsed_time_s": 28.0, "position_3d": [1.0295, 6.9898, 0.4], "position_meters": [209.69, 659.12, 160.0], "velocity_mps": [-0.011, -7.581, 0.0], "ground_speed_mps": 7.581, "airspeed_mps": 19.675, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 95.84, "power_watts": 839.11, "energy_consumed_wh": 3.1172, "r_env": 0.8322, "dynamic_pressure_pa": 198.72, "outcome": "in_flight"}, {"step": 15, "elapsed_time_s": 30.0, "position_3d": [0.2295, 6.989, 0.4], "position_meters": [209.67, 683.11, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.131, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 95.67, "power_watts": 229.77, "energy_consumed_wh": 3.2448, "r_env": 0.8329, "dynamic_pressure_pa": 0.01, "outcome": "in_flight"}, {"step": 16, "elapsed_time_s": 32.0, "position_3d": [0.7342, 6.9883, 0.4], "position_meters": [209.65, 667.97, 160.0], "velocity_mps": [-0.011, -7.571, 0.0], "ground_speed_mps": 7.571, "airspeed_mps": 19.716, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 95.05, "power_watts": 842.87, "energy_consumed_wh": 3.7131, "r_env": 0.8335, "dynamic_pressure_pa": 199.54, "outcome": "in_flight"}, {"step": 17, "elapsed_time_s": 34.0, "position_3d": [1.2386, 6.9875, 0.4], "position_meters": [209.62, 652.84, 160.0], "velocity_mps": [-0.011, -7.566, 0.0], "ground_speed_mps": 7.566, "airspeed_mps": 19.737, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 94.42, "power_watts": 844.85, "energy_consumed_wh": 4.1824, "r_env": 0.8342, "dynamic_pressure_pa": 199.97, "outcome": "in_flight"}, {"step": 18, "elapsed_time_s": 36.0, "position_3d": [0.4386, 6.9868, 0.4], "position_meters": [209.6, 676.84, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.334, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 94.25, "power_watts": 229.78, "energy_consumed_wh": 4.3101, "r_env": 0.8385, "dynamic_pressure_pa": 0.06, "outcome": "in_flight"}, {"step": 19, "elapsed_time_s": 38.0, "position_3d": [0.9428, 6.986, 0.4], "position_meters": [209.58, 661.72, 160.0], "velocity_mps": [-0.011, -7.563, 0.0], "ground_speed_mps": 7.563, "airspeed_mps": 19.748, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 93.63, "power_watts": 845.87, "energy_consumed_wh": 4.78, "r_env": 0.8346, "dynamic_pressure_pa": 200.19, "outcome": "in_flight"}, {"step": 20, "elapsed_time_s": 40.0, "position_3d": [1.4428, 6.9852, 0.4], "position_meters": [209.56, 646.72, 160.0], "velocity_mps": [-0.012, -7.499, 0.0], "ground_speed_mps": 7.499, "airspeed_mps": 20.003, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 92.98, "power_watts": 870.08, "energy_consumed_wh": 5.2634, "r_env": 0.8431, "dynamic_pressure_pa": 205.4, "outcome": "in_flight"}, {"step": 21, "elapsed_time_s": 42.0, "position_3d": [0.6428, 6.9845, 0.4], "position_meters": [209.53, 670.72, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.686, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 92.81, "power_watts": 229.8, "energy_consumed_wh": 5.3911, "r_env": 0.8479, "dynamic_pressure_pa": 0.24, "outcome": "in_flight"}, {"step": 22, "elapsed_time_s": 44.0, "position_3d": [1.1404, 6.9837, 0.4], "position_meters": [209.51, 655.79, 160.0], "velocity_mps": [-0.012, -7.464, 0.0], "ground_speed_mps": 7.464, "airspeed_mps": 20.143, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 92.16, "power_watts": 883.58, "energy_consumed_wh": 5.8819, "r_env": 0.8477, "dynamic_pressure_pa": 208.27, "outcome": "in_flight"}, {"step": 23, "elapsed_time_s": 46.0, "position_3d": [0.3404, 6.9829, 0.4], "position_meters": [209.49, 679.79, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.545, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 91.99, "power_watts": 229.79, "energy_consumed_wh": 6.0096, "r_env": 0.8441, "dynamic_pressure_pa": 0.15, "outcome": "in_flight"}, {"step": 24, "elapsed_time_s": 48.0, "position_3d": [0.8391, 6.9821, 0.4], "position_meters": [209.46, 664.83, 160.0], "velocity_mps": [-0.012, -7.48, 0.0], "ground_speed_mps": 7.48, "airspeed_mps": 20.081, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 91.34, "power_watts": 877.55, "energy_consumed_wh": 6.4971, "r_env": 0.8457, "dynamic_pressure_pa": 206.99, "outcome": "in_flight"}, {"step": 25, "elapsed_time_s": 50.0, "position_3d": [1.3378, 6.9813, 0.4], "position_meters": [209.44, 649.87, 160.0], "velocity_mps": [-0.012, -7.481, 0.0], "ground_speed_mps": 7.481, "airspeed_mps": 20.075, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 90.69, "power_watts": 877.0, "energy_consumed_wh": 6.9844, "r_env": 0.8455, "dynamic_pressure_pa": 206.88, "outcome": "in_flight"}, {"step": 26, "elapsed_time_s": 52.0, "position_3d": [0.5378, 6.9806, 0.4], "position_meters": [209.42, 673.87, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.536, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 90.52, "power_watts": 229.79, "energy_consumed_wh": 7.112, "r_env": 0.8439, "dynamic_pressure_pa": 0.15, "outcome": "in_flight"}, {"step": 27, "elapsed_time_s": 54.0, "position_3d": [1.0384, 6.9798, 0.4], "position_meters": [209.39, 658.85, 160.0], "velocity_mps": [-0.012, -7.509, 0.0], "ground_speed_mps": 7.509, "airspeed_mps": 19.965, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 89.88, "power_watts": 866.4, "energy_consumed_wh": 7.5933, "r_env": 0.8418, "dynamic_pressure_pa": 204.61, "outcome": "in_flight"}, {"step": 28, "elapsed_time_s": 56.0, "position_3d": [0.2384, 6.9791, 0.4], "position_meters": [209.37, 682.85, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.356, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 89.71, "power_watts": 229.78, "energy_consumed_wh": 7.721, "r_env": 0.8391, "dynamic_pressure_pa": 0.07, "outcome": "in_flight"}, {"step": 29, "elapsed_time_s": 58.0, "position_3d": [0.741, 6.9783, 0.4], "position_meters": [209.35, 667.77, 160.0], "velocity_mps": [-0.012, -7.539, 0.0], "ground_speed_mps": 7.539, "airspeed_mps": 19.845, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 89.07, "power_watts": 854.98, "energy_consumed_wh": 8.196, "r_env": 0.8378, "dynamic_pressure_pa": 202.16, "outcome": "in_flight"}, {"step": 30, "elapsed_time_s": 60.0, "position_3d": [1.244, 6.9775, 0.4], "position_meters": [209.33, 652.68, 160.0], "velocity_mps": [-0.012, -7.545, 0.0], "ground_speed_mps": 7.545, "airspeed_mps": 19.821, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 88.44, "power_watts": 852.7, "energy_consumed_wh": 8.6697, "r_env": 0.837, "dynamic_pressure_pa": 201.66, "outcome": "in_flight"}, {"step": 31, "elapsed_time_s": 62.0, "position_3d": [0.444, 6.9768, 0.4], "position_meters": [209.3, 676.68, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.049, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 88.27, "power_watts": 229.77, "energy_consumed_wh": 8.7974, "r_env": 0.8301, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 32, "elapsed_time_s": 64.0, "position_3d": [0.9487, 6.976, 0.4], "position_meters": [209.28, 661.54, 160.0], "velocity_mps": [-0.011, -7.57, 0.0], "ground_speed_mps": 7.57, "airspeed_mps": 19.719, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 87.65, "power_watts": 843.18, "energy_consumed_wh": 9.2658, "r_env": 0.8336, "dynamic_pressure_pa": 199.6, "outcome": "in_flight"}, {"step": 33, "elapsed_time_s": 66.0, "position_3d": [1.4525, 6.9753, 0.4], "position_meters": [209.26, 646.42, 160.0], "velocity_mps": [-0.011, -7.558, 0.0], "ground_speed_mps": 7.558, "airspeed_mps": 19.768, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 87.02, "power_watts": 847.8, "energy_consumed_wh": 9.7368, "r_env": 0.8353, "dynamic_pressure_pa": 200.61, "outcome": "in_flight"}, {"step": 34, "elapsed_time_s": 68.0, "position_3d": [0.6525, 6.9745, 0.4], "position_meters": [209.24, 670.42, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.389, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 86.85, "power_watts": 229.78, "energy_consumed_wh": 9.8645, "r_env": 0.8399, "dynamic_pressure_pa": 0.08, "outcome": "in_flight"}, {"step": 35, "elapsed_time_s": 70.0, "position_3d": [1.1535, 6.9738, 0.4], "position_meters": [209.21, 655.4, 160.0], "velocity_mps": [-0.012, -7.514, 0.0], "ground_speed_mps": 7.514, "airspeed_mps": 19.944, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 86.21, "power_watts": 864.38, "energy_consumed_wh": 10.3447, "r_env": 0.8411, "dynamic_pressure_pa": 204.18, "outcome": "in_flight"}, {"step": 36, "elapsed_time_s": 72.0, "position_3d": [0.3535, 6.973, 0.4], "position_meters": [209.19, 679.4, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.575, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 86.04, "power_watts": 229.79, "energy_consumed_wh": 10.4723, "r_env": 0.8449, "dynamic_pressure_pa": 0.17, "outcome": "in_flight"}, {"step": 37, "elapsed_time_s": 74.0, "position_3d": [0.8548, 6.9722, 0.4], "position_meters": [209.17, 664.36, 160.0], "velocity_mps": [-0.012, -7.52, 0.0], "ground_speed_mps": 7.52, "airspeed_mps": 19.918, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 85.4, "power_watts": 861.95, "energy_consumed_wh": 10.9512, "r_env": 0.8403, "dynamic_pressure_pa": 203.66, "outcome": "in_flight"}, {"step": 38, "elapsed_time_s": 76.0, "position_3d": [1.3584, 6.9715, 0.4], "position_meters": [209.14, 649.25, 160.0], "velocity_mps": [-0.011, -7.554, 0.0], "ground_speed_mps": 7.554, "airspeed_mps": 19.783, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 84.77, "power_watts": 849.17, "energy_consumed_wh": 11.4229, "r_env": 0.8357, "dynamic_pressure_pa": 200.9, "outcome": "in_flight"}, {"step": 39, "elapsed_time_s": 78.0, "position_3d": [0.5584, 6.9707, 0.4], "position_meters": [209.12, 673.25, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.052, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 84.6, "power_watts": 229.77, "energy_consumed_wh": 11.5506, "r_env": 0.8303, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 40, "elapsed_time_s": 80.0, "position_3d": [1.0657, 6.97, 0.4], "position_meters": [209.1, 658.03, 160.0], "velocity_mps": [-0.011, -7.61, 0.0], "ground_speed_mps": 7.61, "airspeed_mps": 19.562, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 83.99, "power_watts": 828.6, "energy_consumed_wh": 12.0109, "r_env": 0.8284, "dynamic_pressure_pa": 196.43, "outcome": "in_flight"}, {"step": 41, "elapsed_time_s": 82.0, "position_3d": [0.2657, 6.9693, 0.4], "position_meters": [209.08, 682.03, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.056, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 83.82, "power_watts": 229.77, "energy_consumed_wh": 12.1386, "r_env": 0.8288, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 42, "elapsed_time_s": 84.0, "position_3d": [0.7732, 6.9685, 0.4], "position_meters": [209.06, 666.8, 160.0], "velocity_mps": [-0.011, -7.612, 0.0], "ground_speed_mps": 7.612, "airspeed_mps": 19.55, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 83.2, "power_watts": 827.57, "energy_consumed_wh": 12.5983, "r_env": 0.828, "dynamic_pressure_pa": 196.2, "outcome": "in_flight"}, {"step": 43, "elapsed_time_s": 86.0, "position_3d": [1.2777, 6.9678, 0.4], "position_meters": [209.03, 651.67, 160.0], "velocity_mps": [-0.011, -7.567, 0.0], "ground_speed_mps": 7.567, "airspeed_mps": 19.731, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 82.58, "power_watts": 844.34, "energy_consumed_wh": 13.0674, "r_env": 0.834, "dynamic_pressure_pa": 199.86, "outcome": "in_flight"}, {"step": 44, "elapsed_time_s": 88.0, "position_3d": [0.4777, 6.967, 0.4], "position_meters": [209.01, 675.67, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.079, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 82.41, "power_watts": 229.77, "energy_consumed_wh": 13.1951, "r_env": 0.8279, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 45, "elapsed_time_s": 90.0, "position_3d": [0.9885, 6.9663, 0.4], "position_meters": [208.99, 660.35, 160.0], "velocity_mps": [-0.011, -7.661, 0.0], "ground_speed_mps": 7.661, "airspeed_mps": 19.354, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 81.81, "power_watts": 809.78, "energy_consumed_wh": 13.6449, "r_env": 0.8215, "dynamic_pressure_pa": 192.29, "outcome": "in_flight"}, {"step": 46, "elapsed_time_s": 92.0, "position_3d": [1.4978, 6.9656, 0.4], "position_meters": [208.97, 645.06, 160.0], "velocity_mps": [-0.011, -7.64, 0.0], "ground_speed_mps": 7.64, "airspeed_mps": 19.439, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 81.2, "power_watts": 817.39, "energy_consumed_wh": 14.099, "r_env": 0.8243, "dynamic_pressure_pa": 193.97, "outcome": "in_flight"}, {"step": 47, "elapsed_time_s": 94.0, "position_3d": [0.6978, 6.9648, 0.4], "position_meters": [208.94, 669.06, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.064, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 81.03, "power_watts": 229.77, "energy_consumed_wh": 14.2267, "r_env": 0.8308, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 48, "elapsed_time_s": 96.0, "position_3d": [1.2036, 6.9641, 0.4], "position_meters": [208.92, 653.89, 160.0], "velocity_mps": [-0.011, -7.586, 0.0], "ground_speed_mps": 7.586, "airspeed_mps": 19.656, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 80.41, "power_watts": 837.32, "energy_consumed_wh": 14.6919, "r_env": 0.8315, "dynamic_pressure_pa": 198.33, "outcome": "in_flight"}, {"step": 49, "elapsed_time_s": 98.0, "position_3d": [0.4036, 6.9633, 0.4], "position_meters": [208.9, 677.89, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.095, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 80.24, "power_watts": 229.77, "energy_consumed_wh": 14.8195, "r_env": 0.8319, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 50, "elapsed_time_s": 100.0, "position_3d": [0.9104, 6.9626, 0.4], "position_meters": [208.88, 662.69, 160.0], "velocity_mps": [-0.011, -7.602, 0.0], "ground_speed_mps": 7.602, "airspeed_mps": 19.592, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 79.62, "power_watts": 831.39, "energy_consumed_wh": 15.2814, "r_env": 0.8294, "dynamic_pressure_pa": 197.04, "outcome": "in_flight"}, {"step": 51, "elapsed_time_s": 102.0, "position_3d": [1.4149, 6.9618, 0.4], "position_meters": [208.86, 647.55, 160.0], "velocity_mps": [-0.011, -7.568, 0.0], "ground_speed_mps": 7.568, "airspeed_mps": 19.726, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 79.0, "power_watts": 843.86, "energy_consumed_wh": 15.7502, "r_env": 0.8339, "dynamic_pressure_pa": 199.75, "outcome": "in_flight"}, {"step": 52, "elapsed_time_s": 104.0, "position_3d": [0.6149, 6.9611, 0.4], "position_meters": [208.83, 671.55, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.163, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 78.83, "power_watts": 229.77, "energy_consumed_wh": 15.8779, "r_env": 0.8255, "dynamic_pressure_pa": 0.01, "outcome": "in_flight"}, {"step": 53, "elapsed_time_s": 106.0, "position_3d": [1.1226, 6.9604, 0.4], "position_meters": [208.81, 656.32, 160.0], "velocity_mps": [-0.011, -7.615, 0.0], "ground_speed_mps": 7.615, "airspeed_mps": 19.54, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 78.22, "power_watts": 826.63, "energy_consumed_wh": 16.3371, "r_env": 0.8276, "dynamic_pressure_pa": 196.0, "outcome": "in_flight"}, {"step": 54, "elapsed_time_s": 108.0, "position_3d": [0.3226, 6.9596, 0.4], "position_meters": [208.79, 680.32, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.173, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 78.05, "power_watts": 229.77, "energy_consumed_wh": 16.4648, "r_env": 0.8341, "dynamic_pressure_pa": 0.02, "outcome": "in_flight"}, {"step": 55, "elapsed_time_s": 110.0, "position_3d": [0.8261, 6.9589, 0.4], "position_meters": [208.77, 665.22, 160.0], "velocity_mps": [-0.011, -7.553, 0.0], "ground_speed_mps": 7.553, "airspeed_mps": 19.789, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 77.42, "power_watts": 849.75, "energy_consumed_wh": 16.9369, "r_env": 0.836, "dynamic_pressure_pa": 201.03, "outcome": "in_flight"}, {"step": 56, "elapsed_time_s": 112.0, "position_3d": [1.3334, 6.9581, 0.4], "position_meters": [208.74, 650.0, 160.0], "velocity_mps": [-0.011, -7.608, 0.0], "ground_speed_mps": 7.608, "airspeed_mps": 19.566, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 76.8, "power_watts": 829.02, "energy_consumed_wh": 17.3974, "r_env": 0.8285, "dynamic_pressure_pa": 196.52, "outcome": "in_flight"}, {"step": 57, "elapsed_time_s": 114.0, "position_3d": [0.5334, 6.9574, 0.4], "position_meters": [208.72, 674.0, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.099, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 76.63, "power_watts": 229.77, "energy_consumed_wh": 17.5251, "r_env": 0.8273, "dynamic_pressure_pa": 0.01, "outcome": "in_flight"}, {"step": 58, "elapsed_time_s": 116.0, "position_3d": [1.0447, 6.9567, 0.4], "position_meters": [208.7, 658.66, 160.0], "velocity_mps": [-0.011, -7.671, 0.0], "ground_speed_mps": 7.671, "airspeed_mps": 19.317, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 76.04, "power_watts": 806.43, "energy_consumed_wh": 17.9731, "r_env": 0.8202, "dynamic_pressure_pa": 191.55, "outcome": "in_flight"}, {"step": 59, "elapsed_time_s": 118.0, "position_3d": [0.2447, 6.956, 0.4], "position_meters": [208.68, 682.66, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.492, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 75.87, "power_watts": 229.78, "energy_consumed_wh": 18.1007, "r_env": 0.8166, "dynamic_pressure_pa": 0.12, "outcome": "in_flight"}, {"step": 60, "elapsed_time_s": 120.0, "position_3d": [0.7594, 6.9553, 0.4], "position_meters": [208.66, 667.22, 160.0], "velocity_mps": [-0.011, -7.72, 0.0], "ground_speed_mps": 7.72, "airspeed_mps": 19.119, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 75.28, "power_watts": 788.87, "energy_consumed_wh": 18.539, "r_env": 0.8136, "dynamic_pressure_pa": 187.64, "outcome": "in_flight"}, {"step": 61, "elapsed_time_s": 122.0, "position_3d": [1.2725, 6.9545, 0.4], "position_meters": [208.64, 651.82, 160.0], "velocity_mps": [-0.011, -7.697, 0.0], "ground_speed_mps": 7.697, "airspeed_mps": 19.212, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 74.69, "power_watts": 797.09, "energy_consumed_wh": 18.9818, "r_env": 0.8167, "dynamic_pressure_pa": 189.48, "outcome": "in_flight"}, {"step": 62, "elapsed_time_s": 124.0, "position_3d": [0.4725, 6.9538, 0.4], "position_meters": [208.62, 675.82, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.489, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 74.52, "power_watts": 229.78, "energy_consumed_wh": 19.1095, "r_env": 0.8167, "dynamic_pressure_pa": 0.12, "outcome": "in_flight"}, {"step": 63, "elapsed_time_s": 126.0, "position_3d": [0.9856, 6.9531, 0.4], "position_meters": [208.59, 660.43, 160.0], "velocity_mps": [-0.011, -7.695, 0.0], "ground_speed_mps": 7.695, "airspeed_mps": 19.218, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 73.93, "power_watts": 797.64, "energy_consumed_wh": 19.5526, "r_env": 0.8169, "dynamic_pressure_pa": 189.6, "outcome": "in_flight"}, {"step": 64, "elapsed_time_s": 128.0, "position_3d": [1.4941, 6.9524, 0.4], "position_meters": [208.57, 645.18, 160.0], "velocity_mps": [-0.011, -7.628, 0.0], "ground_speed_mps": 7.628, "airspeed_mps": 19.489, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 73.32, "power_watts": 822.0, "energy_consumed_wh": 20.0093, "r_env": 0.826, "dynamic_pressure_pa": 194.98, "outcome": "in_flight"}, {"step": 65, "elapsed_time_s": 130.0, "position_3d": [0.6941, 6.9517, 0.4], "position_meters": [208.55, 669.18, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.079, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 73.15, "power_watts": 229.77, "energy_consumed_wh": 20.1369, "r_env": 0.8279, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 66, "elapsed_time_s": 132.0, "position_3d": [1.2029, 6.9509, 0.4], "position_meters": [208.53, 653.91, 160.0], "velocity_mps": [-0.011, -7.632, 0.0], "ground_speed_mps": 7.632, "airspeed_mps": 19.474, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 72.54, "power_watts": 820.59, "energy_consumed_wh": 20.5928, "r_env": 0.8254, "dynamic_pressure_pa": 194.67, "outcome": "in_flight"}, {"step": 67, "elapsed_time_s": 134.0, "position_3d": [0.4029, 6.9502, 0.4], "position_meters": [208.51, 677.91, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.045, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 72.37, "power_watts": 229.77, "energy_consumed_wh": 20.7205, "r_env": 0.8296, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 68, "elapsed_time_s": 136.0, "position_3d": [0.909, 6.9494, 0.4], "position_meters": [208.48, 662.73, 160.0], "velocity_mps": [-0.011, -7.592, 0.0], "ground_speed_mps": 7.592, "airspeed_mps": 19.633, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 71.75, "power_watts": 835.15, "energy_consumed_wh": 21.1844, "r_env": 0.8307, "dynamic_pressure_pa": 197.86, "outcome": "in_flight"}, {"step": 69, "elapsed_time_s": 138.0, "position_3d": [1.4141, 6.9487, 0.4], "position_meters": [208.46, 647.58, 160.0], "velocity_mps": [-0.011, -7.577, 0.0], "ground_speed_mps": 7.577, "airspeed_mps": 19.691, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 71.13, "power_watts": 840.52, "energy_consumed_wh": 21.6514, "r_env": 0.8327, "dynamic_pressure_pa": 199.03, "outcome": "in_flight"}, {"step": 70, "elapsed_time_s": 140.0, "position_3d": [0.6141, 6.948, 0.4], "position_meters": [208.44, 671.58, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.057, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 70.96, "power_watts": 229.77, "energy_consumed_wh": 21.7791, "r_env": 0.8306, "dynamic_pressure_pa": 0.0, "outcome": "in_flight"}, {"step": 71, "elapsed_time_s": 142.0, "position_3d": [1.1211, 6.9472, 0.4], "position_meters": [208.42, 656.37, 160.0], "velocity_mps": [-0.011, -7.604, 0.0], "ground_speed_mps": 7.604, "airspeed_mps": 19.585, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 70.35, "power_watts": 830.77, "energy_consumed_wh": 22.2406, "r_env": 0.8292, "dynamic_pressure_pa": 196.9, "outcome": "in_flight"}, {"step": 72, "elapsed_time_s": 144.0, "position_3d": [0.3211, 6.9465, 0.4], "position_meters": [208.39, 680.37, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.126, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 70.18, "power_watts": 229.77, "energy_consumed_wh": 22.3682, "r_env": 0.8328, "dynamic_pressure_pa": 0.01, "outcome": "in_flight"}, {"step": 73, "elapsed_time_s": 146.0, "position_3d": [0.8271, 6.9457, 0.4], "position_meters": [208.37, 665.19, 160.0], "velocity_mps": [-0.011, -7.591, 0.0], "ground_speed_mps": 7.591, "airspeed_mps": 19.635, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 69.56, "power_watts": 835.38, "energy_consumed_wh": 22.8323, "r_env": 0.8308, "dynamic_pressure_pa": 197.91, "outcome": "in_flight"}, {"step": 74, "elapsed_time_s": 148.0, "position_3d": [1.3375, 6.945, 0.4], "position_meters": [208.35, 649.87, 160.0], "velocity_mps": [-0.011, -7.656, 0.0], "ground_speed_mps": 7.656, "airspeed_mps": 19.377, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 68.96, "power_watts": 811.77, "energy_consumed_wh": 23.2833, "r_env": 0.8222, "dynamic_pressure_pa": 192.73, "outcome": "in_flight"}, {"step": 75, "elapsed_time_s": 150.0, "position_3d": [0.5375, 6.9443, 0.4], "position_meters": [208.33, 673.87, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.44, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 68.79, "power_watts": 229.78, "energy_consumed_wh": 23.411, "r_env": 0.818, "dynamic_pressure_pa": 0.1, "outcome": "in_flight"}, {"step": 76, "elapsed_time_s": 152.0, "position_3d": [1.0485, 6.9436, 0.4], "position_meters": [208.31, 658.55, 160.0], "velocity_mps": [-0.011, -7.665, 0.0], "ground_speed_mps": 7.665, "airspeed_mps": 19.342, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 68.19, "power_watts": 808.63, "energy_consumed_wh": 23.8602, "r_env": 0.821, "dynamic_pressure_pa": 192.04, "outcome": "in_flight"}, {"step": 77, "elapsed_time_s": 154.0, "position_3d": [0.2485, 6.9428, 0.4], "position_meters": [208.29, 682.55, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.344, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 68.02, "power_watts": 229.78, "energy_consumed_wh": 23.9879, "r_env": 0.8206, "dynamic_pressure_pa": 0.06, "outcome": "in_flight"}, {"step": 78, "elapsed_time_s": 156.0, "position_3d": [0.7605, 6.9421, 0.4], "position_meters": [208.26, 667.18, 160.0], "velocity_mps": [-0.011, -7.68, 0.0], "ground_speed_mps": 7.68, "airspeed_mps": 19.278, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 67.42, "power_watts": 802.97, "energy_consumed_wh": 24.434, "r_env": 0.8189, "dynamic_pressure_pa": 190.78, "outcome": "in_flight"}, {"step": 79, "elapsed_time_s": 158.0, "position_3d": [1.2735, 6.9414, 0.4], "position_meters": [208.24, 651.79, 160.0], "velocity_mps": [-0.011, -7.695, 0.0], "ground_speed_mps": 7.695, "airspeed_mps": 19.221, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 66.83, "power_watts": 797.88, "energy_consumed_wh": 24.8772, "r_env": 0.817, "dynamic_pressure_pa": 189.65, "outcome": "in_flight"}, {"step": 80, "elapsed_time_s": 160.0, "position_3d": [0.4735, 6.9407, 0.4], "position_meters": [208.22, 675.79, 160.0], "velocity_mps": [-0.01, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.562, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 66.66, "power_watts": 229.79, "energy_consumed_wh": 25.0049, "r_env": 0.8147, "dynamic_pressure_pa": 0.16, "outcome": "in_flight"}, {"step": 81, "elapsed_time_s": 162.0, "position_3d": [0.9854, 6.94, 0.4], "position_meters": [208.2, 660.44, 160.0], "velocity_mps": [-0.011, -7.678, 0.0], "ground_speed_mps": 7.678, "airspeed_mps": 19.288, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 66.06, "power_watts": 803.82, "energy_consumed_wh": 25.4515, "r_env": 0.8192, "dynamic_pressure_pa": 190.97, "outcome": "in_flight"}, {"step": 82, "elapsed_time_s": 164.0, "position_3d": [1.4961, 6.9392, 0.4], "position_meters": [208.18, 645.12, 160.0], "velocity_mps": [-0.011, -7.66, 0.0], "ground_speed_mps": 7.66, "airspeed_mps": 19.359, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 65.46, "power_watts": 810.17, "energy_consumed_wh": 25.9016, "r_env": 0.8216, "dynamic_pressure_pa": 192.38, "outcome": "in_flight"}, {"step": 83, "elapsed_time_s": 166.0, "position_3d": [0.6961, 6.9385, 0.4], "position_meters": [208.16, 669.12, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.121, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 65.29, "power_watts": 229.77, "energy_consumed_wh": 26.0292, "r_env": 0.8267, "dynamic_pressure_pa": 0.01, "outcome": "in_flight"}, {"step": 84, "elapsed_time_s": 168.0, "position_3d": [1.2045, 6.9378, 0.4], "position_meters": [208.13, 653.86, 160.0], "velocity_mps": [-0.011, -7.627, 0.0], "ground_speed_mps": 7.627, "airspeed_mps": 19.494, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 64.69, "power_watts": 822.39, "energy_consumed_wh": 26.4861, "r_env": 0.8261, "dynamic_pressure_pa": 195.07, "outcome": "in_flight"}, {"step": 85, "elapsed_time_s": 170.0, "position_3d": [0.4045, 6.9371, 0.4], "position_meters": [208.11, 677.86, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.222, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 64.51, "power_watts": 229.77, "energy_consumed_wh": 26.6138, "r_env": 0.8238, "dynamic_pressure_pa": 0.03, "outcome": "in_flight"}, {"step": 86, "elapsed_time_s": 172.0, "position_3d": [0.9134, 6.9363, 0.4], "position_meters": [208.09, 662.6, 160.0], "velocity_mps": [-0.011, -7.634, 0.0], "ground_speed_mps": 7.634, "airspeed_mps": 19.464, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 63.91, "power_watts": 819.7, "energy_consumed_wh": 27.0691, "r_env": 0.8251, "dynamic_pressure_pa": 194.48, "outcome": "in_flight"}, {"step": 87, "elapsed_time_s": 174.0, "position_3d": [1.424, 6.9356, 0.4], "position_meters": [208.07, 647.28, 160.0], "velocity_mps": [-0.011, -7.658, 0.0], "ground_speed_mps": 7.658, "airspeed_mps": 19.367, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 63.31, "power_watts": 810.89, "energy_consumed_wh": 27.5196, "r_env": 0.8219, "dynamic_pressure_pa": 192.54, "outcome": "in_flight"}, {"step": 88, "elapsed_time_s": 176.0, "position_3d": [0.624, 6.9349, 0.4], "position_meters": [208.05, 671.28, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.471, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 63.14, "power_watts": 229.78, "energy_consumed_wh": 27.6473, "r_env": 0.8171, "dynamic_pressure_pa": 0.11, "outcome": "in_flight"}, {"step": 89, "elapsed_time_s": 178.0, "position_3d": [1.1393, 6.9342, 0.4], "position_meters": [208.03, 655.82, 160.0], "velocity_mps": [-0.011, -7.73, 0.0], "ground_speed_mps": 7.73, "airspeed_mps": 19.079, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 62.56, "power_watts": 785.4, "energy_consumed_wh": 28.0836, "r_env": 0.8123, "dynamic_pressure_pa": 186.86, "outcome": "in_flight"}, {"step": 90, "elapsed_time_s": 180.0, "position_3d": [0.3393, 6.9335, 0.4], "position_meters": [208.0, 679.82, 160.0], "velocity_mps": [-0.01, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.658, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 62.38, "power_watts": 229.8, "energy_consumed_wh": 28.2113, "r_env": 0.8122, "dynamic_pressure_pa": 0.22, "outcome": "in_flight"}, {"step": 91, "elapsed_time_s": 182.0, "position_3d": [0.8522, 6.9328, 0.4], "position_meters": [207.98, 664.43, 160.0], "velocity_mps": [-0.011, -7.694, 0.0], "ground_speed_mps": 7.694, "airspeed_mps": 19.226, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 61.79, "power_watts": 798.27, "energy_consumed_wh": 28.6548, "r_env": 0.8172, "dynamic_pressure_pa": 189.74, "outcome": "in_flight"}, {"step": 92, "elapsed_time_s": 184.0, "position_3d": [1.3659, 6.932, 0.4], "position_meters": [207.96, 649.02, 160.0], "velocity_mps": [-0.011, -7.705, 0.0], "ground_speed_mps": 7.705, "airspeed_mps": 19.179, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 61.21, "power_watts": 794.11, "energy_consumed_wh": 29.0959, "r_env": 0.8156, "dynamic_pressure_pa": 188.81, "outcome": "in_flight"}, {"step": 93, "elapsed_time_s": 186.0, "position_3d": [0.5659, 6.9313, 0.4], "position_meters": [207.94, 673.02, 160.0], "velocity_mps": [-0.01, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.596, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 61.04, "power_watts": 229.79, "energy_consumed_wh": 29.2236, "r_env": 0.8138, "dynamic_pressure_pa": 0.18, "outcome": "in_flight"}, {"step": 94, "elapsed_time_s": 188.0, "position_3d": [1.0781, 6.9306, 0.4], "position_meters": [207.92, 657.66, 160.0], "velocity_mps": [-0.011, -7.683, 0.0], "ground_speed_mps": 7.683, "airspeed_mps": 19.27, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 60.44, "power_watts": 802.18, "energy_consumed_wh": 29.6693, "r_env": 0.8186, "dynamic_pressure_pa": 190.61, "outcome": "in_flight"}, {"step": 95, "elapsed_time_s": 190.0, "position_3d": [0.2781, 6.9299, 0.4], "position_meters": [207.9, 681.66, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.467, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 60.27, "power_watts": 229.78, "energy_consumed_wh": 29.7969, "r_env": 0.8172, "dynamic_pressure_pa": 0.11, "outcome": "in_flight"}, {"step": 96, "elapsed_time_s": 192.0, "position_3d": [0.7875, 6.9292, 0.4], "position_meters": [207.88, 666.37, 160.0], "velocity_mps": [-0.011, -7.641, 0.0], "ground_speed_mps": 7.641, "airspeed_mps": 19.436, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 59.67, "power_watts": 817.11, "energy_consumed_wh": 30.2509, "r_env": 0.8242, "dynamic_pressure_pa": 193.91, "outcome": "in_flight"}, {"step": 97, "elapsed_time_s": 194.0, "position_3d": [1.3006, 6.9285, 0.4], "position_meters": [207.85, 650.98, 160.0], "velocity_mps": [-0.011, -7.696, 0.0], "ground_speed_mps": 7.696, "airspeed_mps": 19.214, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 59.07, "power_watts": 797.29, "energy_consumed_wh": 30.6938, "r_env": 0.8168, "dynamic_pressure_pa": 189.52, "outcome": "in_flight"}, {"step": 98, "elapsed_time_s": 196.0, "position_3d": [0.5006, 6.9277, 0.4], "position_meters": [207.83, 674.98, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.178, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 58.9, "power_watts": 229.77, "energy_consumed_wh": 30.8215, "r_env": 0.825, "dynamic_pressure_pa": 0.02, "outcome": "in_flight"}, {"step": 99, "elapsed_time_s": 198.0, "position_3d": [1.0063, 6.927, 0.4], "position_meters": [207.81, 659.81, 160.0], "velocity_mps": [-0.011, -7.585, 0.0], "ground_speed_mps": 7.585, "airspeed_mps": 19.659, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 58.28, "power_watts": 837.57, "energy_consumed_wh": 31.2868, "r_env": 0.8316, "dynamic_pressure_pa": 198.39, "outcome": "in_flight"}, {"step": 100, "elapsed_time_s": 200.0, "position_3d": [0.2063, 6.9263, 0.4], "position_meters": [207.79, 683.81, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.107, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 58.11, "power_watts": 229.77, "energy_consumed_wh": 31.4144, "r_env": 0.8271, "dynamic_pressure_pa": 0.01, "outcome": "in_flight"}, {"step": 101, "elapsed_time_s": 202.0, "position_3d": [0.714, 6.9255, 0.4], "position_meters": [207.77, 668.58, 160.0], "velocity_mps": [-0.011, -7.616, 0.0], "ground_speed_mps": 7.616, "airspeed_mps": 19.537, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 57.5, "power_watts": 826.34, "energy_consumed_wh": 31.8735, "r_env": 0.8275, "dynamic_pressure_pa": 195.93, "outcome": "in_flight"}, {"step": 102, "elapsed_time_s": 204.0, "position_3d": [1.2207, 6.9248, 0.4], "position_meters": [207.74, 653.38, 160.0], "velocity_mps": [-0.011, -7.6, 0.0], "ground_speed_mps": 7.6, "airspeed_mps": 19.6, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 56.89, "power_watts": 832.15, "energy_consumed_wh": 32.3358, "r_env": 0.8297, "dynamic_pressure_pa": 197.2, "outcome": "in_flight"}, {"step": 103, "elapsed_time_s": 206.0, "position_3d": [0.4207, 6.924, 0.4], "position_meters": [207.72, 677.38, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.173, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 56.72, "power_watts": 229.77, "energy_consumed_wh": 32.4635, "r_env": 0.8341, "dynamic_pressure_pa": 0.02, "outcome": "in_flight"}, {"step": 104, "elapsed_time_s": 208.0, "position_3d": [0.9256, 6.9233, 0.4], "position_meters": [207.7, 662.23, 160.0], "velocity_mps": [-0.011, -7.574, 0.0], "ground_speed_mps": 7.574, "airspeed_mps": 19.703, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 56.09, "power_watts": 841.7, "energy_consumed_wh": 32.9311, "r_env": 0.8331, "dynamic_pressure_pa": 199.28, "outcome": "in_flight"}, {"step": 105, "elapsed_time_s": 210.0, "position_3d": [1.4267, 6.9225, 0.4], "position_meters": [207.68, 647.2, 160.0], "velocity_mps": [-0.012, -7.517, 0.0], "ground_speed_mps": 7.517, "airspeed_mps": 19.933, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 55.45, "power_watts": 863.35, "energy_consumed_wh": 33.4107, "r_env": 0.8407, "dynamic_pressure_pa": 203.96, "outcome": "in_flight"}, {"step": 106, "elapsed_time_s": 212.0, "position_3d": [0.6267, 6.9218, 0.4], "position_meters": [207.65, 671.2, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.479, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 55.28, "power_watts": 229.78, "energy_consumed_wh": 33.5384, "r_env": 0.8424, "dynamic_pressure_pa": 0.12, "outcome": "in_flight"}, {"step": 107, "elapsed_time_s": 214.0, "position_3d": [1.1286, 6.921, 0.4], "position_meters": [207.63, 656.14, 160.0], "velocity_mps": [-0.012, -7.528, 0.0], "ground_speed_mps": 7.528, "airspeed_mps": 19.889, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 54.65, "power_watts": 859.18, "energy_consumed_wh": 34.0157, "r_env": 0.8393, "dynamic_pressure_pa": 203.06, "outcome": "in_flight"}, {"step": 108, "elapsed_time_s": 216.0, "position_3d": [0.3286, 6.9202, 0.4], "position_meters": [207.61, 680.14, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.485, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 54.48, "power_watts": 229.78, "energy_consumed_wh": 34.1434, "r_env": 0.8425, "dynamic_pressure_pa": 0.12, "outcome": "in_flight"}, {"step": 109, "elapsed_time_s": 218.0, "position_3d": [0.8297, 6.9195, 0.4], "position_meters": [207.58, 665.11, 160.0], "velocity_mps": [-0.012, -7.516, 0.0], "ground_speed_mps": 7.516, "airspeed_mps": 19.935, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 53.84, "power_watts": 863.54, "energy_consumed_wh": 34.6231, "r_env": 0.8408, "dynamic_pressure_pa": 204.0, "outcome": "in_flight"}, {"step": 110, "elapsed_time_s": 220.0, "position_3d": [1.3291, 6.9187, 0.4], "position_meters": [207.56, 650.13, 160.0], "velocity_mps": [-0.012, -7.491, 0.0], "ground_speed_mps": 7.491, "airspeed_mps": 20.036, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 53.19, "power_watts": 873.2, "energy_consumed_wh": 35.1082, "r_env": 0.8442, "dynamic_pressure_pa": 206.06, "outcome": "in_flight"}, {"step": 111, "elapsed_time_s": 222.0, "position_3d": [0.5291, 6.9179, 0.4], "position_meters": [207.54, 674.13, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.467, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 53.02, "power_watts": 229.78, "energy_consumed_wh": 35.2359, "r_env": 0.842, "dynamic_pressure_pa": 0.11, "outcome": "in_flight"}, {"step": 112, "elapsed_time_s": 224.0, "position_3d": [1.028, 6.9171, 0.4], "position_meters": [207.51, 659.16, 160.0], "velocity_mps": [-0.012, -7.483, 0.0], "ground_speed_mps": 7.483, "airspeed_mps": 20.067, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 52.37, "power_watts": 876.24, "energy_consumed_wh": 35.7227, "r_env": 0.8452, "dynamic_pressure_pa": 206.71, "outcome": "in_flight"}, {"step": 113, "elapsed_time_s": 226.0, "position_3d": [0.228, 6.9164, 0.4], "position_meters": [207.49, 683.16, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.58, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 52.2, "power_watts": 229.79, "energy_consumed_wh": 35.8503, "r_env": 0.8451, "dynamic_pressure_pa": 0.17, "outcome": "in_flight"}, {"step": 114, "elapsed_time_s": 228.0, "position_3d": [0.7264, 6.9156, 0.4], "position_meters": [207.47, 668.21, 160.0], "velocity_mps": [-0.012, -7.477, 0.0], "ground_speed_mps": 7.477, "airspeed_mps": 20.093, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 51.55, "power_watts": 878.79, "energy_consumed_wh": 36.3385, "r_env": 0.8461, "dynamic_pressure_pa": 207.26, "outcome": "in_flight"}, {"step": 115, "elapsed_time_s": 230.0, "position_3d": [1.2266, 6.9148, 0.4], "position_meters": [207.44, 653.2, 160.0], "velocity_mps": [-0.012, -7.502, 0.0], "ground_speed_mps": 7.502, "airspeed_mps": 19.99, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 50.91, "power_watts": 868.85, "energy_consumed_wh": 36.8212, "r_env": 0.8427, "dynamic_pressure_pa": 205.14, "outcome": "in_flight"}, {"step": 116, "elapsed_time_s": 232.0, "position_3d": [0.4266, 6.9141, 0.4], "position_meters": [207.42, 677.2, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.445, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 50.73, "power_watts": 229.78, "energy_consumed_wh": 36.9489, "r_env": 0.8414, "dynamic_pressure_pa": 0.1, "outcome": "in_flight"}, {"step": 117, "elapsed_time_s": 234.0, "position_3d": [0.9273, 6.9133, 0.4], "position_meters": [207.4, 662.18, 160.0], "velocity_mps": [-0.012, -7.51, 0.0], "ground_speed_mps": 7.51, "airspeed_mps": 19.959, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 50.09, "power_watts": 865.83, "energy_consumed_wh": 37.4299, "r_env": 0.8416, "dynamic_pressure_pa": 204.49, "outcome": "in_flight"}, {"step": 118, "elapsed_time_s": 236.0, "position_3d": [1.4262, 6.9125, 0.4], "position_meters": [207.38, 647.22, 160.0], "velocity_mps": [-0.012, -7.483, 0.0], "ground_speed_mps": 7.483, "airspeed_mps": 20.066, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 49.44, "power_watts": 876.15, "energy_consumed_wh": 37.9167, "r_env": 0.8452, "dynamic_pressure_pa": 206.69, "outcome": "in_flight"}, {"step": 119, "elapsed_time_s": 238.0, "position_3d": [0.6262, 6.9118, 0.4], "position_meters": [207.35, 671.22, 160.0], "velocity_mps": [-0.011, 12.0, 0.0], "ground_speed_mps": 12.0, "airspeed_mps": 0.43, "heading_rad": 0.0, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 49.27, "power_watts": 229.78, "energy_consumed_wh": 38.0443, "r_env": 0.841, "dynamic_pressure_pa": 0.09, "outcome": "in_flight"}, {"step": 120, "elapsed_time_s": 240.0, "position_3d": [1.126, 6.911, 0.4], "position_meters": [207.33, 656.22, 160.0], "velocity_mps": [-0.012, -7.498, 0.0], "ground_speed_mps": 7.498, "airspeed_mps": 20.009, "heading_rad": 3.1416, "terrain_clearance_norm": 0.3314, "battery_soc_pct": 48.63, "power_watts": 870.6, "energy_consumed_wh": 38.528, "r_env": 0.8433, "dynamic_pressure_pa": 205.51, "outcome": "timeout"}]}
};

// Embedded Empirical Benchmark Summary from evaluation_summary.csv
const EVALUATION_SUMMARY = [{"bucket": "Calm", "agent": "AdaptiveAgent", "trials": "100", "success_rate_pct": "95.0", "ci_95_pct": "4.3", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "5.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "29.0", "mean_flight_time_s": "58.0", "mean_path_length_m": "576.8", "mean_energy_wh": "4.996", "mean_min_clearance": "0.255", "mean_interventions": "3.16", "mean_reward": "163.4", "mean_wind_speed_mps": "2.21", "mean_r_env": "0.189"}, {"bucket": "Calm", "agent": "AdaptiveAgent_PBRS", "trials": "100", "success_rate_pct": "92.0", "ci_95_pct": "5.3", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "8.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "33.8", "mean_flight_time_s": "67.6", "mean_path_length_m": "633.2", "mean_energy_wh": "5.698", "mean_min_clearance": "0.26", "mean_interventions": "5.65", "mean_reward": "158.1", "mean_wind_speed_mps": "2.21", "mean_r_env": "0.189"}, {"bucket": "Calm", "agent": "StaticBaseline", "trials": "100", "success_rate_pct": "89.0", "ci_95_pct": "6.1", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "11.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "32.5", "mean_flight_time_s": "65.1", "mean_path_length_m": "625.3", "mean_energy_wh": "5.515", "mean_min_clearance": "0.261", "mean_interventions": "6.23", "mean_reward": "156.8", "mean_wind_speed_mps": "2.21", "mean_r_env": "0.189"}, {"bucket": "Calm", "agent": "RuleBasedPlanner", "trials": "100", "success_rate_pct": "99.0", "ci_95_pct": "2.0", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "1.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "20.4", "mean_flight_time_s": "40.8", "mean_path_length_m": "406.2", "mean_energy_wh": "3.522", "mean_min_clearance": "0.266", "mean_interventions": "0.6", "mean_reward": "177.6", "mean_wind_speed_mps": "2.21", "mean_r_env": "0.189"}, {"bucket": "Moderate", "agent": "AdaptiveAgent", "trials": "100", "success_rate_pct": "71.0", "ci_95_pct": "8.9", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "29.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "56.3", "mean_flight_time_s": "112.6", "mean_path_length_m": "700.4", "mean_energy_wh": "9.861", "mean_min_clearance": "0.273", "mean_interventions": "30.75", "mean_reward": "49.8", "mean_wind_speed_mps": "7.01", "mean_r_env": "0.472"}, {"bucket": "Moderate", "agent": "AdaptiveAgent_PBRS", "trials": "100", "success_rate_pct": "67.0", "ci_95_pct": "9.2", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "33.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "59.5", "mean_flight_time_s": "119.0", "mean_path_length_m": "736.2", "mean_energy_wh": "10.344", "mean_min_clearance": "0.274", "mean_interventions": "33.91", "mean_reward": "36.4", "mean_wind_speed_mps": "7.01", "mean_r_env": "0.472"}, {"bucket": "Moderate", "agent": "StaticBaseline", "trials": "100", "success_rate_pct": "68.0", "ci_95_pct": "9.1", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "32.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "57.3", "mean_flight_time_s": "114.6", "mean_path_length_m": "685.6", "mean_energy_wh": "9.917", "mean_min_clearance": "0.273", "mean_interventions": "34.23", "mean_reward": "71.7", "mean_wind_speed_mps": "7.01", "mean_r_env": "0.472"}, {"bucket": "Moderate", "agent": "RuleBasedPlanner", "trials": "100", "success_rate_pct": "74.0", "ci_95_pct": "8.6", "safe_rth_rate_pct": "0.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "26.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "49.0", "mean_flight_time_s": "97.9", "mean_path_length_m": "597.9", "mean_energy_wh": "8.466", "mean_min_clearance": "0.277", "mean_interventions": "27.21", "mean_reward": "91.3", "mean_wind_speed_mps": "7.01", "mean_r_env": "0.472"}, {"bucket": "Severe", "agent": "AdaptiveAgent", "trials": "100", "success_rate_pct": "1.0", "ci_95_pct": "2.0", "safe_rth_rate_pct": "96.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "3.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "7.4", "mean_flight_time_s": "14.8", "mean_path_length_m": "74.8", "mean_energy_wh": "1.493", "mean_min_clearance": "0.318", "mean_interventions": "5.63", "mean_reward": "6.5", "mean_wind_speed_mps": "13.76", "mean_r_env": "0.904"}, {"bucket": "Severe", "agent": "AdaptiveAgent_PBRS", "trials": "100", "success_rate_pct": "1.0", "ci_95_pct": "2.0", "safe_rth_rate_pct": "97.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "2.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "6.2", "mean_flight_time_s": "12.5", "mean_path_length_m": "64.7", "mean_energy_wh": "1.264", "mean_min_clearance": "0.319", "mean_interventions": "4.39", "mean_reward": "12.6", "mean_wind_speed_mps": "13.76", "mean_r_env": "0.904"}, {"bucket": "Severe", "agent": "StaticBaseline", "trials": "100", "success_rate_pct": "3.0", "ci_95_pct": "3.3", "safe_rth_rate_pct": "96.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "1.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "5.2", "mean_flight_time_s": "10.4", "mean_path_length_m": "50.6", "mean_energy_wh": "1.021", "mean_min_clearance": "0.318", "mean_interventions": "3.78", "mean_reward": "31.9", "mean_wind_speed_mps": "13.76", "mean_r_env": "0.904"}, {"bucket": "Severe", "agent": "RuleBasedPlanner", "trials": "100", "success_rate_pct": "4.0", "ci_95_pct": "3.8", "safe_rth_rate_pct": "96.0", "controlled_landing_rate_pct": "0.0", "timeout_rate_pct": "0.0", "crash_rate_pct": "0.0", "battery_depletion_rate_pct": "0.0", "mean_flight_steps": "4.3", "mean_flight_time_s": "8.7", "mean_path_length_m": "25.4", "mean_energy_wh": "0.659", "mean_min_clearance": "0.318", "mean_interventions": "3.61", "mean_reward": "35.2", "mean_wind_speed_mps": "13.76", "mean_r_env": "0.904"}];

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
