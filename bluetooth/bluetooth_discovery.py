# pip3 install beacontools

import time

from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter, EddystoneUIDFrame

# configure name spaces from android app Beacon Simulator
# create 2 EddyStone UID beacons
BEACON_GOOD_NAMESPACE = "4eb8812131c370b10919"
BEACON_BAD_NAMESPACE  = "ccf23a2d7eb174a4786a"

RSSI_THRESHOLD = -65

state = "good"

def callback(bt_addr, rssi, packet, additional_info):
    global state
    #print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))
    print(additional_info["namespace"], rssi)
    if additional_info["namespace"] == BEACON_GOOD_NAMESPACE:
        if rssi > RSSI_THRESHOLD:
          state = "good"
    
    if state == "good":
        if additional_info["namespace"] == BEACON_BAD_NAMESPACE:
            if rssi > RSSI_THRESHOLD:
              state = "bad"
    
    print(state)

# scan for all TLM frames of beacons in the namespace "12345678901234678901"
scanner = BeaconScanner(callback,
    # remove the following line to see packets from all beacons
    #device_filter=EddystoneFilter(namespace="12345678901234678901"),
    packet_filter=EddystoneUIDFrame
)
scanner.start()
time.sleep(100)
scanner.stop()