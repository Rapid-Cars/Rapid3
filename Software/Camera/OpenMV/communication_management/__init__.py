from .I2CTeensy import I2CTeensy
from .SPITeensy import SPITeensy
from .DirectPWM import DirectPWM


def get_communication_manager(instance_name):
    if instance_name == "I2CTeensy":
        return I2CTeensy()
    elif instance_name == "SPITeensy":
        return SPITeensy()
    elif instance_name == "DirectPWM":
        return DirectPWM()
    else:
        raise ValueError("Unknown communication manager")