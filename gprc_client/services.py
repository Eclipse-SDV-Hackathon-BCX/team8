from sdv.model import Service

from my_vehicle_model.proto.types_pb2 import Datapoint, DataEntry, View
from google.protobuf.timestamp_pb2 import Timestamp
from my_vehicle_model.proto.val_pb2 import EntryUpdate, SetRequest, GetRequest, EntryRequest

from my_vehicle_model.proto.val_pb2_grpc import VALStub

import time


class PedalPositionService(Service):
    "SeatService model"

    def __init__(self):
        super().__init__()
        self._stub = VALStub(self.channel)

    def set_data(self, data):
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        timestamp = Timestamp(seconds=seconds, nanos=nanos)
        response = self._stub.Set(SetRequest(updates=[EntryUpdate(entry=DataEntry(path="Vehicle.Chassis.Accelerator.PedalPosition", value=Datapoint(timestamp=timestamp, uint32=data)))]))
        return response

    def get_data(self):
        response = self._stub.Get(
            GetRequest(entries=[EntryRequest(path="Vehicle.Chassis.Accelerator.PedalPosition", view=View.VIEW_CURRENT_VALUE)]),
            metadata=self.metadata,
        )
        return response
