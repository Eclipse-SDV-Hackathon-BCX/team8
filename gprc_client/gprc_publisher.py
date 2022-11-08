from __future__ import print_function
from my_vehicle_model.proto.types_pb2 import Datapoint, DataEntry, View, Field
from google.protobuf.timestamp_pb2 import Timestamp
from my_vehicle_model.proto.val_pb2 import EntryUpdate, SetRequest, GetRequest, EntryRequest, SubscribeEntry, SubscribeRequest

from my_vehicle_model.proto.val_pb2_grpc import VALStub

import grpc
import json
import asyncio
import signal
import time


DEFAULT_CLOUD_CONNECTOR_ADDRESS = "10.52.204.181"
DEFAULT_CLOUD_CONNECTOR_PORT = "55555"


class GrpcClient:
    def __init__(self):
        """Initiate a connection

        Args:
            id (int): thread id
            name (str): thread name
            service_id (str): service id
            callback (function): userlevel callback for received messages
        """


        channel_options = [
            ("grpc.enable_retries", 1),
            ("grpc.keepalive_time_ms", 10000),
            ("grpc.keepalive_timeout_ms", 1000),
            ("grpc.keepalive_permit_without_calls", 1),
            ("grpc.http2.max_ping_strikes", 5),
            ("grpc.http2.max_pings_without_data", 0),
            # Fix to prevent the application from failing after a few hours
            ("grpc.enable_http_proxy", 0),
        ]

        channel = grpc.insecure_channel(
            DEFAULT_CLOUD_CONNECTOR_ADDRESS + ":" + DEFAULT_CLOUD_CONNECTOR_PORT,
            options=channel_options,
        )
        self._stub = VALStub(channel)

        self.command_stream = None

        self.subscriptions = list()
    
    async def set_data(self, datapoint_path, datatype, data):
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        timestamp = Timestamp(seconds=seconds, nanos=nanos)

        if datatype == "int32":
            datapoint = Datapoint(timestamp=timestamp, int32=data)
        else:
            datapoint = Datapoint(timestamp=timestamp, int32=data)
        data_entry = DataEntry(path=datapoint_path, value=datapoint)
        updates = [EntryUpdate(entry=data_entry, fields=[Field.FIELD_VALUE])]
        response = self._stub.Set(SetRequest(updates=updates))
        return response

    async def get_data(self, datapoint_path):
        response = self._stub.Get(
            GetRequest(entries=[EntryRequest(path=datapoint_path, view=View.VIEW_CURRENT_VALUE)]),
            # metadata=self.metadata,
        )
        return response
    
    async def subscribe(self, path):
        responses = self._stub.Subscribe(SubscribeRequest(entries=[SubscribeEntry(path=path, view=View.VIEW_ALL)]))
        
        for response in responses:
            print(response)
            await asyncio.sleep(1)


# async def main(grpc_client):
#     await grpc_client.subscribe("Vehicle.Chassis.Accelerator.PedalPosition")

    # while True:
    #     resp = await grpc_client.get_data("Vehicle.Chassis.Accelerator.PedalPosition")
    #     resp2 = await grpc_client.get_data("Vehicle.Chassis.SteeringWheel.Angle")
    #     resp3 = await grpc_client.get_data("Vehicle.Powertrain.Transmission.CurrentGear")

    #     if resp:
    #         print("pedal ", resp.entries[0].value.uint32)
    #     if resp2:
    #         print("angle ", resp2.entries[0].value.int32)
    #     if resp3:
    #         print(resp3)
    #     await asyncio.sleep(1)

async def publish_gear(grpc_client):
    
    
    resp = await grpc_client.set_data("Vehicle.Chassis.SteeringWheel.AngleAct", 11)

    print(resp)


grpc_client = GrpcClient()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(publish_gear(grpc_client))
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
