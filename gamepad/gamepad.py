# pip3 install evdev

from evdev import InputDevice, categorize, ecodes, KeyEvent
from gprc_client.grpc_client import GrpcClient

gamepad = InputDevice("/dev/input/by-id/usb-ShanWan_USB_WirelessGamepad-event-joystick")
grpc_client = GrpcClient()
print(gamepad)

for event in gamepad.read_loop():
    #print(event)
    if event.type == ecodes.EV_KEY:
        keyevent = categorize(event)
        if keyevent.keystate == KeyEvent.key_down:
            if keyevent.scancode == 305:
                print('Button B')
            elif keyevent.scancode == 304:
                print ('Button A')
            elif keyevent.scancode == 307:
                print ('Button X')
            elif keyevent.scancode == 308:
                print ('Button Y')

    #print("event.code", event.code, event.value)
    # code 2: right thumb stick 
    if event.code == 2:
        # right stick left<->right
        # analog 0 .. 255
        steering_raw = event.value
        # [-45.0,45.0]
        steering = float(steering_raw - 127) / 127 * 45.0
        grpc_client.set_data("Vehicle.Chassis.SteeringWheel.Angle", datatype="int32" , data=int(steering))
        print("steering", steering)
        
      # code 1: right thumb stick   
    if event.code == 1:
        # left stick
        # analog 0 .. 255, 127 -> neutral
        throttle_raw = event.value
        throttle = float(throttle_raw - 127) / 127 * - 100.0
        # [ -100 .. 0 .. 100]
        grpc_client.set_data("Vehicle.Chassis.Accelerator.PedalPosition ", datatype="uint32", data=int(throttle))
        if throttle == 0:
            grpc_client.set_data("Vehicle.Powertrain.Transmission.CurrentGear", datatype="int32" , data=0)
        elif throttle > 0:
            grpc_client.set_data("Vehicle.Powertrain.Transmission.CurrentGear", datatype="int32" , data=1)
        elif throttle < 0:
            grpc_client.set_data("Vehicle.Powertrain.Transmission.CurrentGear", datatype="int32" , data=-1)
        print("throttle", throttle)
