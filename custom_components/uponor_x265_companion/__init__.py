"""The Uponor X265 Companion integration."""
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, SCAN_INTERVAL
from .coordinator import UponorCompanionCoordinator
from .jnap import JNAPClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Uponor X265 Companion from a config entry."""
    host = entry.data[CONF_HOST]
    
    client = JNAPClient(host)
    coordinator = UponorCompanionCoordinator(hass, client)
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Schedule periodic updates - ensures polling continues even if no entities are listening
    # async_track_time_interval passes a datetime argument, so we wrap the call
    async def _async_update(_now=None):
        """Wrapper to handle time interval callback."""
        await coordinator.async_refresh()

    entry.async_on_unload(
        async_track_time_interval(hass, _async_update, SCAN_INTERVAL)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["client"].close()
        
    return unload_ok