from grpc_client import GrpcClient
import asyncio

async def sub_callback(stream):
    for item in stream:
        print(item)

async def main(grpc_client):
    # asyncio.gather(grpc_client.subscribe("Vehicle.Chassis.Accelerator.PedalPosition", sub_callback))
    await grpc_client.subscribe("Vehicle.Chassis.SteeringWheel.AngleAct", sub_callback)
    # await grpc_client.set_data("Vehicle.Chassis.SteeringWheel.AngleAct", datatype="int32" , data=11)

    # while True:
    #     resp = await grpc_client.get_data("Vehicle.Chassis.Accelerator.PedalPositionAct")
    #     resp2 = await grpc_client.get_data("Vehicle.Chassis.SteeringWheel.AngleAct")
    #     resp3 = await grpc_client.get_data("Vehicle.Powertrain.Transmission.CurrentGear")

    #     if resp:
    #         print("setThrottle", resp.entries[0].value.uint32)
    #         setThrottle(resp.entries[0].value.uint32)
            
    #     if resp2:
    #         print("setSteering", resp2.entries[0].value.int32)
    #         setSteering(resp2.entries[0].value.int32)
    #     #if resp3:
    #     #    print("CurrentGear", resp3)
    #     await asyncio.sleep(0.1)

grpc_client = GrpcClient()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.create_task(main(grpc_client))
    loop.run_forever()
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
