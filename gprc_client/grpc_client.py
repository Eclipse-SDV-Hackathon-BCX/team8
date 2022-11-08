from my_vehicle_model.proto.types_pb2 import Datapoint, DataEntry, View
from google.protobuf.timestamp_pb2 import Timestamp
from my_vehicle_model.proto.val_pb2 import EntryUpdate, SetRequest, GetRequest, EntryRequest, SubscribeEntry, SubscribeRequest

from my_vehicle_model.proto.val_pb2_grpc import VALStub

import grpc
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
    
    def set_data(self, datapoint_path, data):
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        timestamp = Timestamp(seconds=seconds, nanos=nanos)
        response = self._stub.Set(SetRequest(updates=[EntryUpdate(entry=DataEntry(path=datapoint_path, value=Datapoint(timestamp=timestamp, uint32=data)))]))
        return response

    async def get_data(self, datapoint_path):
        response = await self._stub.Get(
            GetRequest(entries=[EntryRequest(path=datapoint_path, view=View.VIEW_CURRENT_VALUE)]),
            # metadata=self.metadata,
        )
        return response
    
    async def subscribe(self, path):
        responses = self._stub.Subscribe(SubscribeRequest(entries=[SubscribeEntry(path=path, view=View.VIEW_ALL)]))
        
        for response in responses:
            print(response)


async def main():
    grpc_client = GrpcClient()
    grpc_client.subscribe("Vehicle.Chassis.Accelerator.PedalPosition")

    set_resp = grpc_client.set_data("Vehicle.Chassis.Accelerator.PedalPosition", 42)

loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# LOOP = asyncio.get_event_loop()
# LOOP.add_signal_handler(signal.SIGTERM, LOOP.stop)
loop.run_until_complete(main())
loop.close()
