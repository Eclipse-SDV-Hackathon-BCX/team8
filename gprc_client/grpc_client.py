from __future__ import print_function
from my_vehicle_model.proto.types_pb2 import Datapoint, DataEntry, View
from google.protobuf.timestamp_pb2 import Timestamp
from my_vehicle_model.proto.val_pb2 import EntryUpdate, SetRequest, GetRequest, EntryRequest, SubscribeEntry, SubscribeRequest

from my_vehicle_model.proto.val_pb2_grpc import VALStub

import grpc
import json
import asyncio
import signal
import time


from jetracer.nvidia_racecar import NvidiaRacecar

import time

car = NvidiaRacecar()
car.throttle = 0.0
car.steering_offset = 0.0
car.steering = 0.0

def setThrottle(t):
    car.throttle = t / 100.0
    print("car.throttle", car.throttle)


def setSteering(s):
    car.steering = s / 45.0  


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
    
    async def set_data(self, datapoint_path, data):
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        timestamp = Timestamp(seconds=seconds, nanos=nanos)
        response = self._stub.Set(SetRequest(updates=[EntryUpdate(entry=DataEntry(path=datapoint_path, value=Datapoint(timestamp=timestamp, uint32=data)))]))
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
            yield response


async def main(grpc_client):
    grpc_client.subscribe("Vehicle.Chassis.Accelerator.PedalPosition")

    

    while True:
        resp = await grpc_client.get_data("Vehicle.Chassis.Accelerator.PedalPositionAct")
        resp2 = await grpc_client.get_data("Vehicle.Chassis.SteeringWheel.AngleAct")
        resp3 = await grpc_client.get_data("Vehicle.Powertrain.Transmission.CurrentGear")

        if resp:
            print("setThrottle", resp.entries[0].value.uint32)
            setThrottle(resp.entries[0].value.uint32)
            
        if resp2:
            print("setSteering", resp2.entries[0].value.int32)
            setSteering(resp2.entries[0].value.int32)
        #if resp3:
        #    print("CurrentGear", resp3)
        await asyncio.sleep(0.1)

grpc_client = GrpcClient()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.create_task(main(grpc_client))
    loop.run_forever()
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
