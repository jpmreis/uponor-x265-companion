# Uponor X265 Companion Integration for Home Assistant

This is a companion integration for the existing [UponorX265 integration](https://github.com/dave-code-ruiz/uponorX265) that adds additional sensors and binary sensors that are not exposed by the main integration.

## Features

This companion integration adds the following sensor types:

### Humidity Sensors (Per Room)
- **Humidity**: Current relative humidity (%)
- **Humidity Setpoint**: Target humidity setpoint (%)
- **Humidity Control**: Binary sensor indicating if humidity control is active
- **Humidity Cool Shutdown**: Binary sensor for cooling shutdown due to humidity

### Valve Position Sensors (Per Room)
- **Valve Position 1**: Primary valve opening percentage (0-100%)
- **Valve Position 2**: Secondary valve opening percentage (if present)
- **Actuator Status**: Binary sensor for actuator status

### Battery Status (Per Thermostat)
- **Battery Error**: Binary sensor indicating low battery warning

### Demand/Heating Active (Per Room)
- **Demand LED**: Binary sensor indicating if zone is actively calling for heat
- **Controller Demand**: System-level demand status

### Floor Temperature Limits
- **Maximum Floor Setpoint**: Maximum allowed floor temperature (°C)
- **Minimum Floor Setpoint**: Minimum allowed floor temperature (°C)
- **Floor Limit Reached**: Binary sensor indicating floor limit has been reached

### External/Floor Temperature Sensor
- **External Temperature**: Reading from external temperature sensor (if connected)

### System-Level Sensors
- **Average Room Temperature**: System average of all room temperatures (°C)
- **Supply Temperature**: Supply water temperature (if sensor present)
- **Outdoor Temperature**: Outdoor temperature reading (if sensor present)

### Diagnostic Binary Sensors
- **RF Error**: RF communication error
- **RF Low Signal Warning**: Low signal strength warning
- **Air Sensor Error**: Air sensor fault
- **Humidity Sensor Error**: Humidity sensor fault
- **Valve Position Error**: Valve positioning error
- **Tamper Alarm**: Thermostat tamper detection
- **General System Alarm**: System-wide alarm status

### Controller Status
- **Controller Presence**: Controller online status
- **Controller Lost**: Controller communication lost
- **Output Module Lost**: Output module communication lost

### Pump/System Status
- **Pump Management**: Pump operation status
- **Valve Exercise**: Valve exercise mode active
- **Heat/Cool Mode**: System operating mode (0=heating, 1=cooling)

### ECO Mode Details (Per Room)
- **ECO Offset**: Temperature reduction in ECO mode (°C)
- **ECO Program**: Scheduled ECO mode active
- **ECO Forced**: Forced ECO mode active
- **Mode Comfort/ECO**: Current comfort/ECO mode status

### Thermostat Metadata
- **Software Version**: Thermostat firmware version
- **Thermostat Type**: Thermostat model type
- **Hardware Type**: Hardware type identifier

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jpmreis&repository=uponor-x265-companion&category=integration)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add `https://github.com/jpmreis/uponor-x265-companion` as a custom integration repository
5. Search for "Uponor X265 Companion" and install
6. Restart Home Assistant
7. Add the integration via Settings > Devices & Services > Add Integration

### Manual Installation

1. Download the `custom_components/uponor_x265_companion` directory from this repository
2. Copy it to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Go to **Settings** > **Devices & Services** > **Add Integration**
5. Search for "Uponor X265 Companion" and select it
6. Enter the same IP address you used for the main UponorX265 integration

## Prerequisites

- The main [UponorX265 integration](https://github.com/dave-code-ruiz/uponorX265) should be installed and working
- Both integrations can use the same device IP address
- Your Uponor X265 controller must be accessible on your network

## Device Compatibility

This integration uses the same JNAP protocol as the main UponorX265 integration and should work with the same devices:

- Uponor Smatrix Move Pro controller
- Uponor X-265 controller
- Compatible Uponor thermostats and sensors

## Troubleshooting

### Integration Not Discovering Sensors
- Ensure the IP address is correct and the controller is accessible
- Check that your Uponor system actually supports the additional variables
- Some sensors may only appear if the corresponding hardware is connected

### Sensors Showing as Unavailable
- Check network connectivity to the Uponor controller
- Verify the controller is responding to JNAP requests
- Check Home Assistant logs for error messages

### Missing Sensors
Not all sensors will be available on every system. The availability depends on:
- Connected hardware (humidity sensors, external temperature sensors, etc.)
- Controller configuration
- System model and firmware version

## Technical Details

### Communication Protocol
- Uses JNAP (JSON Network Application Protocol) over HTTP
- Same protocol as the main UponorX265 integration
- Polls controller every 30 seconds
- Automatic retry with exponential backoff

### Entity Naming
- Thermostat-specific sensors: `{Controller}_{Thermostat}_{Sensor Type}`
- System-level sensors: `Uponor {Sensor Type}`
- All entities include device information for grouping

### Data Processing
- Temperature values are automatically converted from raw format
- Percentage values for valves and humidity
- Binary sensors for status indicators
- Proper device classes and units for Home Assistant

## Contributing

This is an independent companion integration. For issues or contributions:

1. Check that the issue is specific to this companion integration
2. Verify the main UponorX265 integration is working correctly
3. Provide Home Assistant logs when reporting issues

## Support

If you find this integration useful, please consider:
- ⭐ Starring this repository
- 🐛 Reporting issues you encounter
- 💡 Suggesting new features or additional Uponor variables to support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.