"""
Sensor module for BME280.
"""

from typing import cast

from ...exceptions import RuntimeConfigError
from ...types import CerberusSchemaType, ConfigType, SensorValueType
from . import GenericSensor

REQUIREMENTS = ("smbus2", "RPi.bme280")
CONFIG_SCHEMA: CerberusSchemaType = {
    "i2c_bus_num": dict(type="integer", required=True, empty=False),
    "chip_addr": dict(type="integer", required=True, empty=False),
}


class Sensor(GenericSensor):
    """
    Implementation of Sensor class for the BME280 sensor.
    """

    SENSOR_SCHEMA: CerberusSchemaType = {
        "type": dict(
            type="string",
            required=False,
            empty=False,
            default="temperature",
            allowed=["temperature", "humidity", "pressure"],
        )
    }

    def setup_module(self) -> None:
        # pylint: disable=import-outside-toplevel,attribute-defined-outside-init
        # pylint: disable=import-error,no-member
        from smbus2 import SMBus  # type: ignore
        import bme280  # type: ignore

        self.bus = SMBus(self.config["i2c_bus_num"])
        self.address: int = self.config["chip_addr"]
        self.bme = bme280
        self.calib = bme280.load_calibration_params(self.bus, self.address)

    def get_value(self, sens_conf: ConfigType) -> SensorValueType:
        """
        Get the temperature, humidity or pressure value from the sensor
        """
        # pylint: disable=no-member
        data = self.bme.sample(self.bus, self.address, self.calib)

        if sens_conf["type"] == "temperature":
            return cast(SensorValueType, data.temperature)
        if sens_conf["type"] == "humidity":
            return cast(SensorValueType, data.humidity)
        if sens_conf["type"] == "pressure":
            return cast(SensorValueType, data.pressure)
        raise RuntimeConfigError(
            (
                "bme280 sensor '%s' was not configured to return 'temperature', "
                "'humidity' or 'pressure'"
            )
            % sens_conf["name"]
        )
