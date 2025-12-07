"""Binary sensor platform for Uponor X265 Companion integration."""
import logging
from typing import Optional

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MANUFACTURER, MODEL, BINARY_SENSOR_TYPES, SIGNAL_UPDATE
from .coordinator import UponorCompanionCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Uponor X265 Companion binary sensor entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    
    entities = []
    
    await coordinator.async_request_refresh()
    
    for thermostat_id in coordinator.thermostats:
        thermostat_data = coordinator.get_thermostat_data(thermostat_id)
        
        for sensor_key, sensor_value in thermostat_data.items():
            if sensor_key in ["humidity_control", "humidity_cool_shutdown", "battery_error",
                             "demand_led", "floor_limit_reached", "rf_error", "rf_low_signal",
                             "air_sensor_error", "rh_sensor_error", "valve_position_error",
                             "tamper_alarm", "eco_program", "eco_forced", "mode_comfort_eco",
                             "actuator_status"]:
                
                if sensor_key in BINARY_SENSOR_TYPES:
                    entities.append(
                        UponorCompanionBinarySensor(
                            coordinator,
                            thermostat_id,
                            sensor_key,
                        )
                    )
    
    system_data = coordinator.get_system_data()
    for sensor_key in ["general_system_alarm", "controller_presence", "controller_lost",
                      "output_module_lost", "pump_management", "valve_exercise",
                      "heat_cool_mode", "controller_demand"]:
        if sensor_key in system_data:
            entities.append(
                UponorCompanionSystemBinarySensor(
                    coordinator,
                    sensor_key,
                )
            )
    
    async_add_entities(entities)


class UponorCompanionBinarySensor(BinarySensorEntity):
    """Representation of an Uponor X265 Companion binary sensor."""

    def __init__(
        self,
        coordinator: UponorCompanionCoordinator,
        thermostat_id: str,
        sensor_key: str,
    ) -> None:
        """Initialize the binary sensor."""
        self._coordinator = coordinator
        self._thermostat_id = thermostat_id
        self._sensor_key = sensor_key
        self._sensor_config = BINARY_SENSOR_TYPES.get(sensor_key, {})
        
        self._attr_unique_id = f"{DOMAIN}_{thermostat_id}_{sensor_key}"
        self._attr_name = f"{thermostat_id.replace('_', ' ')} {sensor_key.replace('_', ' ').title()}"
        
        device_class = self._sensor_config.get("device_class")
        if device_class:
            self._attr_device_class = BinarySensorDeviceClass(device_class)
        
        self._attr_icon = self._sensor_config.get("icon")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={("uponorx265", self._thermostat_id)},
            name=f"Thermostat {self._thermostat_id}",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def is_on(self) -> Optional[bool]:
        """Return the state of the binary sensor."""
        data = self._coordinator.get_thermostat_data(self._thermostat_id)
        value = data.get(self._sensor_key)
        
        if self._sensor_key == "heat_cool_mode":
            return value == 1
        
        return bool(value) if value is not None else None

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


class UponorCompanionSystemBinarySensor(BinarySensorEntity):
    """Representation of a system-level Uponor X265 Companion binary sensor."""

    def __init__(
        self,
        coordinator: UponorCompanionCoordinator,
        sensor_key: str,
    ) -> None:
        """Initialize the binary sensor."""
        self._coordinator = coordinator
        self._sensor_key = sensor_key
        self._sensor_config = BINARY_SENSOR_TYPES.get(sensor_key, {})
        
        self._attr_unique_id = f"{DOMAIN}_system_{sensor_key}"
        self._attr_name = f"Uponor {sensor_key.replace('_', ' ').title()}"
        
        device_class = self._sensor_config.get("device_class")
        if device_class:
            self._attr_device_class = BinarySensorDeviceClass(device_class)
        
        self._attr_icon = self._sensor_config.get("icon")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={("uponorx265", "system")},
            name="Uponor X265 System",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def is_on(self) -> Optional[bool]:
        """Return the state of the binary sensor."""
        data = self._coordinator.get_system_data()
        value = data.get(self._sensor_key)
        
        if self._sensor_key == "heat_cool_mode":
            return value == 1
        
        return bool(value) if value is not None else None

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