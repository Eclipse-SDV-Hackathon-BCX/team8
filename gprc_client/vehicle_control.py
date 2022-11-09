from jetracer.nvidia_racecar import NvidiaRacecar
from grpc_client import GrpcClient
import asyncio

car = NvidiaRacecar()
car.throttle = 0.0
car.steering_offset = 0.0
car.steering = 0.0

def setThrottle(t):
    car.throttle = t / -100.0 # change rotation direction because of wrong wireing
    print("car.throttle", car.throttle)


def setSteering(s):
    car.steering = s / 45.0  
    print("car.steering", car.steering)

gear = 1.0 # -1.0 is reverse gear

def sub_callback(stream):
    global gear
    for item in stream:
        if item.updates[0].entry.path == "Vehicle.Chassis.Accelerator.PedalPositionAct":
            print("Vehicle.Chassis.Accelerator.PedalPositionAct", item.updates[0].entry.value.uint32)
            setThrottle( gear* float(item.updates[0].entry.value.uint32))
        elif item.updates[0].entry.path == "Vehicle.Chassis.SteeringWheel.AngleAct":
            print("Vehicle.Chassis.SteeringWheel.AngleAct", item.updates[0].entry.value.int32)
            setSteering( item.updates[0].entry.value.int32)
        elif item.updates[0].entry.path == "Vehicle.Powertrain.Transmission.SelectedGear":
            print("Vehicle.Powertrain.Transmission.SelectedGear", item.updates[0].entry.value.int32)
            if item.updates[0].entry.value.int32 < 0:
                gear = -1.0
            else:
                gear = 1.0;

def main(grpc_client):
    grpc_client.subscribe(["Vehicle.Chassis.Accelerator.PedalPositionAct","Vehicle.Chassis.SteeringWheel.AngleAct","Vehicle.Powertrain.Transmission.SelectedGear"],  sub_callback)



grpc_client = GrpcClient()
main(grpc_client)