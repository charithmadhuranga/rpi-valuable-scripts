#---------------------------------------------------------------------------------------
#Manages Hardware for Dehumidifier
#---------------------------------------------------------------------------------------
#import shell modules
import sys
import signal

#set proper path for modules
sys.path.append('/home/pi/oasis-grow')

import rusty_pins
from peripherals import relays
from utils import concurrent_state as cs
from utils import error_handler as err

resource_name = "dehumidifier"
cs.check_lock(resource_name)

#get hardware config
cs.load_state()
dehum_GPIO = int(cs.structs["hardware_config"]["equipment_gpio_map"]["dehumidifier_relay"]) #dehumidifier pin pulls from config file
pin = rusty_pins.GpioOut(dehum_GPIO)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, cs.wrapped_sys_exit)
    try:
        while True:
            if cs.structs["feature_toggles"]["dehum_pid"] == "1":
                print("Running dehumidifier in pulse mode with " + cs.structs["control_params"]["dehum_feedback"] + "%" + " power...")
                relays.actuate_slow_pwm(pin, float(cs.structs["control_params"]["dehum_feedback"]), wattage=cs.structs["hardware_config"]["equipment_wattage"]["dehumidifier"], log="dehumidifier_kwh") #trigger appropriate response
            else:
                print("Running dehumidifier for " + cs.structs["control_params"]["dehumidifier_duration"] + " minute(s) on, " + cs.structs["control_params"]["dehumidifier_interval"] + " minute(s) off...")
                relays.actuate_interval_sleep(pin, float(cs.structs["control_params"]["dehumidifier_duration"]), float(cs.structs["control_params"]["dehumidifier_interval"]), duration_units= "minutes", sleep_units="minutes", wattage=cs.structs["hardware_config"]["equipment_wattage"]["dehumidifier"], log="dehumidifier_kwh")
            cs.load_state()
    except SystemExit:
        print("Dehumidifier was terminated.")
    except KeyboardInterrupt:
        print("Dehumidifier was interrupted.")
    except Exception:    
        print("Dehumidifier encountered an error!")
        print(err.full_stack())
    finally:
        print("Shutting down dehumidifier...")
        try:
            relays.turn_off(pin)
        except:
            print(resource_name + " has no relay objects remaining.")
        
        cs.rusty_pipes.unlock(cs.lock_filepath, resource_name)
