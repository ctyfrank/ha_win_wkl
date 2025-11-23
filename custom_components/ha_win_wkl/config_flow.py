"""
Hass.io My Custom Switch Plugin Config Flow
"""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class MyCustomSwitchFlowHandler(config_entries.ConfigFlow):
    """Handle a config flow for My Custom Switch."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # 为每个设备生成唯一ID
            unique_id = f"{user_input['ip']}_{user_input['mac']}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=f"电脑唤醒 - {user_input['name']}", 
                data=user_input
            )

        # 配置表单
        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required("ip", default=""): str,
                vol.Required("name", default=""): str,
                vol.Required("mac", default=""): str,
                vol.Required("account", default=""): str,
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return MyCustomSwitchOptionsFlowHandler(config_entry)


class MyCustomSwitchOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for My Custom Switch."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            if user_input.get("remove_device"):
                # 删除设备
                return self.async_abort(reason="device_removed")
            
            # 可以在这里添加其他选项，比如更新配置
            return self.async_create_entry(title="", data={})

        # 显示选项表单
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("remove_device", default=False): bool,
            }),
            description_placeholders={
                "device_name": self.config_entry.data.get("name", "Unknown")
            }
        )
