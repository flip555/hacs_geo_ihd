"""Sensor entities for Geo Home IHD."""

import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
    RestoreSensor,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GeoIhdSensor(CoordinatorEntity, RestoreSensor):
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
        state_class_map = {
            "measurement": SensorStateClass.MEASUREMENT,
            "total_increasing": SensorStateClass.TOTAL_INCREASING,
        }

        dc = sensor_info.get("device_class")
        self._attr_device_class = device_class_map.get(dc) if dc else None
        sc = sensor_info.get("state_class")
        self._attr_state_class = state_class_map.get(sc) if sc else None
        self._attr_icon = sensor_info.get("icon", "")

        device_type = "electric" if "electric" in key else "gas"
        self._attr_device_info = DeviceInfo(
            identifiers={("geo_ihd", entry_id, username, device_type)},
            manufacturer="Geo Home",
            name=f"Geo Home IHD",
            model="Geo IHD",
            sw_version="v1.0",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._key]["state"]

    @property
    def native_unit_of_measurement(self):
        return self.coordinator.data[self._key]["unit_of_measurement"]

    @property
    def device_class(self):
        return self._attr_device_class

    @property
    def state_class(self):
        return self._attr_state_class


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geo Home IHD sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    username = entry.data.get("username")

    sensors_data = coordinator.data
    _LOGGER.debug("LiveMeterData raw: %s", str(sensors_data.get("LiveMeterData", {}))[:500])

    electric_prefix = "Geo IHD - Electricity"
    gas_prefix = "Geo IHD - Gas"

    sensor_defs = {}

    try:
        periodic = sensors_data.get("PeriodicMeterData", {})
        live = sensors_data.get("LiveMeterData", {})

        # Total Consumption
        if "totalConsumptionList" in periodic and len(periodic["totalConsumptionList"]) > 0:
            sensor_defs["electricity_total_consumption"] = {
                "state": periodic["totalConsumptionList"][0]["totalConsumption"],
                "name": f"{electric_prefix} Total Consumption",
                "unique_id": f"geo_ihd_electricity_total_consumption_{entry.entry_id}",
                "unit_of_measurement": "kWh",
                "device_class": "energy",
                "state_class": "total_increasing",
                "icon": "",
            }
        if "totalConsumptionList" in periodic and len(periodic["totalConsumptionList"]) > 1:
            sensor_defs["gas_total_consumption"] = {
                "state": periodic["totalConsumptionList"][1]["totalConsumption"] / 1000,
                "name": f"{gas_prefix} Total Consumption",
                "unique_id": f"geo_ihd_gas_total_consumption_{entry.entry_id}",
                "unit_of_measurement": "m³",
                "device_class": "gas",
                "state_class": "total_increasing",
                "icon": "",
            }

        # Supply Status
        if "supplyStatusList" in periodic and len(periodic["supplyStatusList"]) > 0:
            sensor_defs["electricity_supply_status"] = {
                "state": periodic["supplyStatusList"][0]["supplyStatus"],
                "name": f"{electric_prefix} Supply Status",
                "unique_id": f"geo_ihd_electricity_supply_status_{entry.entry_id}",
                "unit_of_measurement": "",
                "device_class": "",
                "state_class": "",
                "icon": "",
            }
        if "supplyStatusList" in periodic and len(periodic["supplyStatusList"]) > 1:
            sensor_defs["gas_supply_status"] = {
                "state": periodic["supplyStatusList"][1]["supplyStatus"],
                "name": f"{gas_prefix} Supply Status",
                "unique_id": f"geo_ihd_gas_supply_status_{entry.entry_id}",
                "unit_of_measurement": "",
                "device_class": "",
                "state_class": "",
                "icon": "",
            }

        # Bill To Date
        if "billToDateList" in periodic and len(periodic["billToDateList"]) > 0:
            sensor_defs["electricity_bill_to_date"] = {
                "state": periodic["billToDateList"][0]["billToDate"] / 100,
                "name": f"{electric_prefix} Bill To Date",
                "unique_id": f"geo_ihd_electricity_bill_to_date_{entry.entry_id}",
                "unit_of_measurement": "GBP",
                "device_class": "monetary",
                "state_class": "total_increasing",
                "icon": "",
            }
        if "billToDateList" in periodic and len(periodic["billToDateList"]) > 1:
            sensor_defs["gas_bill_to_date"] = {
                "state": periodic["billToDateList"][1]["billToDate"] / 100,
                "name": f"{gas_prefix} Bill To Date",
                "unique_id": f"geo_ihd_gas_bill_to_date_{entry.entry_id}",
                "unit_of_measurement": "GBP",
                "device_class": "monetary",
                "state_class": "total_increasing",
                "icon": "",
            }

        # Active Tariff Price
        if "activeTariffList" in periodic and len(periodic["activeTariffList"]) > 0:
            sensor_defs["electricity_active_tariff_price"] = {
                "state": periodic["activeTariffList"][0]["activeTariffPrice"] / 100,
                "name": f"{electric_prefix} Active Tariff Price",
                "unique_id": f"geo_ihd_electricity_active_tariff_price_{entry.entry_id}",
                "unit_of_measurement": "GBP/kWh",
                "device_class": "",
                "state_class": "",
                "icon": "",
            }
        if "activeTariffList" in periodic and len(periodic["activeTariffList"]) > 1:
            sensor_defs["gas_active_tariff_price"] = {
                "state": periodic["activeTariffList"][1]["activeTariffPrice"] / 100,
                "name": f"{gas_prefix} Active Tariff Price",
                "unique_id": f"geo_ihd_gas_active_tariff_price_{entry.entry_id}",
                "unit_of_measurement": "GBP/kWh",
                "device_class": "",
                "state_class": "",
                "icon": "",
            }

        # Current Costs - Electric
        if "currentCostsElec" in periodic:
            costs = periodic["currentCostsElec"]
            periods = ["Day", "Week", "Month"]
            for i, period in enumerate(periods):
                if i < len(costs):
                    key = f"electricity_cost_{period.lower()}"
                    sensor_defs[key] = {
                        "state": costs[i]["costAmount"] / 100,
                        "name": f"{electric_prefix} Cost ({period})",
                        "unique_id": f"geo_ihd_electricity_cost_{period.lower()}_{entry.entry_id}",
                        "unit_of_measurement": "GBP",
                        "device_class": "monetary",
                        "state_class": "measurement",
                        "icon": "",
                    }

        # Current Costs - Gas
        if "currentCostsGas" in periodic:
            costs = periodic["currentCostsGas"]
            periods = ["Day", "Week", "Month"]
            for i, period in enumerate(periods):
                if i < len(costs):
                    key = f"gas_cost_{period.lower()}"
                    sensor_defs[key] = {
                        "state": costs[i]["costAmount"] / 100,
                        "name": f"{gas_prefix} Cost ({period})",
                        "unique_id": f"geo_ihd_gas_cost_{period.lower()}_{entry.entry_id}",
                        "unit_of_measurement": "GBP",
                        "device_class": "monetary",
                        "state_class": "measurement",
                        "icon": "",
                    }

        # Live Data — try multiple possible API response structures
        power_data = None
        if "power" in live:
            power_data = live["power"]
        elif "watts" in live:
            power_data = [{"watts": live["watts"]}]
        
        if power_data:
            if len(power_data) > 0 and isinstance(power_data[0], dict) and "watts" in power_data[0]:
                sensor_defs["live_electricity_usage"] = {
                    "state": power_data[0]["watts"],
                    "name": f"{electric_prefix} Live Usage",
                    "unique_id": f"geo_ihd_live_electricity_usage_{entry.entry_id}",
                    "unit_of_measurement": "W",
                    "device_class": "power",
                    "state_class": "measurement",
                    "icon": "",
                }
            if len(power_data) > 1 and isinstance(power_data[1], dict) and "watts" in power_data[1]:
                sensor_defs["live_gas_usage"] = {
                    "state": power_data[1]["watts"],
                    "name": f"{gas_prefix} Live Usage",
                    "unique_id": f"geo_ihd_live_gas_usage_{entry.entry_id}",
                    "unit_of_measurement": "W",
                    "device_class": "power",
                    "state_class": "measurement",
                    "icon": "",
                }

        # Zigbee Status
        if "zigbeeStatus" in live:
            zs = live["zigbeeStatus"]
            if "electricityClusterStatus" in zs:
                sensor_defs["electricity_zigbee_status"] = {
                    "state": zs["electricityClusterStatus"],
                    "name": f"{electric_prefix} Zigbee Status",
                    "unique_id": f"geo_ihd_electricity_zigbee_status_{entry.entry_id}",
                    "unit_of_measurement": "",
                    "device_class": "",
                    "state_class": "",
                    "icon": "",
                }
            if "gasClusterStatus" in zs:
                sensor_defs["gas_zigbee_status"] = {
                    "state": zs["gasClusterStatus"],
                    "name": f"{gas_prefix} Zigbee Status",
                    "unique_id": f"geo_ihd_gas_zigbee_status_{entry.entry_id}",
                    "unit_of_measurement": "",
                    "device_class": "",
                    "state_class": "",
                    "icon": "",
                }

    except Exception as err:
        _LOGGER.error("Error building Geo IHD sensors: %s", err)

    # Replace coordinator data with our processed sensor defs
    # so each sensor can look up its own data
    coordinator.data = sensor_defs

    entities = [
        GeoIhdSensor(coordinator, key, entry.entry_id, username)
        for key in sensor_defs
    ]
    _LOGGER.info("Setting up %d Geo IHD sensors", len(entities))
    async_add_entities(entities)
