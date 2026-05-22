# Geo Home IHD

A Home Assistant custom component for integrating Geo Home In-Home Display energy monitoring via the Geo Together API.

[![GitHub Release](https://img.shields.io/github/v/release/flip555/hacs_geo_ihd?style=for-the-badge)](https://github.com/flip555/hacs_geo_ihd/releases)
[![HACS Default](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://hacs.xyz/)
[![Discord](https://img.shields.io/discord/1161651448011034734?style=for-the-badge&logo=discord)](https://discord.gg/4eQbPEETBR)

## Features

- **Electricity Monitoring**: Live usage, total consumption, tariffs, costs, supply status
- **Gas Monitoring**: Live usage, total consumption, tariffs, costs, supply status
- **18 sensors** across electricity and gas categories
- **Automatic caching** — token cached 1h, periodic data 10min, live data 30s
- **Secure authentication** using email + password

## Supported Sensors

| Electricity | Gas |
|---|---|
| Total Consumption | Total Consumption |
| Supply Status | Supply Status |
| Bill To Date | Bill To Date |
| Active Tariff Price | Active Tariff Price |
| Cost (Day/Week/Month) | Cost (Day/Week/Month) |
| Live Usage | Live Usage |
| Zigbee Status | Zigbee Status |

## Installation

### Via HACS (recommended)
1. Ensure [HACS](https://hacs.xyz/) is installed.
2. Go to HACS → Integrations → Three dots → "Custom repositories".
3. Add `https://github.com/flip555/hacs_geo_ihd` as an Integration.
4. Install "Geo Home IHD" from HACS.
5. Restart Home Assistant.

### Manual
1. Download the ZIP from the [latest release](https://github.com/flip555/hacs_geo_ihd/releases).
2. Extract `geo_ihd` into your `custom_components` directory.
3. Restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for "Geo Home IHD".
3. Enter your Geo Together **email** and **password**.
4. Optionally change the API host (defaults to `https://api.geotogether.com`).
5. Set the update frequency (default 30 seconds).
6. Click Submit.

## Screenshots

![Dashboard](https://github.com/flip555/hacs_geo_ihd/raw/main/docs/dash.png)
![Live Electric Data](https://github.com/flip555/hacs_geo_ihd/raw/main/docs/live_electric.png)

## Support

Open an issue on [GitHub](https://github.com/flip555/hacs_geo_ihd/issues) or join the [Discord](https://discord.gg/4eQbPEETBR).

## License

MIT License
