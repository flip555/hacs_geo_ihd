"""Sensor entities for Geo Home IHD."""

import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GeoIhdSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Geo Home IHD data."""

    def __init__(self, coordinator, key: str, entry_id: str, username: str) -> None:
        super().__init__(coordinator)
        sensor_info = coordinator.data[key]
        self._key = key

        self._attr_name = sensor_info["name"]
        self._attr_unique_id = sensor_info["unique_id"]
        self._attr_native_unit_of_measurement = sensor_info["unit_of_measurement"]

        device_class_map = {
            "power": SensorDeviceClass.POWER,
            "energy": SensorDeviceClass.ENERGY,
            "gas": SensorDeviceClass.GAS,
            "monetary": SensorDeviceClass.MONETARY,
        }

        dc = sensor_info.get("device_class")
        self._attr_device_class = device_class_map.get(dc) if dc else None

        sc = sensor_info.get("state_class")
        state_class_map = {
            "measurement": SensorStateClass.MEASUREMENT,
            "total_increasing": SensorStateClass.TOTAL_INCREASING,
        }
        self._attr_state_class = state_class_map.get(sc) if sc else None

        device_type = "electric" if "electric" in key else "gas"
        device_name = f"Geo IHD - {device_type.capitalize()}"
        self._attr_device_info = DeviceInfo(
            identifiers={("geo_ihd", entry_id, username, device_type)},
            manufacturer="Geo Home",
            name=device_name,
            model="Geo IHD",
            sw_version="v1.0",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self._key)
        if data is None:
            return None
        return data.get("state")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geo Home IHD sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    username = entry.data.get("username")

    sensor_keys = list(coordinator.data.keys())
    _LOGGER.info("Setting up %d Geo IHD sensors", len(sensor_keys))

    entities = [
        GeoIhdSensor(coordinator, key, entry.entry_id, username)
        for key in sensor_keys
    ]
    async_add_entities(entities)
