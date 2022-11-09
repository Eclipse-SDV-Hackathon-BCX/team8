from my_vehicle_model.proto.types_pb2 import Datapoint, DataEntry, View, Field
from google.protobuf.timestamp_pb2 import Timestamp
from my_vehicle_model.proto.val_pb2 import EntryUpdate, SetRequest, GetRequest, EntryRequest, SubscribeEntry, SubscribeRequest

from my_vehicle_model.proto.val_pb2_grpc import VALStub

import grpc
import json
import asyncio
import signal
import time
import queue
import os


KUKSA_DATA_BROKER_ADDRESS = os.environ['KUKSA_DATA_BROKER_ADDRESS']
KUKSA_DATA_BROKER_PORT = os.environ['KUKSA_DATA_BROKER_PORT']

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
            KUKSA_DATA_BROKER_ADDRESS + ":" + KUKSA_DATA_BROKER_PORT,
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

    def get_data(self, datapoint_path):
        response = self._stub.Get(
            GetRequest(entries=[EntryRequest(path=datapoint_path, view=View.VIEW_CURRENT_VALUE)]),
            # metadata=self.metadata,
        )
        return response
    
    def subscribe(self, path, sub_callback):
        responses = self._stub.Subscribe(SubscribeRequest(entries=[SubscribeEntry(path=path, fields=[Field.FIELD_VALUE])]))
        
        sub_callback(responses)
