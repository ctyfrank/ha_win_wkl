import asyncio
import json
import requests
from homeassistant import config_entries, core
from .const import (
    DOMAIN
)
import logging
import subprocess
from datetime import timedelta
from .utils import ping_ip
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    "switch",
]

async def async_setup(hass: core.HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass, entry):
    _LOGGER.debug("Setting up My Device component")
    ip = entry.data.get('ip')
    name = entry.data.get('name')
    mac = entry.data.get('mac')
    account = entry.data.get('account')

    # 使用entry_id作为key，避免IP冲突
    entry_id = entry.entry_id

    if ping_ip(ip):
        status = "0"
    else:
        status = "-1"

    _LOGGER.debug(f"获取初始化信息完成，开始创建设备IP: {ip}, Name:{name}, Mac:{mac}, Status: {status}")

    coordinator = DEVICEDataUpdateCoordinator(hass, entry, ip, name, mac, status)

    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    # 使用entry_id作为key存储coordinator
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry_id] = coordinator

    _LOGGER.info(f"创建设备完成IP: {ip}, Name:{name}, Mac:{mac}, Status: {status}")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def update_listener(hass, entry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    """Handle removal of an entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    
    # 清理数据
    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        
    return unload_ok

async def async_remove_entry(hass, entry):
    """Handle removal of an entry."""
    _LOGGER.info(f"删除设备: {entry.data.get('name')}")
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)

class DEVICEDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching DEVICE data."""

    def __init__(self, hass, entry, ip, name, mac, status):
        self.hass = hass
        self.entry = entry
        self.ip = ip
        self.name = name
        self.mac = mac
        self.status = status
        self._isenable = True

        super().__init__(
            hass,
            _LOGGER,
            name=self.name,
            update_interval=timedelta(minutes=10),
        )

    def set_device_enabled(self, enabled):
        self._isenable = enabled

    async def _async_update_data(self):
        """Fetch data from My Custom Device."""
        try:
            if ping_ip(self.ip):
                self.status = "0"
            else:
                self.status = "-1"
            return json.loads('{"ip":"' + self.ip
                              + '","name":"' + self.name
                              + '","status":"' + self.status + '"}')
        except Exception as err:
            raise UpdateFailed(f"Error communicating with My Custom Device: {err}")
