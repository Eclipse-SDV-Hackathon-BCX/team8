from grpc_client import GrpcClient
import asyncio

def sub_callback(stream):
    for item in stream:
        print(item.updates[0].entry.value.uint32)

def main(grpc_client):
    # grpc_client.subscribe(["Vehicle.Chassis.Accelerator.PedalPositionAct"], sub_callback)
    # grpc_client.set_data("Vehicle.Chassis.SteeringWheel.AngleAct", "int32", -30)
    grpc_client.set_data("Vehicle.Chassis.Accelerator.PedalPosition ", datatype="uint32", data=30)

grpc_client = GrpcClient()
main(grpc_client=grpc_client)
