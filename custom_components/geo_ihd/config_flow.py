from homeassistant import config_entries, data_entry_flow

import voluptuous as vol

from .const import DOMAIN

class GeoHomeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Your usual code
            return self.async_create_entry(title="GEO IHD", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required('username'): str,
                vol.Required('password'): str
            }),
            errors=errors,
            description_placeholders={
                'username': 'e.g., email@email.com',
                'password': 'e.g., Password123'
            }
        )
