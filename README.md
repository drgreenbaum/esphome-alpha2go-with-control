# ESPHome Component for Grundfos Alpha2 GO Pumps (with control)

ESPHome component for reading measurement values **and controlling** a Grundfos
Alpha2 GO circulator pump via Bluetooth LE (GENIbus-over-BLE), from an ESP32.

This started as a fork of the read-only sensor component originally posted at
[esphome/esphome#13003](https://github.com/esphome/esphome/tree/dev/esphome/components/alpha3)
/ the original `alpha2` component this repo was forked from. It has since grown
into a much larger component with real, hardware-confirmed **write** support
(start/stop, operating mode, setpoints, flow limits, venting, panel lock,
display sleep) on top of the original sensor readings, reverse-engineered from
BLE HCI captures of the official Grundfos GO app.

**Disclaimer:** this is unofficial, reverse-engineered from passive traffic
analysis, not from any Grundfos documentation. It works on an ALPHA2 GO
15-50/60 (product code 93074220) - other models/firmware versions may differ
or may not work at all. Use at your own risk, especially the write features.

## What it supports

- **Sensors:** flow, head (pressure), speed (RPM), power, voltage, current,
  calculated media temperature, start count (`Antal starter`).
- **Binary sensor:** manual venting in progress.
- **Switches:** pump start/stop, external control (PWM), night setback, min/
  max flow limit enable, continuous venting, panel lock, prevent display
  sleep - all with live GET-response readback, not just optimistic write-echo.
- **Numbers:** pressure/flow/speed setpoint, min/max flow limit value.
- **Select:** operating mode (Konstant tryck / Proportionellt tryck /
  Konstantkurva / Konstant flöde / AutoAdapt variants).
- **Text sensors:** device info (product type/number, serial number,
  production code, app/BLE firmware version, GSC identification/description).
- Manual venting (start on pump only / start on system+pump / cancel) via a
  `write_venting()` method, meant to be called from a `button:` lambda in your
  own device YAML (see example below) since it's a momentary action rather
  than a persistent entity.

Bluetooth writes require the pump to accept a bonded, encrypted BLE
connection (`esp32_ble: auth_req_mode: sc_bond`) - see the example below.

## How to add it as an external component in Home Assistant / ESPHome

1. Access your `/config/esphome/` folder (e.g. via the Samba/SMB add-on in
   Home Assistant OS).
2. Create a folder named `components`.
3. Copy the `alpha2` folder from this repository into it.

In your ESPHome device YAML:

```yaml
external_components:
 - source:
     type: local
     path: components
   components: [alpha2]

esp32_ble_tracker:

# Needed for write support - the pump appears to gate Class-10 SET writes on
# bonded status, not just an encrypted link.
esp32_ble:
  auth_req_mode: sc_bond

ble_client:
  - mac_address: XX:XX:XX:XX:XX:XX # your pump's bluetooth mac here
    id: heatingpump

sensor:
  - platform: alpha2
    id: alpha2_pump
    ble_client_id: heatingpump
    flow:
      name: "Pump Flow"
      state_class: measurement
      device_class: volume_flow_rate
    head:
      name: "Pump Pressure"
      state_class: measurement
    speed:
      name: "Pump Speed"
      state_class: measurement
      accuracy_decimals: 0
    power:
      name: "Pump Power"
      state_class: measurement
      device_class: power
    voltage:
      name: "Pump Voltage"
      state_class: measurement
      device_class: voltage
    current:
      name: "Pump Current"
      state_class: measurement
      device_class: current
    medietemperatur:
      name: "Pump Media Temperature"
      unit_of_measurement: "°C"
      device_class: temperature
      state_class: measurement
    antal_starter:
      name: "Pump Start Count"
      state_class: total_increasing

binary_sensor:
  - platform: alpha2
    alpha2_id: alpha2_pump
    avluftning_pagar:
      name: "Pump Venting In Progress"

switch:
  - platform: alpha2
    type: power
    alpha2_id: alpha2_pump
    name: "Pump Start/Stop"
    restore_mode: RESTORE_DEFAULT_OFF
  - platform: alpha2
    type: extern_kontroll
    alpha2_id: alpha2_pump
    name: "Pump External Control"
  - platform: alpha2
    type: nattsankning
    alpha2_id: alpha2_pump
    name: "Pump Night Setback"
  - platform: alpha2
    type: min_flow_limit
    alpha2_id: alpha2_pump
    name: "Pump Min Flow Limit Enable"
  - platform: alpha2
    type: max_flow_limit
    alpha2_id: alpha2_pump
    name: "Pump Max Flow Limit Enable"
  - platform: alpha2
    type: continuous_venting
    alpha2_id: alpha2_pump
    name: "Pump Continuous Venting"
  - platform: alpha2
    type: panel_lock
    alpha2_id: alpha2_pump
    name: "Pump Panel Lock"
  - platform: alpha2
    type: prevent_display_sleep
    alpha2_id: alpha2_pump
    name: "Pump Prevent Display Sleep"

select:
  - platform: alpha2
    alpha2_id: alpha2_pump
    name: "Pump Operating Mode"

number:
  - platform: alpha2
    type: pressure_setpoint
    alpha2_id: alpha2_pump
    name: "Pump Pressure Setpoint"
  - platform: alpha2
    type: flow_setpoint
    alpha2_id: alpha2_pump
    name: "Pump Flow Setpoint"
  - platform: alpha2
    type: speed_setpoint
    alpha2_id: alpha2_pump
    name: "Pump Speed Setpoint"
  - platform: alpha2
    type: min_flow_limit
    alpha2_id: alpha2_pump
    name: "Pump Min Flow Limit Value"
  - platform: alpha2
    type: max_flow_limit
    alpha2_id: alpha2_pump
    name: "Pump Max Flow Limit Value"

text_sensor:
  - platform: alpha2
    alpha2_id: alpha2_pump
    product_type:
      name: "Pump Product Type"
    serial_no:
      name: "Pump Serial Number"
    app_software:
      name: "Pump App Software Version"
    ble_software:
      name: "Pump BLE Software Version"

button:
  - platform: template
    name: "Vent Pump"
    on_press:
      - lambda: id(alpha2_pump)->write_venting(true, 0x01);
  - platform: template
    name: "Vent System And Pump"
    on_press:
      - lambda: id(alpha2_pump)->write_venting(true, 0x02);
  - platform: template
    name: "Cancel Venting"
    on_press:
      - lambda: id(alpha2_pump)->write_venting(false);
```

For the first connection you may need to press the pump's physical
"Connectivity" button to allow a new device to pair/bond, the same way the
official app originally paired. To find your pump's Bluetooth MAC address,
use an app like [nRF Connect](https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp).

## Notes / known limitations

- Flash usage is significant on smaller ESP32 boards once most of these
  entities are enabled together - only configure the platforms/types you
  actually need.
- Speed setpoint scale (raw RPM, no conversion) is confirmed working but was
  only validated against one pump; double-check against your app's displayed
  value the first time you use it.
- "Kumulativ effektförbrukning" (cumulative energy) and true lifetime runtime
  are NOT exposed by this component - they don't appear anywhere in the
  routine BLE traffic the app generates during normal use; they may only be
  requested on-demand by a specific app screen that hasn't been captured yet.
