import logging
from homeassistant.components.switch import SwitchEntity
from .const import (
    DOMAIN,
)
from .utils import ping_ip

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    ip = config_entry.data.get('ip')
    name = config_entry.data.get('name')
    mac = config_entry.data.get('mac')
    account = config_entry.data.get('account')

    # 使用config_entry.entry_id来获取对应的coordinator
    entry_id = config_entry.entry_id
    coordinator = hass.data[DOMAIN][entry_id]
    
    my_switch = MyCustomSwitch(coordinator, hass, config_entry, ip, name, mac, account)
    async_add_entities([my_switch], False)

class MyCustomSwitch(SwitchEntity):
    def __init__(self, coordinator, hass, entry, ip, name, mac, account):
        super().__init__()
        self.coordinator = coordinator
        self.hass = hass
        self.entry = entry
        self._ip = ip
        self._name = name
        self._mac = mac
        self._account = account
        
        # 使用entry_id作为唯一ID的一部分，避免冲突
        self._unique_id = f"{ip}_{mac}_{entry.entry_id}"
        
        if self.coordinator.data["status"] == "0":
            self._state = True
        else:
            self._state = False

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        _LOGGER.debug("Data will be update every %s", self.coordinator.data)
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "manufacturer": "Custom",
            "model": "Network Wake PC",
        }

    @property
    def is_on(self):
        self._state = ping_ip(self._ip)
        _LOGGER.debug(f"设备的ip[is_on]: {self._ip}")
        _LOGGER.debug(f"设备的状态[is_on]: {self._state}")
        return self._state

    async def set_state(self, state):
        self._state = state

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self._state = True
        self.schedule_update_ha_state()
        _LOGGER.debug(f"设备的ip: {self._ip}")

        from wakeonlan import send_magic_packet
        send_magic_packet(self._mac.strip().upper())

        _LOGGER.debug("---------------switch async_turn_on----------------")

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._state = False
        self.schedule_update_ha_state()
        _LOGGER.debug(f"设备的ip: {self._ip}")
        _LOGGER.debug(f"设备的account: {self._account}")
        _LOGGER.debug("---------------switch async_turn_off----------------")
