from __future__ import print_function
from my_vehicle_model.proto.types_pb2 import Datapoint, DataEntry, View, Field
from google.protobuf.timestamp_pb2 import Timestamp
from my_vehicle_model.proto.val_pb2 import EntryUpdate, SetRequest, GetRequest, EntryRequest, SubscribeEntry, SubscribeRequest

from my_vehicle_model.proto.val_pb2_grpc import VALStub

from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter, EddystoneUIDFrame


import grpc
import json
import asyncio
import signal
import time
import queue
import os

from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter, EddystoneUIDFrame

# configure name spaces from android app Beacon Simulator
# create 2 EddyStone UID beacons
BEACON_GOOD_NAMESPACE = "6e91a77068f83d7e586f"
BEACON_BAD_NAMESPACE  = "245067ce9125c778c24e"


state = "good"

DEFAULT_CLOUD_CONNECTOR_ADDRESS = os.environ['KUKSA_DATA_BROKER_ADDRESS']
DEFAULT_CLOUD_CONNECTOR_PORT = os.environ['KUKSA_DATA_BROKER_PORT']


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

        self.queue = queue.Queue()
    
    def set_data(self, datapoint_path, datatype, data):
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        timestamp = Timestamp(seconds=seconds, nanos=nanos)

        if datatype == "int32":
            datapoint = Datapoint(timestamp=timestamp, int32=data)
        elif datatype == "string":
            datapoint = Datapoint(timestamp=timestamp, string=data)
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
            yield response

grpc_client = GrpcClient()

def callback(bt_addr, rssi, packet, additional_info):
    global state
    global grpc_client
    #print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))
    print(additional_info["namespace"], rssi)
    if additional_info["namespace"] == BEACON_GOOD_NAMESPACE:
          if state == "bad":
              state = "good"
              print("state change", state)
              grpc_client.set_data("Vehicle.Driver.Identifier.Subject","string", state)
    
    if state == "good":
        if additional_info["namespace"] == BEACON_BAD_NAMESPACE:
                if state == "good":
                    state = "bad"
                    print("state change", state)
                    grpc_client.set_data("Vehicle.Driver.Identifier.Subject","string", state)

    


def main(grpc_client):
    # scan for all TLM frames of beacons in the namespace "12345678901234678901"
    scanner = BeaconScanner(callback,
    # remove the following line to see packets from all beacons
    #device_filter=EddystoneFilter(namespace="12345678901234678901"),
    packet_filter=EddystoneUIDFrame
    )
    scanner.start()

main(grpc_client)

#loop = asyncio.new_event_loop()
#asyncio.set_event_loop(loop)
#try:
#    loop.create_task(main(grpc_client))
#    loop.run_forever()
#finally:
#    loop.run_until_complete(loop.shutdown_asyncgens())
#    loop.close()
