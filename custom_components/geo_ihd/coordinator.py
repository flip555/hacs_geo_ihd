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

    def _build_sensor_defs(self, periodic, live):
        """Build processed sensor definitions from raw API data."""
        electric_prefix = "Electricity"
        gas_prefix = "Gas"
        entry_id = self.entry_id
        sensors = {}

        try:
            if "totalConsumptionList" in periodic and len(periodic["totalConsumptionList"]) > 0:
                sensors["electricity_total_consumption"] = {
                    "state": periodic["totalConsumptionList"][0]["totalConsumption"],
                    "name": f"{electric_prefix} Total Consumption",
                    "unique_id": f"geo_ihd_electricity_total_consumption_{entry_id}",
                    "unit_of_measurement": "kWh",
                    "device_class": "energy",
                    "state_class": "total_increasing",
                }
            if "totalConsumptionList" in periodic and len(periodic["totalConsumptionList"]) > 1:
                sensors["gas_total_consumption"] = {
                    "state": periodic["totalConsumptionList"][1]["totalConsumption"] / 1000,
                    "name": f"{gas_prefix} Total Consumption",
                    "unique_id": f"geo_ihd_gas_total_consumption_{entry_id}",
                    "unit_of_measurement": "m\u00b3",
                    "device_class": "gas",
                    "state_class": "total_increasing",
                }

            if "supplyStatusList" in periodic and len(periodic["supplyStatusList"]) > 0:
                sensors["electricity_supply_status"] = {
                    "state": periodic["supplyStatusList"][0]["supplyStatus"],
                    "name": f"{electric_prefix} Supply Status",
                    "unique_id": f"geo_ihd_electricity_supply_status_{entry_id}",
                    "unit_of_measurement": None,
                    "device_class": None,
                    "state_class": None,
                }
            if "supplyStatusList" in periodic and len(periodic["supplyStatusList"]) > 1:
                sensors["gas_supply_status"] = {
                    "state": periodic["supplyStatusList"][1]["supplyStatus"],
                    "name": f"{gas_prefix} Supply Status",
                    "unique_id": f"geo_ihd_gas_supply_status_{entry_id}",
                    "unit_of_measurement": None,
                    "device_class": None,
                    "state_class": None,
                }

            if "billToDateList" in periodic and len(periodic["billToDateList"]) > 0:
                sensors["electricity_bill_to_date"] = {
                    "state": periodic["billToDateList"][0]["billToDate"] / 100,
                    "name": f"{electric_prefix} Bill To Date",
                    "unique_id": f"geo_ihd_electricity_bill_to_date_{entry_id}",
                    "unit_of_measurement": "GBP",
                    "device_class": "monetary",
                    "state_class": None,
                }
            if "billToDateList" in periodic and len(periodic["billToDateList"]) > 1:
                sensors["gas_bill_to_date"] = {
                    "state": periodic["billToDateList"][1]["billToDate"] / 100,
                    "name": f"{gas_prefix} Bill To Date",
                    "unique_id": f"geo_ihd_gas_bill_to_date_{entry_id}",
                    "unit_of_measurement": "GBP",
                    "device_class": "monetary",
                    "state_class": None,
                }

            if "activeTariffList" in periodic and len(periodic["activeTariffList"]) > 0:
                sensors["electricity_active_tariff_price"] = {
                    "state": periodic["activeTariffList"][0]["activeTariffPrice"] / 100,
                    "name": f"{electric_prefix} Active Tariff Price",
                    "unique_id": f"geo_ihd_electricity_active_tariff_price_{entry_id}",
                    "unit_of_measurement": "GBP/kWh",
                    "device_class": None,
                    "state_class": None,
                }
            if "activeTariffList" in periodic and len(periodic["activeTariffList"]) > 1:
                sensors["gas_active_tariff_price"] = {
                    "state": periodic["activeTariffList"][1]["activeTariffPrice"] / 100,
                    "name": f"{gas_prefix} Active Tariff Price",
                    "unique_id": f"geo_ihd_gas_active_tariff_price_{entry_id}",
                    "unit_of_measurement": "GBP/kWh",
                    "device_class": None,
                    "state_class": None,
                }

            if "currentCostsElec" in periodic:
                costs = periodic["currentCostsElec"]
                for i, period in enumerate(["Day", "Week", "Month"]):
                    if i < len(costs):
                        key = f"electricity_cost_{period.lower()}"
                        sensors[key] = {
                            "state": costs[i]["costAmount"] / 100,
                            "name": f"{electric_prefix} Cost ({period})",
                            "unique_id": f"geo_ihd_electricity_cost_{period.lower()}_{entry_id}",
                            "unit_of_measurement": "GBP",
                            "device_class": "monetary",
                            "state_class": None,
                        }

            if "currentCostsGas" in periodic:
                costs = periodic["currentCostsGas"]
                for i, period in enumerate(["Day", "Week", "Month"]):
                    if i < len(costs):
                        key = f"gas_cost_{period.lower()}"
                        sensors[key] = {
                            "state": costs[i]["costAmount"] / 100,
                            "name": f"{gas_prefix} Cost ({period})",
                            "unique_id": f"geo_ihd_gas_cost_{period.lower()}_{entry_id}",
                            "unit_of_measurement": "GBP",
                            "device_class": "monetary",
                            "state_class": None,
                        }

            if "power" in live:
                power = live["power"]
                if len(power) > 0 and isinstance(power[0], dict) and "watts" in power[0]:
                    sensors["live_electricity_usage"] = {
                        "state": power[0]["watts"],
                        "name": f"{electric_prefix} Live Usage",
                        "unique_id": f"geo_ihd_live_electricity_usage_{entry_id}",
                        "unit_of_measurement": "W",
                        "device_class": "power",
                        "state_class": "measurement",
                    }
                if len(power) > 1 and isinstance(power[1], dict) and "watts" in power[1]:
                    sensors["live_gas_usage"] = {
                        "state": power[1]["watts"],
                        "name": f"{gas_prefix} Live Usage",
                        "unique_id": f"geo_ihd_live_gas_usage_{entry_id}",
                        "unit_of_measurement": "W",
                        "device_class": "power",
                        "state_class": "measurement",
                    }

            if "zigbeeStatus" in live:
                zs = live["zigbeeStatus"]
                if "electricityClusterStatus" in zs:
                    sensors["electricity_zigbee_status"] = {
                        "state": zs["electricityClusterStatus"],
                        "name": f"{electric_prefix} Zigbee Status",
                        "unique_id": f"geo_ihd_electricity_zigbee_status_{entry_id}",
                        "unit_of_measurement": None,
                        "device_class": None,
                        "state_class": None,
                    }
                if "gasClusterStatus" in zs:
                    sensors["gas_zigbee_status"] = {
                        "state": zs["gasClusterStatus"],
                        "name": f"{gas_prefix} Zigbee Status",
                        "unique_id": f"geo_ihd_gas_zigbee_status_{entry_id}",
                        "unit_of_measurement": None,
                        "device_class": None,
                        "state_class": None,
                    }

        except Exception as err:
            _LOGGER.error("Error building sensor defs: %s", err)

        return sensors

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data and return processed sensor definitions."""
        client = None
        try:
            client = GeoHomeAPIClient(
                self.username,
                self._config.get("password"),
                self._config.get("host", "https://api.geotogether.com"),
            )

            system_id = None
            if not self._is_cache_valid("system_id", timedelta(hours=1)):
                if not self._is_cache_valid("device_data", timedelta(hours=1)):
                    device_data = await client.get_device_data()
                    self._update_cache("device_data", device_data)
                else:
                    device_data = self._get_cached_data("device_data")
                system_id = device_data["systemRoles"][0]["systemId"]
                self._update_cache("system_id", system_id)
            else:
                system_id = self._get_cached_data("system_id")

            if not self._is_cache_valid("periodic_data", timedelta(minutes=10)):
                periodic_data = await client.get_periodic_meter_data(system_id)
                self._update_cache("periodic_data", periodic_data)
            else:
                periodic_data = self._get_cached_data("periodic_data")

            if not self._is_cache_valid("live_data", timedelta(seconds=30)):
                live_data = await client.get_live_meter_data(system_id)
                self._update_cache("live_data", live_data)
            else:
                live_data = self._get_cached_data("live_data")

            if not self._is_cache_valid("device_data", timedelta(hours=1)):
                device_data = await client.get_device_data()
                self._update_cache("device_data", device_data)

            return self._build_sensor_defs(periodic_data, live_data)

        except Exception as e:
            for key in list(self._cache.keys()):
                self._cache.pop(key, None)
            raise UpdateFailed(f"Failed to fetch Geo IHD data: {e}")
        finally:
            if client:
                await client.close()
