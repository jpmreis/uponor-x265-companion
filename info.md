## Uponor X265 Companion

A companion integration for the [UponorX265 integration](https://github.com/dave-code-ruiz/uponorX265) that exposes additional sensors and binary sensors not available in the main integration.

### Features Added

- **Humidity sensors** per room (humidity %, setpoint, control status)
- **Valve position sensors** showing valve opening percentages for diagnostics
- **Battery status** indicators for low battery warnings
- **Demand sensors** showing active heating calls per zone
- **Floor temperature limits** with min/max setpoints and warnings
- **External temperature sensors** for additional temperature readings
- **System-level sensors** including averages and supply temperatures
- **Diagnostic sensors** for RF errors, sensor faults, and tamper detection
- **Controller status** sensors for connectivity and communication
- **ECO mode details** including offsets and program status
- **Thermostat metadata** with firmware and hardware information

### Installation

1. Install via HACS (recommended) or copy files manually
2. Restart Home Assistant
3. Add the integration using the same IP as your main UponorX265 integration
4. Sensors will automatically appear based on your system's capabilities

### Compatibility

Works alongside the existing UponorX265 integration. Both can use the same device IP address safely.