from .DirectPWM import DirectPWM


def get_communication_manager(instance_name, driving_mode = 0):
    if instance_name == "DirectPWM":
        return DirectPWM(driving_mode)
    else:
        raise ValueError("Unknown communication manager")