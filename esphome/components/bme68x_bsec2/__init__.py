import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c
from esphome.const import CONF_ID

CODEOWNERS = ["@bootmagic"]
DEPENDENCIES = ["i2c"]
AUTO_LOAD = ["sensor", "text_sensor"]
MULTI_CONF = True

CONF_BME680_BSEC_ID = "bme68x_bsec2_id"
CONF_TEMPERATURE_OFFSET = "temperature_offset"
CONF_IAQ_MODE = "iaq_mode"
CONF_SAMPLE_RATE = "sample_rate"
CONF_STATE_SAVE_INTERVAL = "state_save_interval"
CONF_BSEC_CONFIG = "bsec_configuration" #Do we need this?

bme68x_bsec2_ns = cg.esphome_ns.namespace("bme68x_bsec2")

IAQMode = bme68x_bsec2_ns.enum("IAQMode")
IAQ_MODE_OPTIONS = {
    "STATIC": IAQMode.IAQ_MODE_STATIC,
    "MOBILE": IAQMode.IAQ_MODE_MOBILE,
}

SampleRate = bme68x_bsec2_ns.enum("SampleRate")
SAMPLE_RATE_OPTIONS = {
    "LP": SampleRate.SAMPLE_RATE_LP,
    "ULP": SampleRate.SAMPLE_RATE_ULP,
}

BME68xBSEC2Component = bme68x_bsec2_ns.class_(
    "BME68xBSEC2Component", cg.Component, i2c.I2CDevice
)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(BME68xBSEC2Component),
        cv.Optional(CONF_TEMPERATURE_OFFSET, default=0): cv.temperature,
        cv.Optional(CONF_IAQ_MODE, default="STATIC"): cv.enum(
            IAQ_MODE_OPTIONS, upper=True
        ),
        cv.Optional(CONF_SAMPLE_RATE, default="LP"): cv.enum(
            SAMPLE_RATE_OPTIONS, upper=True
        ),
        cv.Optional(
            CONF_STATE_SAVE_INTERVAL, default="6hours"
        ): cv.positive_time_period_minutes,
        cv.Optional(CONF_BSEC_CONFIG, default=""): cv.string,
    },
    cv.only_with_arduino,
).extend(i2c.i2c_device_schema(0x76))


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)

    cg.add(var.set_device_id(str(config[CONF_ID])))
    cg.add(var.set_temperature_offset(config[CONF_TEMPERATURE_OFFSET]))
    cg.add(var.set_iaq_mode(config[CONF_IAQ_MODE]))
    cg.add(var.set_sample_rate(config[CONF_SAMPLE_RATE]))
    cg.add(
        var.set_state_save_interval(config[CONF_STATE_SAVE_INTERVAL].total_milliseconds)
    )

    if config[CONF_BSEC_CONFIG] != "":
        # Convert BSEC config to int array and hand it to .cpp
        temp = [int(a) for a in config[CONF_BSEC_CONFIG].split(",")]
        cg.add_define("BME68x_BSEC2_CONFIGURATION", temp)

    # Although this component does not use SPI, the BSEC library requires the SPI library
    cg.add_library("SPI", None)

    cg.add_define("USE_BSEC")
    cg.add_library(
        "BME68x Sensor library",
        "1.1.40407",
        "https://github.com/BoschSensortec/Bosch-BME68x-Library.git",
    )
    cg.add_library(
        "BSEC2 Software Library",
        "1.4.2200",
        "https://github.com/BoschSensortec/Bosch-BSEC2-Library.git",
    )
