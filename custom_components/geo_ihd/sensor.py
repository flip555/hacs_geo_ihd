from homeassistant.helpers.entity import Entity
from .geo_helper import GeoHelper
from . import DOMAIN
import logging
import json
from datetime import timedelta

SCAN_INTERVAL = timedelta(seconds=10)

_LOGGER = logging.getLogger(__name__)

class GeoSensor(Entity):
    def __init__(self, name, data_func, attr, unit=None):
        self._name = name
        self._data_func = data_func
        self._attr = attr
        self._unit = unit  # Adding the unit of measurement
        self._latest_data = {}  # Initialize as empty dictionary

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit
        
    async def async_update_data(self):
        try:
            result = await self._data_func()
            
            #_LOGGER.debug("Raw data fetched for %s: %s", self._name, result)

            # Check if the result is a string, and if so, try to parse it as JSON
            if isinstance(result, str):
                self._latest_data = json.loads(result)
            else:
                self._latest_data = result

            #_LOGGER.debug("Processed data for %s: %s", self._name, self._latest_data)

        except json.JSONDecodeError:
            _LOGGER.error("Received data is not valid JSON: %s", result)
        except Exception as e:
            _LOGGER.error("Error fetching data: %s", e)

    async def async_update(self):
        """Fetch latest data."""
        await self.async_update_data()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self._latest_data
        for attr_part in self._attr.split('.'):
            if isinstance(data, dict):
                data = data.get(attr_part)
                if data is None:
                    _LOGGER.error("Missing data for attribute part '%s'.", attr_part)
                    return None
            elif isinstance(data, list):
                try:
                    index = int(attr_part)
                    data = data[index]
                except ValueError:
                    _LOGGER.error("Attribute part '%s' is not an integer, but encountered a list. Data: %s", attr_part, data)
                    return None
                except IndexError:
                    _LOGGER.error("Index '%s' is out of range for the list. Data: %s", attr_part, data)
                    return None
            else:
                _LOGGER.error("Data structure mismatch at attribute part '%s'. Expected dictionary or list but got %s. Data: %s", attr_part, type(data), data)
                return None

        #_LOGGER.debug("Final state for %s: %s", self._name, data)
        return data


# Further properties as needed...

async def async_setup_entry(hass, entry, async_add_entities):
    username = hass.data[DOMAIN]["username"]
    password = hass.data[DOMAIN]["password"]

    geo_helper = GeoHelper(username, password)
    
    async def get_data():
        return await geo_helper.get_consolidated_data(hass)


    sensors = [
        # Total Consumption
        GeoSensor("Geo IHD HACS - Electricity Total Consumption", get_data, "PeriodicMeterData.totalConsumptionList.0.totalConsumption", "kWh"),
        GeoSensor("Geo IHD HACS - Gas Total Consumption", get_data, "PeriodicMeterData.totalConsumptionList.1.totalConsumption", "kWh"),

        # Supply Status
        GeoSensor("Geo IHD HACS - Electricity Supply Status", get_data, "PeriodicMeterData.supplyStatusList.0.supplyStatus"),
        GeoSensor("Geo IHD HACS - Gas Supply Status", get_data, "PeriodicMeterData.supplyStatusList.1.supplyStatus"),

        # Bill To Date
        GeoSensor("Geo IHD HACS - Electricity Bill To Date", get_data, "PeriodicMeterData.billToDateList.0.billToDate", "p"),
        GeoSensor("Geo IHD HACS - Gas Bill To Date", get_data, "PeriodicMeterData.billToDateList.1.billToDate", "p"),

        # Active Tariff Price
        GeoSensor("Geo IHD HACS - Electricity Active Tariff Price", get_data, "PeriodicMeterData.activeTariffList.0.activeTariffPrice", "p/kWh"),
        GeoSensor("Geo IHD HACS - Gas Active Tariff Price", get_data, "PeriodicMeterData.activeTariffList.1.activeTariffPrice", "p/kWh"),

        # Current Costs for Electricity
        GeoSensor("Geo IHD HACS - Electricity Cost (Day)", get_data, "PeriodicMeterData.currentCostsElec.0.costAmount", "p"),
        GeoSensor("Geo IHD HACS - Electricity Cost (Week)", get_data, "PeriodicMeterData.currentCostsElec.1.costAmount", "p"),
        GeoSensor("Geo IHD HACS - Electricity Cost (Month)", get_data, "PeriodicMeterData.currentCostsElec.2.costAmount", "p"),

        # Current Costs for Gas
        GeoSensor("Geo IHD HACS - Gas Cost (Day)", get_data, "PeriodicMeterData.currentCostsGas.0.costAmount", "p"),
        GeoSensor("Geo IHD HACS - Gas Cost (Week)", get_data, "PeriodicMeterData.currentCostsGas.1.costAmount", "p"),
        GeoSensor("Geo IHD HACS - Gas Cost (Month)", get_data, "PeriodicMeterData.currentCostsGas.2.costAmount", "p"),

        # Live Meter Data (Power)
        GeoSensor("Geo IHD HACS - Live Electricity Usage", get_data, "LiveMeterData.power.0.watts", "W"),
        GeoSensor("Geo IHD HACS - Live Gas Usage", get_data, "LiveMeterData.power.1.watts", "W"),

        # Zigbee Status
        GeoSensor("Geo IHD HACS - Electricity Zigbee Status", get_data, "LiveMeterData.zigbeeStatus.electricityClusterStatus"),
        GeoSensor("Geo IHD HACS - Gas Zigbee Status", get_data, "LiveMeterData.zigbeeStatus.gasClusterStatus"),
    ]

    async_add_entities(sensors, True)