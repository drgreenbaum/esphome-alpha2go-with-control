import esphome.codegen as cg
from esphome.components import text_sensor
import esphome.config_validation as cv

from . import Alpha2, CONF_ALPHA2_ID

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ALPHA2_ID): cv.use_id(Alpha2),
        # Device info (ASCII) fields, found 2026-09-04 - matches the app's
        # "Product info" screen exactly (GENIbus Class 7, not the usual
        # Class 10 registers). Fetched once per connection, not polled.
        # See memory: grundfos-alpha2-control.
        cv.Optional("product_type"): text_sensor.text_sensor_schema(),
        cv.Optional("product_no"): text_sensor.text_sensor_schema(),
        cv.Optional("serial_no"): text_sensor.text_sensor_schema(),
        cv.Optional("production_code"): text_sensor.text_sensor_schema(),
        cv.Optional("gsc_description"): text_sensor.text_sensor_schema(),
        cv.Optional("gsc_identification"): text_sensor.text_sensor_schema(),
        cv.Optional("app_software"): text_sensor.text_sensor_schema(),
        cv.Optional("ble_software"): text_sensor.text_sensor_schema(),
    }
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_ALPHA2_ID])

    if product_type_config := config.get("product_type"):
        sens = await text_sensor.new_text_sensor(product_type_config)
        cg.add(hub.set_product_type_text_sensor(sens))

    if product_no_config := config.get("product_no"):
        sens = await text_sensor.new_text_sensor(product_no_config)
        cg.add(hub.set_product_no_text_sensor(sens))

    if serial_no_config := config.get("serial_no"):
        sens = await text_sensor.new_text_sensor(serial_no_config)
        cg.add(hub.set_serial_no_text_sensor(sens))

    if production_code_config := config.get("production_code"):
        sens = await text_sensor.new_text_sensor(production_code_config)
        cg.add(hub.set_production_code_text_sensor(sens))

    if gsc_description_config := config.get("gsc_description"):
        sens = await text_sensor.new_text_sensor(gsc_description_config)
        cg.add(hub.set_gsc_description_text_sensor(sens))

    if gsc_identification_config := config.get("gsc_identification"):
        sens = await text_sensor.new_text_sensor(gsc_identification_config)
        cg.add(hub.set_gsc_identification_text_sensor(sens))

    if app_software_config := config.get("app_software"):
        sens = await text_sensor.new_text_sensor(app_software_config)
        cg.add(hub.set_app_software_text_sensor(sens))

    if ble_software_config := config.get("ble_software"):
        sens = await text_sensor.new_text_sensor(ble_software_config)
        cg.add(hub.set_ble_software_text_sensor(sens))
