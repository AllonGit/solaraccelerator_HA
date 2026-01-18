"""Sensor platform for Solar Accelerator integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.util.dt import utcnow

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_SERVER_URL,
    CONF_SEND_INTERVAL,
    CONF_ENTITY_MAPPING,
    API_PUSH_ENDPOINT,
    ENTITY_KEYS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""

    coordinator_data = hass.data[DOMAIN][entry.entry_id]

    # Add diagnostic sensors
    async_add_entities([
        SolarAcceleratorStatusSensor(hass, entry, coordinator_data),
        SolarAcceleratorLastSentSensor(hass, entry, coordinator_data),
        SolarAcceleratorEntitiesCountSensor(hass, entry, coordinator_data),
    ])

    # Start periodic data sending task
    task = hass.async_create_task(
        async_send_data_periodically(hass, entry, coordinator_data)
    )

    # Store task reference for cleanup
    coordinator_data["_task"] = task


class SolarAcceleratorSensorBase(SensorEntity):
    """Base class for Solar Accelerator sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        coordinator_data: dict[str, Any],
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self.entry = entry
        self.coordinator_data = coordinator_data
        self.sensor_type = sensor_type
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name="SolarAccelerator",
            manufacturer="SolarAccelerator",
            model="Home Assistant Push API",
            entry_type=DeviceEntryType.SERVICE,
        )


class SolarAcceleratorStatusSensor(SolarAcceleratorSensorBase):
    """Sensor for connection status."""

    _attr_icon = "mdi:cloud-check"
    _attr_translation_key = "connection_status"

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, coordinator_data: dict[str, Any]
    ) -> None:
        """Initialize."""
        super().__init__(hass, entry, coordinator_data, "connection_status")
        self._attr_name = "Status połączenia"

    @property
    def native_value(self) -> str:
        """Return the state."""
        return self.coordinator_data.get("connection_status", "unknown")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "server_url": self.coordinator_data.get(CONF_SERVER_URL),
            "send_interval": self.coordinator_data.get(CONF_SEND_INTERVAL),
            "last_response": self.coordinator_data.get("last_response"),
        }


class SolarAcceleratorLastSentSensor(SolarAcceleratorSensorBase):
    """Sensor for last data sent timestamp."""

    _attr_icon = "mdi:clock-outline"
    _attr_translation_key = "last_sent"

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, coordinator_data: dict[str, Any]
    ) -> None:
        """Initialize."""
        super().__init__(hass, entry, coordinator_data, "last_sent")
        self._attr_name = "Ostatnie wysłanie"

    @property
    def native_value(self) -> str | None:
        """Return the state."""
        return self.coordinator_data.get("last_sent")


class SolarAcceleratorEntitiesCountSensor(SolarAcceleratorSensorBase):
    """Sensor for entities count."""

    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "entities_sent"

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, coordinator_data: dict[str, Any]
    ) -> None:
        """Initialize."""
        super().__init__(hass, entry, coordinator_data, "entities_sent")
        self._attr_name = "Wysłane encje"

    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator_data.get("entities_sent", 0)


def convert_value(value: str | None, entity_key: str) -> float | int | bool | str | None:
    """Convert entity value to appropriate type for API."""
    if value is None or value in ("unknown", "unavailable", ""):
        return 0

    # Boolean for grid_connected_status
    if entity_key == "grid_connected_status":
        return value.lower() in ("on", "true", "1", "connected")

    # Status field - keep as string
    if entity_key == "inverter_status":
        return value

    # Numeric values
    try:
        float_val = float(value)
        # Return int if it's a whole number
        if float_val.is_integer():
            return int(float_val)
        return float_val
    except (ValueError, TypeError):
        return 0


async def async_send_data_periodically(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator_data: dict[str, Any],
) -> None:
    """Send data to server periodically."""

    api_key = coordinator_data.get(CONF_API_KEY)
    server_url = coordinator_data.get(CONF_SERVER_URL)
    entity_mapping = coordinator_data.get(CONF_ENTITY_MAPPING, {})

    session = async_get_clientsession(hass)
    endpoint = f"{server_url}{API_PUSH_ENDPOINT}"

    while True:
        try:
            # Get current send_interval (may change from options)
            send_interval = max(60, coordinator_data.get(CONF_SEND_INTERVAL, 60))

            # Wait for the interval
            await asyncio.sleep(send_interval)

            # Gather current state of mapped entities
            entities_data = {}
            entities_count = 0

            for entity_key in ENTITY_KEYS:
                ha_entity_id = entity_mapping.get(entity_key)
                if ha_entity_id:
                    state = hass.states.get(ha_entity_id)
                    if state:
                        value = convert_value(state.state, entity_key)
                        entities_data[entity_key] = value
                        entities_count += 1
                    else:
                        entities_data[entity_key] = 0
                else:
                    entities_data[entity_key] = 0

            # Build payload
            payload = {
                "timestamp": utcnow().isoformat(),
                "entities": entities_data,
            }

            # Send to server
            async with session.post(
                endpoint,
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                response_text = await resp.text()

                if resp.status == 200:
                    coordinator_data["last_sent"] = utcnow().isoformat()
                    coordinator_data["connection_status"] = "connected"
                    coordinator_data["entities_sent"] = entities_count
                    coordinator_data["last_response"] = "OK"
                    _LOGGER.debug(
                        "Data sent successfully to %s: %d entities",
                        endpoint,
                        entities_count,
                    )
                elif resp.status == 401:
                    coordinator_data["connection_status"] = "auth_error"
                    coordinator_data["last_response"] = "Nieprawidłowy klucz API"
                    _LOGGER.error("Authentication failed: invalid API key")
                else:
                    coordinator_data["connection_status"] = "error"
                    coordinator_data["last_response"] = f"HTTP {resp.status}: {response_text[:100]}"
                    _LOGGER.error(
                        "Failed to send data: %s - %s",
                        resp.status,
                        response_text,
                    )

        except asyncio.CancelledError:
            _LOGGER.debug("Data sending task cancelled")
            break
        except aiohttp.ClientError as e:
            coordinator_data["connection_status"] = "disconnected"
            coordinator_data["last_response"] = f"Connection error: {str(e)[:50]}"
            _LOGGER.error("Connection error: %s", e)
        except Exception as e:
            coordinator_data["connection_status"] = "error"
            coordinator_data["last_response"] = f"Error: {str(e)[:50]}"
            _LOGGER.exception("Error sending data: %s", e)
