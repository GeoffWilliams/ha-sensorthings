import voluptuous as vol


from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant , callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from .const import (
    DOMAIN,
    CONF_URL, 
    CONF_AUTH_BASIC_USERNAME, 
    CONF_AUTH_BASIC_PASSWORD, 
    CONF_INTERVAL,
    CONF_SENSOR_MAP
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Required(CONF_AUTH_BASIC_USERNAME): str,
        vol.Required(CONF_AUTH_BASIC_PASSWORD): str,
        vol.Required(CONF_INTERVAL, default=60): vol.Coerce(int),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SENSOR_MAP): selector(
            {
                "object": {
                    "multiple": True,
                    "label_field": "iot_id",
                    "description_field": "entity",
                    "fields": {
                        "iot_id": {
                            "label": "@iot_id",
                            "selector": {
                                "number": {}
                            }
                        },
                        "entity": {
                            "label": "entity",
                            "selector": {
                                "entity": {
                                    "domain": "sensor"
                                }
                            }
                        }
                    }
                }
            }
        )
    }
)


class SensorThingsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SensorThings."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            # Optional: validate input
            if not user_input[CONF_URL].startswith("http"):
                errors[CONF_URL] = "invalid_url"

            if not errors:
                return self.async_create_entry(
                    title="SensorThings",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return SensorThingsOptionsFlowHandler()
    
class SensorThingsOptionsFlowHandler(OptionsFlow):
    """Options flow for SensorThings."""

    # def __init__(self, config_entry: ConfigEntry) -> None:
    #     """Initialize options flow."""
    #     self.config_entry = config_entry
    #     self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(title="", data=options)


        # schema = vol.Schema(
        #     {
        #         vol.Required(
        #             CONF_SENSOR_MAP
        #             # default=self.config_entry.options | {}
        #         ): selector(
        #             {
        #                 "object": {
        #                     "multiple": True,
        #                     "label_field": "iot_id",
        #                     "description_field": "entity",
        #                     "fields": {
        #                         "iot_id": {
        #                             "label": "@iot_id",
        #                             "selector": {
        #                                 "number": {}
        #                             }
        #                         },
        #                         "entity": {
        #                             "name": "entity",
        #                             "selector": {
        #                                 "text": {}
        #                                 #"entity": {"domain": "sensor"}
        #                             }
        #                         }
        #                     }
        #                 }
        #             }
        #         )
        #     }
        # )

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            ),
            # data_schema=self.add_suggested_values_to_schema(
            #     schema, self.config_entry.options
            # ),
        )
