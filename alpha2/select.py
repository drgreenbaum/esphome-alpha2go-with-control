import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import select

from . import Alpha2, CONF_ALPHA2_ID, alpha2_ns

Alpha2DriftlageSelect = alpha2_ns.class_("Alpha2DriftlageSelect", select.Select, cg.Component)

# Options and their GENIbus codes - see ALPHA2_DRIFTLAGE_OPTIONS in
# alpha2.cpp (the two lists must stay in sync) and memory:
# grundfos-alpha2-control for how each code was confirmed.
DRIFTLAGE_OPTIONS = [
    "Konstant tryck",
    "Proportionellt tryck",
    "Konstantkurva",
    "Konstant flöde",
    "Proportionellt tryck + AutoAdapt",
    "Konstant tryck + AutoAdapt",
]

CONFIG_SCHEMA = select.select_schema(Alpha2DriftlageSelect).extend(
    {
        cv.GenerateID(CONF_ALPHA2_ID): cv.use_id(Alpha2),
    }
)


async def to_code(config):
    var = await select.new_select(config, options=DRIFTLAGE_OPTIONS)
    await cg.register_component(var, config)
    hub = await cg.get_variable(config[CONF_ALPHA2_ID])
    cg.add(var.set_parent(hub))
    cg.add(hub.set_driftlage_select(var))
