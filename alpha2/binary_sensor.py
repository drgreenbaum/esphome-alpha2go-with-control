import esphome.codegen as cg
from esphome.components import binary_sensor
import esphome.config_validation as cv

from . import Alpha2, CONF_ALPHA2_ID

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ALPHA2_ID): cv.use_id(Alpha2),
        # Manuell avluftning pågår, register 560008 (2026-09-04) - confirmed
        # via a real capture bracketing two full manual venting sessions.
        # See memory: grundfos-alpha2-control.
        cv.Optional("avluftning_pagar"): binary_sensor.binary_sensor_schema(),
    }
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_ALPHA2_ID])

    if avluftning_pagar_config := config.get("avluftning_pagar"):
        sens = await binary_sensor.new_binary_sensor(avluftning_pagar_config)
        cg.add(hub.set_venting_active_sensor(sens))
