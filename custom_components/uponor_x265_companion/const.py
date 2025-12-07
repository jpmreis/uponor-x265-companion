"""Constants for the Uponor X265 Companion integration."""
from datetime import timedelta

DOMAIN = "uponor_x265_companion"
MANUFACTURER = "Uponor"
MODEL = "X265"

CONF_HOST = "host"

SCAN_INTERVAL = timedelta(seconds=30)
UNAVAILABLE_TIME = timedelta(minutes=5)

SIGNAL_UPDATE = f"{DOMAIN}_update"

SENSOR_TYPES = {
    "humidity": {
        "unit": "%",
        "device_class": "humidity",
        "icon": "mdi:water-percent",
        "state_class": "measurement",
    },
    "humidity_setpoint": {
        "unit": "%",
        "device_class": "humidity",
        "icon": "mdi:water-percent",
        "state_class": "measurement",
    },
    "valve_position": {
        "unit": "%",
        "icon": "mdi:valve",
        "state_class": "measurement",
    },
    "floor_temp_max": {
        "unit": "°C",
        "device_class": "temperature",
        "icon": "mdi:thermometer-chevron-up",
        "state_class": "measurement",
    },
    "floor_temp_min": {
        "unit": "°C",
        "device_class": "temperature",
        "icon": "mdi:thermometer-chevron-down",
        "state_class": "measurement",
    },
    "external_temperature": {
        "unit": "°C",
        "device_class": "temperature",
        "icon": "mdi:thermometer",
        "state_class": "measurement",
    },
    "average_room_temperature": {
        "unit": "°C",
        "device_class": "temperature",
        "icon": "mdi:home-thermometer",
        "state_class": "measurement",
    },
    "supply_temperature": {
        "unit": "°C",
        "device_class": "temperature",
        "icon": "mdi:pipe-disconnected",
        "state_class": "measurement",
    },
    "outdoor_temperature": {
        "unit": "°C",
        "device_class": "temperature",
        "icon": "mdi:thermometer-lines",
        "state_class": "measurement",
    },
    "eco_offset": {
        "unit": "°C",
        "device_class": "temperature",
        "icon": "mdi:leaf",
        "state_class": "measurement",
    },
    "sw_version": {
        "icon": "mdi:information-outline",
    },
    "thermostat_type": {
        "icon": "mdi:thermostat",
    },
    "hw_type": {
        "icon": "mdi:chip",
    },
}

BINARY_SENSOR_TYPES = {
    "humidity_control": {
        "device_class": "running",
        "icon": "mdi:water",
    },
    "humidity_cool_shutdown": {
        "device_class": "problem",
        "icon": "mdi:water-alert",
    },
    "battery_error": {
        "device_class": "battery",
        "icon": "mdi:battery-alert",
    },
    "demand_led": {
        "device_class": "heat",
        "icon": "mdi:radiator",
    },
    "floor_limit_reached": {
        "device_class": "problem",
        "icon": "mdi:thermometer-alert",
    },
    "rf_error": {
        "device_class": "connectivity",
        "icon": "mdi:wifi-strength-alert-outline",
    },
    "rf_low_signal": {
        "device_class": "problem",
        "icon": "mdi:wifi-strength-1",
    },
    "air_sensor_error": {
        "device_class": "problem",
        "icon": "mdi:thermometer-alert",
    },
    "rh_sensor_error": {
        "device_class": "problem",
        "icon": "mdi:water-alert",
    },
    "valve_position_error": {
        "device_class": "problem",
        "icon": "mdi:valve-open",
    },
    "tamper_alarm": {
        "device_class": "tamper",
        "icon": "mdi:shield-alert",
    },
    "general_system_alarm": {
        "device_class": "problem",
        "icon": "mdi:alert-circle",
    },
    "controller_presence": {
        "device_class": "connectivity",
        "icon": "mdi:router-wireless",
    },
    "controller_lost": {
        "device_class": "connectivity",
        "icon": "mdi:router-wireless-off",
    },
    "output_module_lost": {
        "device_class": "connectivity",
        "icon": "mdi:link-off",
    },
    "pump_management": {
        "device_class": "running",
        "icon": "mdi:pump",
    },
    "valve_exercise": {
        "device_class": "running",
        "icon": "mdi:cog-refresh",
    },
    "heat_cool_mode": {
        "icon": "mdi:toggle-switch",
    },
    "eco_program": {
        "device_class": "running",
        "icon": "mdi:leaf",
    },
    "eco_forced": {
        "device_class": "running",
        "icon": "mdi:leaf-circle",
    },
    "mode_comfort_eco": {
        "icon": "mdi:home-heart",
    },
    "actuator_status": {
        "device_class": "running",
        "icon": "mdi:cog",
    },
    "controller_demand": {
        "device_class": "heat",
        "icon": "mdi:radiator",
    },
}

VARIABLE_MAPPING = {
    "rh": "humidity",
    "rh_setpoint": "humidity_setpoint",
    "rh_control": "humidity_control",
    "stat_cb_rh_cool_shutdown": "humidity_cool_shutdown",
    "head1_valve_pos_percent": "valve_position_1",
    "head2_valve_pos_percent": "valve_position_2",
    "stat_cb_actuator": "actuator_status",
    "stat_battery_error": "battery_error",
    "stat_demand_led": "demand_led",
    "stat_demand": "controller_demand",
    "maximum_floor_setpoint": "floor_temp_max",
    "minimum_floor_setpoint": "floor_temp_min",
    "stat_cb_floor_limit_reach": "floor_limit_reached",
    "external_temperature": "external_temperature",
    "average_room_temperature": "average_room_temperature",
    "supply_temperature": "supply_temperature",
    "outdoor_temperature": "outdoor_temperature",
    "stat_rf_error": "rf_error",
    "stat_rf_low_sig_warning": "rf_low_signal",
    "stat_air_sensor_error": "air_sensor_error",
    "stat_rh_sensor_error": "rh_sensor_error",
    "stat_valve_position_err": "valve_position_error",
    "stat_tamper_alarm": "tamper_alarm",
    "stat_general_system_alarm": "general_system_alarm",
    "eco_offset": "eco_offset",
    "stat_eco_program": "eco_program",
    "stat_cb_eco_forced": "eco_forced",
    "mode_comfort_eco": "mode_comfort_eco",
    "sw_version": "sw_version",
    "thermostat_type": "thermostat_type",
    "hw_type": "hw_type",
}

SYSTEM_VARIABLE_MAPPING = {
    "sys_controller_1_presence": "controller_presence",
    "sys_controller_1_lost": "controller_lost",
    "stat_out_module_com_lost": "output_module_lost",
    "sys_pump_management": "pump_management",
    "sys_valve_exercise": "valve_exercise",
    "sys_heat_cool_mode": "heat_cool_mode",
}