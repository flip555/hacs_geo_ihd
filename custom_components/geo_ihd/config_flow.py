"""Config flow for Geo Home IHD."""

from homeassistant import config_entries
import voluptuous as vol
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_HOST, DEFAULT_PORT


class GeoIhdConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Geo Home IHD."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(f"geo_ihd_{user_input['username']}")
            return self.async_create_entry(
                title=f"Geo Home IHD - {user_input['username']}",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("username"): selector.TextSelector(
                    selector.TextSelectorConfig(type="email")
                ),
                vol.Required("password"): selector.TextSelector(
                    selector.TextSelectorConfig(type="password")
                ),
                vol.Optional(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional("sensor_update_frequency", default=30): int,
            }),
        )
