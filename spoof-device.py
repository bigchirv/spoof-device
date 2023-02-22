#!/usr/bin/env python3
# See the original script at https://github.com/beniwtv/evdev-spoof-device
# Read https://github.com/starcitizen-lug/knowledge-base/wiki/Sticks,-Throttles,-&-Pedals
#
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
    print("       ", sys.argv[0], "-d <device>\n")
    print("       ", sys.argv[0], "--list-devices\n")
    sys.exit(0)

print("Using: " + device.path + " (" + device.name + ")")

caps = {
    ecodes.EV_MSC: [ecodes.MSC_SCAN],
    ecodes.EV_ABS: [ecodes.ABS_X, ecodes.ABS_Y],
    ecodes.EV_KEY: [ecodes.BTN_JOYSTICK, ecodes.BTN_TRIGGER]
}

deviceCapabilities = device.capabilities()
if ecodes.EV_ABS in deviceCapabilities:
    caps[ecodes.EV_ABS] += deviceCapabilities[ecodes.EV_ABS]

if ecodes.EV_KEY in deviceCapabilities:
    caps[ecodes.EV_KEY] = deviceCapabilities[ecodes.EV_KEY]

spoofDevice = evdev.uinput.UInput(events=caps,
                                  name=device.name + " PRO",
                                  vendor=device.info.vendor, 
                                  product=device.info.product,
                                  version=device.info.version)

print("Spoofing:", spoofDevice)
print("Mirroring events. Press Ctrl-C twice to exit.")

for event in device.read_loop():
    spoofDevice.write_event(event)
    spoofDevice.syn()
