from jetracer.nvidia_racecar import NvidiaRacecar

import time


car = NvidiaRacecar()
car.throttle = 0.0
car.steering_offset = 0.0
car.steering = 0.0


def setThrottle(t):
    car.throttle = t / 100.0


def setSteering(s):
    car.steering = s / 45.0  
  
def doHappyAction():
    car.throttle = 0.0
    time.sleep(0.2)
    setSteering(45)
    time.sleep(0.5)
    setSteering(-45)
    time.sleep(0.5)
    setSteering(0)
    time.sleep(0.5)
    
doHappyAction()