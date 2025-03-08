from .I2CTeensy import I2CTeensy
from .SPITeensy import SPITeensy


def get_communication_manager(instance_name):
    if instance_name == "I2CTeensy":
        return I2CTeensy()
    elif instance_name == "SPITeensy":
        return SPITeensy()
    else:
        raise ValueError("Unknown communication manager")