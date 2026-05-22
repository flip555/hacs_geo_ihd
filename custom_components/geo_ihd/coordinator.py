"""Data coordinator for Geo Home IHD."""

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import GeoHomeAPIClient

_LOGGER = logging.getLogger(__name__)


class GeoIhdCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for Geo Home IHD."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._config = entry.data
        self.entry_id = entry.entry_id
        self.username = self._config.get("username")
        self._api_client = None
        self._cache = {}
        super().__init__(
            hass, _LOGGER, name="Geo Home IHD",
            update_interval=timedelta(
                seconds=self._config.get("sensor_update_frequency", 30)
            ),
        )

    def _is_cache_valid(self, cache_key: str, expiration_delta: timedelta) -> bool:
        cache_entry = self._cache.get(cache_key, {})
        timestamp = cache_entry.get("timestamp")
        if not timestamp:
            return False
        return datetime.now() - timestamp < expiration_delta

    def _update_cache(self, cache_key: str, data: Any) -> None:
        self._cache[cache_key] = {"timestamp": datetime.now(), "data": data}

    def _get_cached_data(self, cache_key: str) -> Any:
        return self._cache.get(cache_key, {}).get("data")

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Geo Together API."""
        try:
            if self._api_client is None:
                self._api_client = GeoHomeAPIClient(
                    self.username,
                    self._config.get("password"),
                    self._config.get("host", "https://api.geotogether.com"),
                )

            async with self._api_client:
                system_id = None
                if not self._is_cache_valid("system_id", timedelta(hours=1)):
                    if not self._is_cache_valid("device_data", timedelta(hours=1)):
                        device_data = await self._api_client.get_device_data()
                        self._update_cache("device_data", device_data)
                    else:
                        device_data = self._get_cached_data("device_data")
                    system_id = device_data["systemRoles"][0]["systemId"]
                    self._update_cache("system_id", system_id)
                else:
                    system_id = self._get_cached_data("system_id")

                if not self._is_cache_valid("periodic_data", timedelta(minutes=10)):
                    periodic_data = await self._api_client.get_periodic_meter_data(system_id)
                    self._update_cache("periodic_data", periodic_data)
                else:
                    periodic_data = self._get_cached_data("periodic_data")

                if not self._is_cache_valid("live_data", timedelta(seconds=30)):
                    live_data = await self._api_client.get_live_meter_data(system_id)
                    self._update_cache("live_data", live_data)
                else:
                    live_data = self._get_cached_data("live_data")

                if not self._is_cache_valid("device_data", timedelta(hours=1)):
                    device_data = await self._api_client.get_device_data()
                    self._update_cache("device_data", device_data)
                else:
                    device_data = self._get_cached_data("device_data")

            return {
                'PeriodicMeterData': periodic_data,
                'LiveMeterData': live_data,
                'DeviceData': device_data,
            }

        except Exception as e:
            for key in list(self._cache.keys()):
                self._cache.pop(key, None)
            raise UpdateFailed(f"Failed to fetch Geo IHD data: {e}")
