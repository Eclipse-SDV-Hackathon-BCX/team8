from grpc_client import GrpcClient
import asyncio

def sub_callback(stream):
    for item in stream:
        print(item)

def main(grpc_client):
    grpc_client.subscribe("Vehicle.Driver.Identifier.Subject", sub_callback)

grpc_client = GrpcClient()
main(grpc_client=grpc_client)
