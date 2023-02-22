#!/usr/bin/env python3
import evdev
import sys
from evdev import ecodes

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

if not devices:
    print('Error: No evdev devices found on your system.',
          'Check your evdev installation and device permissions.')
    sys.exit(1)

if "--list-devices" in sys.argv:
    print("\nAvailable devices:")
    print("==============================================================")
    print("Path               (Name)")
    print("================== ===========================================")
    for device in devices:
        print(device.path, "(" + device.name + ")")
    print("================= ============================================\n")
    sys.exit(0)

if "-d" in sys.argv:
    inputDevice = sys.argv[sys.argv.index("-d") + 1]
    for device in devices:
        if device.path == inputDevice:
            break
    else:
        print('Error: Device', inputDevice, 'not found')
        sys.exit(1)
    
else:
    print("\nUsage:\n")
    print("       ", sys.argv[0], "-d <device> [--quirk-fix]\n")
    print("       ", sys.argv[0], "--list-devices\n")
    sys.exit(0)

print("Using: " + device.path + " (" + device.name + ")")
idVendorProduct = "" + str(device.info.vendor) + ":" + str(device.info.product)

caps = {
        ecodes.EV_MSC : [ecodes.MSC_SCAN],
        }

deviceCapabilities = device.capabilities()
if ecodes.EV_ABS in deviceCapabilities:
    caps[ecodes.EV_ABS] = deviceCapabilities[ecodes.EV_ABS]
else:
    # Some devices do not have axis, so fake at least two axis
    caps[ecodes.EV_ABS] = [ecodes.ABS_X, ecodes.ABS_Y]

if ecodes.EV_KEY in deviceCapabilities:
    caps[ecodes.EV_KEY] = deviceCapabilities[ecodes.EV_KEY]
else:
    # Some devices do not have buttons, so fake at least one button
    caps[ecodes.EV_KEY] = [ecodes.BTN_JOYSTICK, ecodes.BTN_TRIGGER]

# Quirk Fix: For pedals that may need the extra X/Y axis,
# e.g. ATMEL/VIRPIL/191105 VPC Rudder Pedals, VKBsim T-Rudder 
if "--quirk-fix" in sys.argv:
    print ("Warning: Applying quirk (add X/Y axis) for " + device.name +  "!")
    caps[ecodes.EV_ABS].append(ecodes.ABS_X)
    caps[ecodes.EV_ABS].append(ecodes.ABS_Y)

spoofdevice = evdev.uinput.UInput(events=caps,
                                  name=device.name + " PRO",
                                  vendor=device.info.vendor, 
                                  product=device.info.product,
                                  version=device.info.version)

print("Spoofing:", spoofdevice)
print("Mirroring events. Press Ctrl-C twice for exit.")

for event in device.read_loop():
    spoofdevice.write_event(event)
    spoofdevice.syn()

