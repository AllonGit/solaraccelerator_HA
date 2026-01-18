"""The Solar Accelerator integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_SERVER_URL,
    CONF_SEND_INTERVAL,
    CONF_ENTITY_MAPPING,
    DEFAULT_SEND_INTERVAL,
)

LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solar Accelerator from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # Get send_interval from options if available, otherwise from data
    send_interval = entry.options.get(
        CONF_SEND_INTERVAL,
        entry.data.get(CONF_SEND_INTERVAL, DEFAULT_SEND_INTERVAL),
    )

    hass.data[DOMAIN][entry.entry_id] = {
        CONF_API_KEY: entry.data.get(CONF_API_KEY),
        CONF_SERVER_URL: entry.data.get(CONF_SERVER_URL),
        CONF_SEND_INTERVAL: send_interval,
        CONF_ENTITY_MAPPING: entry.data.get(CONF_ENTITY_MAPPING, {}),
        "last_sent": None,
        "last_response": None,
        "connection_status": "unknown",
        "entities_sent": 0,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    # Update the stored send_interval
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        hass.data[DOMAIN][entry.entry_id][CONF_SEND_INTERVAL] = entry.options.get(
            CONF_SEND_INTERVAL,
            entry.data.get(CONF_SEND_INTERVAL, DEFAULT_SEND_INTERVAL),
        )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
