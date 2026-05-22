"""Geo Home IHD integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Geo Home IHD from a config entry."""
    from .coordinator import GeoIhdCoordinator

    coordinator = GeoIhdCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
