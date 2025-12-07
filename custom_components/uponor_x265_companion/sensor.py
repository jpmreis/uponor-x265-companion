"""Sensor platform for Uponor X265 Companion integration."""
import logging
from typing import Any, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MANUFACTURER, MODEL, SENSOR_TYPES, SIGNAL_UPDATE
from .coordinator import UponorCompanionCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Uponor X265 Companion sensor entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    
    entities = []
    
    await coordinator.async_request_refresh()
    
    for thermostat_id in coordinator.thermostats:
        thermostat_data = coordinator.get_thermostat_data(thermostat_id)
        
        for sensor_key, sensor_value in thermostat_data.items():
            if sensor_key in ["humidity", "humidity_setpoint", "valve_position_1", 
                             "valve_position_2", "floor_temp_max", "floor_temp_min",
                             "external_temperature", "eco_offset", "sw_version",
                             "thermostat_type", "hw_type"]:
                sensor_type = sensor_key.replace("_1", "").replace("_2", "")
                if sensor_type == "valve_position":
                    sensor_type = "valve_position"
                    
                if sensor_type in SENSOR_TYPES:
                    entities.append(
                        UponorCompanionSensor(
                            coordinator,
                            thermostat_id,
                            sensor_key,
                            sensor_type,
                        )
                    )
    
    system_data = coordinator.get_system_data()
    for sensor_key in ["average_room_temperature", "supply_temperature", 
                      "outdoor_temperature"]:
        if sensor_key in system_data:
            entities.append(
                UponorCompanionSystemSensor(
                    coordinator,
                    sensor_key,
                    sensor_key,
                )
            )
    
    async_add_entities(entities)


class UponorCompanionSensor(SensorEntity):
    """Representation of an Uponor X265 Companion sensor."""

    def __init__(
        self,
        coordinator: UponorCompanionCoordinator,
        thermostat_id: str,
        sensor_key: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._thermostat_id = thermostat_id
        self._sensor_key = sensor_key
        self._sensor_type = sensor_type
        self._sensor_config = SENSOR_TYPES.get(sensor_type, {})
        
        self._attr_unique_id = f"{DOMAIN}_{thermostat_id}_{sensor_key}"
        self._attr_name = f"{thermostat_id.replace('_', ' ')} {sensor_type.replace('_', ' ').title()}"
        
        self._attr_device_class = self._sensor_config.get("device_class")
        self._attr_state_class = self._sensor_config.get("state_class")
        self._attr_icon = self._sensor_config.get("icon")
        
        unit = self._sensor_config.get("unit")
        if unit == "°C":
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif unit == "%":
            self._attr_native_unit_of_measurement = PERCENTAGE
        else:
            self._attr_native_unit_of_measurement = unit

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._thermostat_id)},
            name=f"Thermostat {self._thermostat_id}",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        data = self._coordinator.get_thermostat_data(self._thermostat_id)
        return data.get(self._sensor_key)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.is_available

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_UPDATE, self._handle_coordinator_update
            )
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class UponorCompanionSystemSensor(SensorEntity):
    """Representation of a system-level Uponor X265 Companion sensor."""

    def __init__(
        self,
        coordinator: UponorCompanionCoordinator,
        sensor_key: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._sensor_key = sensor_key
        self._sensor_type = sensor_type
        self._sensor_config = SENSOR_TYPES.get(sensor_type, {})
        
        self._attr_unique_id = f"{DOMAIN}_system_{sensor_key}"
        self._attr_name = f"Uponor {sensor_type.replace('_', ' ').title()}"
        
        self._attr_device_class = self._sensor_config.get("device_class")
        self._attr_state_class = self._sensor_config.get("state_class")
        self._attr_icon = self._sensor_config.get("icon")
        
        unit = self._sensor_config.get("unit")
        if unit == "°C":
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif unit == "%":
            self._attr_native_unit_of_measurement = PERCENTAGE
        else:
            self._attr_native_unit_of_measurement = unit

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, "system")},
            name="Uponor X265 System",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        data = self._coordinator.get_system_data()
        return data.get(self._sensor_key)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.is_available

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_UPDATE, self._handle_coordinator_update
            )
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()