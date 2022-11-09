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

async def sub_callback(stream):
    for item in stream:
        print(item)

async def main(grpc_client):
    asyncio.gather(grpc_client.subscribe("Vehicle.Chassis.SteeringWheel.AngleAct", sub_callback))

grpc_client = GrpcClient()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.create_task(main(grpc_client))
    loop.run_forever()
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
