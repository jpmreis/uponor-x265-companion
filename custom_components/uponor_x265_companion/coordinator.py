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
    UNAVAILABLE_TIME,
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
        self._custom_names: Dict[str, str] = {}
        self._last_successful_update: Optional[datetime] = None
        self._last_response_time: Optional[datetime] = None
        
    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from controller."""
        _LOGGER.debug("Starting data update cycle")
        try:
            all_variables = await self.client.discover_variables()
            
            _LOGGER.debug("Discovered %d total variables from controller", len(all_variables) if all_variables else 0)
            _LOGGER.debug("First 10 discovered variables: %s", all_variables[:10] if all_variables else [])
            
            if not all_variables:
                raise UpdateFailed("Failed to discover variables from controller")
            
            relevant_variables = self._filter_relevant_variables(all_variables)
            _LOGGER.debug("Filtered to %d relevant variables: %s", len(relevant_variables), relevant_variables[:10] if relevant_variables else [])
            
            # Get all data and filter afterwards since specific requests seem to fail
            all_data = await self.client.get_attributes([])
            
            # Filter to only relevant variables
            data = {k: v for k, v in all_data.items() if k in relevant_variables} if all_data else None
            
            if not data:
                raise UpdateFailed("Failed to get attributes from controller")
            
            _LOGGER.debug("Retrieved data for %d variables", len(data))
            _LOGGER.debug("Sample data keys: %s", list(data.keys())[:10] if data else [])
            
            self._process_data(data)
            self._last_successful_update = datetime.now()
            self._last_response_time = self._last_successful_update
            
            _LOGGER.debug("Update successful - found %d thermostats, %d system variables. Last update: %s", 
                         len(self._discovered_thermostats), len(self._system_data), self._last_successful_update)
            
            async_dispatcher_send(self.hass, SIGNAL_UPDATE)
            
            return {
                "thermostats": self._discovered_thermostats,
                "system": self._system_data,
                "last_update": self._last_successful_update,
            }
            
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            # Only raise UpdateFailed if this is the first update or we haven't had a successful update in a while
            if not self._last_successful_update or (datetime.now() - self._last_successful_update) > timedelta(minutes=10):
                _LOGGER.error("Raising UpdateFailed - no recent successful updates")
                raise UpdateFailed(f"Error communicating with controller: {err}") from err
            else:
                # For temporary failures, log but don't fail the entire update
                time_since_last = datetime.now() - self._last_successful_update
                _LOGGER.warning("Temporary failure communicating with controller (last success %s ago), using cached data: %s", 
                              time_since_last, err)
                # Update the response time so availability doesn't expire
                self._last_response_time = datetime.now()
                return {
                    "thermostats": self._discovered_thermostats,
                    "system": self._system_data,
                    "last_update": self._last_response_time,
                }
    
    def _filter_relevant_variables(self, variables: List[str]) -> List[str]:
        """Filter variables to only those we're interested in."""
        relevant = []
        
        for var in variables:
            if any(key in var for key in VARIABLE_MAPPING.keys()):
                relevant.append(var)
            elif any(key in var for key in SYSTEM_VARIABLE_MAPPING.keys()):
                relevant.append(var)
            # Include controller-level variables for any controller (C1, C2, C3, etc.)
            elif any(f"C{i}_average_room_temperature" in var for i in range(1, 10)):
                relevant.append(var)
            elif any(f"C{i}_supply_temperature" in var for i in range(1, 10)):
                relevant.append(var)
            elif any(f"C{i}_outdoor_temperature" in var for i in range(1, 10)):
                relevant.append(var)
            # Include custom name variables
            elif var.startswith("cust_") and var.endswith("_name"):
                relevant.append(var)
                
        return relevant
    
    def _process_data(self, data: Dict[str, Any]) -> None:
        """Process raw data into structured format."""
        # First, process custom names
        for key, value in data.items():
            if key.startswith("cust_") and key.endswith("_name"):
                self._custom_names[key] = value
        
        # Then process all other data
        for key, value in data.items():
            # Process thermostat data for any controller (C1, C2, C3, etc.)
            if "_T" in key and key.startswith("C"):
                self._process_thermostat_data(key, value)
            # Process controller data for any controller
            elif key.startswith("C") and "_T" not in key:
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
            # Only store the value if it's not None (which indicates unavailable/no sensor)
            if processed_value is not None:
                self._discovered_thermostats[thermostat_id]["data"][mapped_name] = processed_value
    
    def _process_controller_data(self, key: str, value: Any) -> None:
        """Process controller-level data."""
        parts = key.split("_", 1)
        if len(parts) < 2:
            return
            
        attribute = parts[1]
        
        if attribute == "average_room_temperature":
            temp_value = self._convert_temperature(value)
            if temp_value is not None:
                self._system_data["average_room_temperature"] = temp_value
        elif attribute == "supply_temperature":
            temp_value = self._convert_temperature(value)
            if temp_value is not None:
                self._system_data["supply_temperature"] = temp_value
        elif attribute == "outdoor_temperature":
            temp_value = self._convert_temperature(value)
            if temp_value is not None:
                self._system_data["outdoor_temperature"] = temp_value
        elif attribute.startswith("stat_"):
            if attribute in VARIABLE_MAPPING:
                mapped_name = VARIABLE_MAPPING[attribute]
                try:
                    raw_val = int(value)
                    if raw_val != 32767:  # Skip sentinel values
                        self._system_data[mapped_name] = bool(raw_val)
                except (ValueError, TypeError):
                    pass
    
    def _process_system_data(self, key: str, value: Any) -> None:
        """Process system-level data."""
        if key in SYSTEM_VARIABLE_MAPPING:
            mapped_name = SYSTEM_VARIABLE_MAPPING[key]
            try:
                raw_val = int(value)
                if raw_val != 32767:  # Skip sentinel values
                    self._system_data[mapped_name] = bool(raw_val)
            except (ValueError, TypeError):
                pass
    
    def _convert_value(self, attribute: str, value: Any) -> Any:
        """Convert raw value to appropriate type."""
        try:
            raw_val = int(value)
            # 32767 is INT16_MAX, used as sentinel for "not available" or "no sensor"
            if raw_val == 32767:
                return None
        except (ValueError, TypeError):
            pass  # Not an integer, continue with normal processing
            
        if attribute in ["rh", "rh_setpoint", "head1_valve_pos_percent", "head2_valve_pos_percent"]:
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        elif attribute in ["maximum_floor_setpoint", "minimum_floor_setpoint", 
                          "external_temperature"]:
            return self._convert_temperature(value)
        elif attribute == "eco_offset":
            return self._convert_temperature_offset(value)
        elif attribute in ["sw_version", "thermostat_type", "hw_type"]:
            return str(value)
        else:
            try:
                return bool(int(value))
            except (ValueError, TypeError):
                return value
    
    def _convert_temperature(self, value: Any) -> Optional[float]:
        """Convert temperature value from tenths of Fahrenheit to Celsius."""
        try:
            raw_val = int(value)
            # 32767 is INT16_MAX, used as sentinel for "not available" or "no sensor"
            if raw_val == 32767:
                return None
            # Convert from tenths of Fahrenheit to Celsius
            fahrenheit = raw_val / 10.0
            celsius = (fahrenheit - 32) * 5.0 / 9.0
            return round(celsius, 1)
        except (ValueError, TypeError):
            return None
    
    def _convert_temperature_offset(self, value: Any) -> Optional[float]:
        """Convert temperature offset from tenths of Fahrenheit offset to Celsius offset."""
        try:
            raw_val = int(value)
            # 32767 is INT16_MAX, used as sentinel for "not available" or "no sensor"
            if raw_val == 32767:
                return None
            # For offsets: divide by 10, then multiply by 5/9 (no subtraction of 32)
            fahrenheit_offset = raw_val / 10.0
            celsius_offset = fahrenheit_offset * 5.0 / 9.0
            return round(celsius_offset, 1)
        except (ValueError, TypeError):
            return None
    
    def get_thermostat_data(self, thermostat_id: str) -> Dict[str, Any]:
        """Get data for a specific thermostat."""
        return self._discovered_thermostats.get(thermostat_id, {}).get("data", {})
    
    def get_system_data(self) -> Dict[str, Any]:
        """Get system-level data."""
        return self._system_data
    
    def get_custom_name(self, identifier: str) -> str:
        """Get custom name for a thermostat or controller."""
        # Check for thermostat custom name (e.g., cust_C1_T1_name)
        thermostat_key = f"cust_{identifier}_name"
        if thermostat_key in self._custom_names:
            return self._custom_names[thermostat_key]
        
        # Check for controller custom name (e.g., cust_Controller1_Name for C1)
        if identifier.startswith("C"):
            controller_num = identifier.split("_")[0][1:]  # C1 -> 1
            controller_key = f"cust_Controller{controller_num}_Name"
            if controller_key in self._custom_names:
                return self._custom_names[controller_key]
        
        # Fallback to generic name
        return identifier.replace("_", " ")
    
    @property
    def thermostats(self) -> List[str]:
        """Return list of discovered thermostat IDs."""
        return list(self._discovered_thermostats.keys())
    
    @property
    def is_available(self) -> bool:
        """Check if coordinator is available."""
        # Check if we've ever had a response
        if not self._last_response_time:
            _LOGGER.debug("Coordinator not available: no responses yet")
            return False
        
        # Use response time for availability (updates even when returning cached data)
        time_since_response = datetime.now() - self._last_response_time
        is_available = time_since_response < UNAVAILABLE_TIME
        
        if not is_available:
            _LOGGER.warning("Coordinator unavailable: last response %s ago", time_since_response)
        
        # Log separately about data freshness for debugging
        if self._last_successful_update:
            time_since_data = datetime.now() - self._last_successful_update
            if time_since_data > timedelta(minutes=2):
                _LOGGER.debug("Note: Using cached data from %s ago", time_since_data)
            
        return is_available