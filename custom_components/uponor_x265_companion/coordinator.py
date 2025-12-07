"""Data coordinator for Uponor X265 Companion integration."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    SCAN_INTERVAL,
    SIGNAL_UPDATE,
    VARIABLE_MAPPING,
    SYSTEM_VARIABLE_MAPPING,
)
from .jnap import JNAPClient

_LOGGER = logging.getLogger(__name__)


class UponorCompanionCoordinator(DataUpdateCoordinator):
    """Coordinate data updates for Uponor X265 Companion."""

    def __init__(self, hass: HomeAssistant, client: JNAPClient) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client
        self._discovered_thermostats: Dict[str, Dict[str, Any]] = {}
        self._system_data: Dict[str, Any] = {}
        self._last_successful_update: Optional[datetime] = None
        
    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from controller."""
        try:
            all_variables = await self.client.discover_variables()
            
            if not all_variables:
                raise UpdateFailed("Failed to discover variables from controller")
            
            relevant_variables = self._filter_relevant_variables(all_variables)
            
            data = await self.client.get_attributes(relevant_variables)
            
            if not data:
                raise UpdateFailed("Failed to get attributes from controller")
            
            self._process_data(data)
            self._last_successful_update = datetime.now()
            
            async_dispatcher_send(self.hass, SIGNAL_UPDATE)
            
            return {
                "thermostats": self._discovered_thermostats,
                "system": self._system_data,
                "last_update": self._last_successful_update,
            }
            
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(f"Error communicating with controller: {err}") from err
    
    def _filter_relevant_variables(self, variables: List[str]) -> List[str]:
        """Filter variables to only those we're interested in."""
        relevant = []
        
        for var in variables:
            if any(key in var for key in VARIABLE_MAPPING.keys()):
                relevant.append(var)
            elif any(key in var for key in SYSTEM_VARIABLE_MAPPING.keys()):
                relevant.append(var)
            elif "C1_average_room_temperature" in var:
                relevant.append(var)
            elif "C1_supply_temperature" in var:
                relevant.append(var)
            elif "C1_outdoor_temperature" in var:
                relevant.append(var)
                
        return relevant
    
    def _process_data(self, data: Dict[str, Any]) -> None:
        """Process raw data into structured format."""
        for key, value in data.items():
            if key.startswith("C1_T"):
                self._process_thermostat_data(key, value)
            elif key.startswith("C1_") and "_T" not in key:
                self._process_controller_data(key, value)
            elif key.startswith("sys_"):
                self._process_system_data(key, value)
    
    def _process_thermostat_data(self, key: str, value: Any) -> None:
        """Process thermostat-specific data."""
        parts = key.split("_")
        if len(parts) < 3:
            return
            
        controller = parts[0]
        thermostat = parts[1]
        attribute = "_".join(parts[2:])
        
        thermostat_id = f"{controller}_{thermostat}"
        
        if thermostat_id not in self._discovered_thermostats:
            self._discovered_thermostats[thermostat_id] = {
                "id": thermostat_id,
                "controller": controller,
                "thermostat": thermostat,
                "data": {},
            }
        
        if attribute in VARIABLE_MAPPING:
            mapped_name = VARIABLE_MAPPING[attribute]
            processed_value = self._convert_value(attribute, value)
            self._discovered_thermostats[thermostat_id]["data"][mapped_name] = processed_value
    
    def _process_controller_data(self, key: str, value: Any) -> None:
        """Process controller-level data."""
        parts = key.split("_", 1)
        if len(parts) < 2:
            return
            
        attribute = parts[1]
        
        if attribute == "average_room_temperature":
            self._system_data["average_room_temperature"] = self._convert_temperature(value)
        elif attribute == "supply_temperature":
            self._system_data["supply_temperature"] = self._convert_temperature(value)
        elif attribute == "outdoor_temperature":
            self._system_data["outdoor_temperature"] = self._convert_temperature(value)
        elif attribute.startswith("stat_"):
            if attribute in VARIABLE_MAPPING:
                mapped_name = VARIABLE_MAPPING[attribute]
                self._system_data[mapped_name] = bool(int(value))
    
    def _process_system_data(self, key: str, value: Any) -> None:
        """Process system-level data."""
        if key in SYSTEM_VARIABLE_MAPPING:
            mapped_name = SYSTEM_VARIABLE_MAPPING[key]
            self._system_data[mapped_name] = bool(int(value))
    
    def _convert_value(self, attribute: str, value: Any) -> Any:
        """Convert raw value to appropriate type."""
        if attribute in ["rh", "rh_setpoint", "head1_valve_pos_percent", "head2_valve_pos_percent"]:
            return int(value)
        elif attribute in ["maximum_floor_setpoint", "minimum_floor_setpoint", 
                          "external_temperature", "eco_offset"]:
            return self._convert_temperature(value)
        elif attribute in ["sw_version", "thermostat_type", "hw_type"]:
            return str(value)
        else:
            try:
                return bool(int(value))
            except (ValueError, TypeError):
                return value
    
    def _convert_temperature(self, value: Any) -> float:
        """Convert temperature value from raw format to Celsius."""
        try:
            raw_val = int(value)
            return raw_val / 10.0 if raw_val > 100 else raw_val
        except (ValueError, TypeError):
            return 0.0
    
    def get_thermostat_data(self, thermostat_id: str) -> Dict[str, Any]:
        """Get data for a specific thermostat."""
        return self._discovered_thermostats.get(thermostat_id, {}).get("data", {})
    
    def get_system_data(self) -> Dict[str, Any]:
        """Get system-level data."""
        return self._system_data
    
    @property
    def thermostats(self) -> List[str]:
        """Return list of discovered thermostat IDs."""
        return list(self._discovered_thermostats.keys())
    
    @property
    def is_available(self) -> bool:
        """Check if coordinator is available."""
        if not self._last_successful_update:
            return False
        return (datetime.now() - self._last_successful_update) < timedelta(minutes=2)