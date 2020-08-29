import os
import sys
import ctypes

LED_MAX_NAME_SIZE = 64
ULEDS_DEVICE = "/dev/uleds"
ULEDS_SYS_PATH = "/sys/class/leds"

class uleds_user_dev(ctypes.Structure):
     _fields_ = [("name", ctypes.c_char * LED_MAX_NAME_SIZE), ("max-brightness", ctypes.c_int)]

     def __repr__(self):
         print(f"name={self.name} max_brightness={self.max_brightness}")


class uled:
    def __init__(self, uleds_user_dev):
        self._struct = uleds_user_dev
        self._brightness = 0
        try:
            self._uleds = os.open(ULEDS_DEVICE, os.O_RDWR)
            os.write(self._uleds, self._struct)
            os.set_blocking(self._uleds, False)
            self._uleds_sys = os.path.join(ULEDS_SYS_PATH, self._struct.name.decode())
        except Exception as e:
            print(f"Failed to initialise uleds device: {e}")
            print(f'Ensure that the `uleds` kernel module is loaded and you have r/w access to {ULEDS_DEVICE}.')
            self._uleds = None
            self._uleds_sys = None

    def get(self):
        try:
            data = os.read(self._uleds, ctypes.sizeof(ctypes.c_int))
            if data != b'':
                self._brightness = int.from_bytes(data, sys.byteorder)
            return self._brightness
        except OSError as e:
            if e.errno == 11:
                return self._brightness
        except Exception as e:
            print(f"Failed to get uleds status: {e}")
            return None

    def get_triggers(self):
        try:
            # returns a list of available led triggers from `/sys/class/led/<led name>/trigger` and
            # the currently set trigger as a tuple
            triggers_f = os.open(os.path.join(self._uleds_sys, "trigger"), os.O_RDWR)
            triggers = list(os.read(triggers_f, 2048).decode().split(" "))
            current_trigger = [t for t in triggers if t.startswith("[")][0]
            triggers[triggers.index(f"{current_trigger}")] = current_trigger[1:-1]
            return (triggers, current_trigger[1:-1])
        except Exception as e:
            print(f"Failed to get led triggers: {e}")
            return None

    def set_trigger(self, trigger):
        try:
            triggers_f = os.open(os.path.join(self._uleds_sys, "trigger"), os.O_RDWR)
            os.write(triggers_f, trigger.encode())
        except Exception as e:
            print(f"Failed to set led trigger: {e}")

    def close(self):
        try:
            os.close(self._uleds)
            self._uleds_sys = None
        except Exception as e:
            print(f"Failed to close uleds device: {e}")
