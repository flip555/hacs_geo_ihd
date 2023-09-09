DOMAIN = "geo_home"

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    hass.data[DOMAIN] = {
        "username": entry.data["username"],
        "password": entry.data["password"]
    }
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True
