import logging
from datetime import datetime, timezone, timedelta
import base64
import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN, 
    CONF_AUTH_BASIC_PASSWORD, 
    CONF_AUTH_BASIC_USERNAME, 
    CONF_INTERVAL, 
    CONF_URL,
    CONF_SENSOR_MAP
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """YAML setup (not used but must exist)."""
    return True



async def observation_json(iot_id, result):
    return {
        "result" : result,
        "phenomenonTime": datetime.now(timezone.utc).isoformat(),
        "Datastream": {"@iot.id": iot_id}
    }


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Start your 1-minute POST loop here
    # Use entry.data["url"], entry.data["api_key"], etc.

    session = aiohttp.ClientSession()
    credential = f"{entry.data[CONF_AUTH_BASIC_USERNAME]}:{entry.data[CONF_AUTH_BASIC_PASSWORD]}"
    b64_credential = base64.b64encode(credential.encode("utf-8")).decode('utf-8')
    headers = {
        "Content-Type": "application/json",
        aiohttp.hdrs.AUTHORIZATION: f"Basic {b64_credential}"
    }


    async def post_job(now):
        sensor_map = entry.options.get(CONF_SENSOR_MAP, [])
        for mapping in sensor_map:
            iot_id = mapping.get("iot_id")
            entity_id = mapping.get("entity")

            entity = hass.states.get(entity_id)
            if not entity:
                _LOGGER.warning("error reading sensor: %s", entity_id)
                continue

            try:
                json = await observation_json(iot_id, entity.state)
                async with session.post(
                    entry.data[CONF_URL],
                    headers=headers,
                    json=json,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 201:
                        _LOGGER.warning(
                            "POST failed: status=%s", resp.status
                        )
                    else:
                        _LOGGER.debug("SensorThings Observation POST OK, sent: %s", json)

            except Exception as e:
                _LOGGER.exception("POST request failed: %s", e)

    # Run every minute
    remove_listener = async_track_time_interval(
        hass,
        post_job,
        timedelta(seconds=entry.data[CONF_INTERVAL]),
    )

    async def shutdown(event):
        remove_listener()
        await session.close()

    hass.bus.async_listen_once("homeassistant_stop", shutdown)

    _LOGGER.info("SensorThings integration started")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Stop timers, close sessions
    hass.data[DOMAIN].pop(entry.entry_id)
    return True

