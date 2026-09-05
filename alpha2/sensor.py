import esphome.codegen as cg
from esphome.components import ble_client, sensor
import esphome.config_validation as cv
from esphome.const import (
    CONF_CURRENT,
    CONF_FLOW,
    CONF_HEAD,
    CONF_ID,
    CONF_POWER,
    CONF_SPEED,
    CONF_VOLTAGE,
    UNIT_AMPERE,
    UNIT_CELSIUS,
    UNIT_CUBIC_METER_PER_HOUR,
    UNIT_METER,
    UNIT_REVOLUTIONS_PER_MINUTE,
    UNIT_VOLT,
    UNIT_WATT,
)

from . import Alpha2

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(Alpha2),
            cv.Optional(CONF_FLOW): sensor.sensor_schema(
                unit_of_measurement=UNIT_CUBIC_METER_PER_HOUR,
                accuracy_decimals=2,
            ),
            cv.Optional(CONF_HEAD): sensor.sensor_schema(
                unit_of_measurement=UNIT_METER,
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_POWER): sensor.sensor_schema(
                unit_of_measurement=UNIT_WATT,
                accuracy_decimals=2,
            ),
            cv.Optional(CONF_CURRENT): sensor.sensor_schema(
                unit_of_measurement=UNIT_AMPERE,
                accuracy_decimals=2,
            ),
            cv.Optional(CONF_SPEED): sensor.sensor_schema(
                unit_of_measurement=UNIT_REVOLUTIONS_PER_MINUTE,
                accuracy_decimals=0,
            ),
            cv.Optional(CONF_VOLTAGE): sensor.sensor_schema(
                unit_of_measurement=UNIT_VOLT,
                accuracy_decimals=2,
            ),
            # Raw driftläge (operating mode) code: 0=Konstant tryck,
            # 1=Proportionellt tryck, 2=Konstantkurva (unconfirmed),
            # 8=Konstant flöde, 13=AutoAdapt. No standard unit/device class -
            # it's an enum code, not a measurement. See memory:
            # grundfos-alpha2-control.
            cv.Optional("driftlage"): sensor.sensor_schema(
                accuracy_decimals=0,
            ),
            # Extern kontroll (external control) on/off, register 5c0193.
            # Raw uint16 (OFF=0x0000, ON=0x7b00, both confirmed). Registers
            # swapped 2026-09-04 evening - was wrongly 5a0008. See memory:
            # grundfos-alpha2-control.
            cv.Optional("extern_kontroll"): sensor.sensor_schema(
                accuracy_decimals=0,
            ),
            # Nattsänkning (night setback), register 5a0008. Raw 0/1 boolean,
            # confirmed. Registers swapped 2026-09-04 evening - was wrongly
            # 5c0193. See memory: grundfos-alpha2-control.
            cv.Optional("nattsankning"): sensor.sensor_schema(
                accuracy_decimals=0,
            ),
            # Avluftningsstatus, register 580263. Raw code: 1=manuell
            # avluftning pågår, 2=kontinuerlig avluftning av, 3=kontinuerlig
            # avluftning på. Confirmed 2026-09-04. See memory:
            # grundfos-alpha2-control.
            cv.Optional("avluftningsstatus"): sensor.sensor_schema(
                accuracy_decimals=0,
            ),
            # Avluftning nedräkning, samma register 560008 - rått
            # nedräkningsvärde (enhet okänd, minskar för snabbt för att vara
            # sekunder rakt av). Bara meningsfullt medan avluftning_pagar=1.
            # See memory: grundfos-alpha2-control.
            cv.Optional("avluftning_nedrakning"): sensor.sensor_schema(
                accuracy_decimals=1,
            ),
            # Beräknad medietemperatur, register 5d012c (2026-09-04) -
            # matched against the app's "Visa alla mätvärden" screen. See
            # memory: grundfos-alpha2-control.
            cv.Optional("medietemperatur"): sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                device_class="temperature",
                state_class="measurement",
                accuracy_decimals=1,
            ),
            # Antal starter, register 5d0001 (2026-09-04) - confirmed via a
            # before/after restart diff (283->290). See memory:
            # grundfos-alpha2-control.
            cv.Optional("antal_starter"): sensor.sensor_schema(
                state_class="total_increasing",
                accuracy_decimals=0,
            ),
        }
    )
    .extend(ble_client.BLE_CLIENT_SCHEMA)
    .extend(cv.polling_component_schema("15s"))
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await ble_client.register_ble_node(var, config)

    if flow_config := config.get(CONF_FLOW):
        sens = await sensor.new_sensor(flow_config)
        cg.add(var.set_flow_sensor(sens))

    if head_config := config.get(CONF_HEAD):
        sens = await sensor.new_sensor(head_config)
        cg.add(var.set_head_sensor(sens))

    if power_config := config.get(CONF_POWER):
        sens = await sensor.new_sensor(power_config)
        cg.add(var.set_power_sensor(sens))

    if current_config := config.get(CONF_CURRENT):
        sens = await sensor.new_sensor(current_config)
        cg.add(var.set_current_sensor(sens))

    if speed_config := config.get(CONF_SPEED):
        sens = await sensor.new_sensor(speed_config)
        cg.add(var.set_speed_sensor(sens))

    if voltage_config := config.get(CONF_VOLTAGE):
        sens = await sensor.new_sensor(voltage_config)
        cg.add(var.set_voltage_sensor(sens))

    if driftlage_config := config.get("driftlage"):
        sens = await sensor.new_sensor(driftlage_config)
        cg.add(var.set_driftlage_sensor(sens))

    if extern_kontroll_config := config.get("extern_kontroll"):
        sens = await sensor.new_sensor(extern_kontroll_config)
        cg.add(var.set_extern_control_sensor(sens))

    if nattsankning_config := config.get("nattsankning"):
        sens = await sensor.new_sensor(nattsankning_config)
        cg.add(var.set_night_setback_sensor(sens))

    if avluftningsstatus_config := config.get("avluftningsstatus"):
        sens = await sensor.new_sensor(avluftningsstatus_config)
        cg.add(var.set_venting_status_sensor(sens))

    if avluftning_nedrakning_config := config.get("avluftning_nedrakning"):
        sens = await sensor.new_sensor(avluftning_nedrakning_config)
        cg.add(var.set_venting_countdown_sensor(sens))

    if medietemperatur_config := config.get("medietemperatur"):
        sens = await sensor.new_sensor(medietemperatur_config)
        cg.add(var.set_media_temp_sensor(sens))

    if antal_starter_config := config.get("antal_starter"):
        sens = await sensor.new_sensor(antal_starter_config)
        cg.add(var.set_antal_starter_sensor(sens))
