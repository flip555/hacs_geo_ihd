# Geo Home IHD Integration for Home Assistant

This custom component for Home Assistant allows users to integrate with the Geo Home platform, bringing seamless home automation and control to your Home Assistant instance.

## Features

- Easy integration with Geo Home via the Home Assistant UI.
- Securely authenticate using your Geo Home credentials.

## Installation

### Via HACS (Home Assistant Community Store) as a Custom Repository

1. Ensure that [HACS](https://hacs.xyz/) is installed.
2. Navigate to the HACS Integrations page.
3. Click on the three dots in the top right corner and choose "Custom repositories".
4. Enter the URL `https://github.com/flip555/hacs_geo_ihd` and select `Integration` from the category dropdown.
5. Click "Add".
6. Now, `Geo Home` should appear in the Integrations list in HACS. Install it from there.

### Manual Installation

1. Clone this repository or download the zip.
2. Copy the `hacs_geo_ihd` directory from the repository into your `custom_components` directory of your Home Assistant configuration.
3. Restart Home Assistant.

## Configuration

1. Go to the Integrations page in the Home Assistant UI.
2. Click on the "+" button at the bottom.
3. Search for "Geo Home" and start the configuration flow.
4. Provide your Geo Home Account `email` and `password`.
5. Click "Submit" and you're good to go!

## Screenshots

![Dashboard Screenshot](https://github.com/flip555/hacs_geo_ihd/raw/main/docs/dash.png)

![Live Electric Data Screenshot](https://github.com/flip555/hacs_geo_ihd/raw/main/docs/live_electric.png)

## Support

- For any issues or feedback, please [open an issue on GitHub](https://github.com/flip555/hacs_geo_ihd/issues).

## Contributing

If you'd like to contribute to this project, feel free to fork the repo, make your changes, and submit a pull request. All contributions are welcome!

## License

This project is under the [MIT License](LICENSE.md).

[releases]: https://github.com/flip555/hacs_geo_ihd/releases
[releases-shield]: https://img.shields.io/github/release/flip555/hacs_geo_ihd.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/flip555/hacs_geo_ihd.svg?style=for-the-badge
