from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.static import File
from twisted.internet import task
import sys
import os
import time
import json
import RPi.GPIO as GPIO
from bbq import *

sys.path.insert(0, os.getcwd() + "/max31855")
from max31855 import MAX31855, MAX31855Error


class MyTempSensor(TempSensor):
    def __init__(self):
        cs_pin = 24
        clock_pin = 11
        data_pin = 10
        units = "f"
        self.thermocouple = MAX31855(cs_pin, clock_pin, data_pin, units)
        self.currentTemp = 0
        self.previousCurrentTemp = 0
        self.ambientTemp = 0
        self.previousAmbientTemp = 0

    def getTemp(self):
        self.previousAmbientTemp = self.ambientTemp
        self.previousCurrentTemp = self.currentTemp
        try:
            self.ambientTemp = self.thermocouple.get_rj()
            self.currentTemp = self.thermocouple.get()
            self.thermocoupleStatus = "normal"
        except MAX31855Error as e:
            self.status = "" + e.value
            self.ambientTemp = self.previousAmbientTemp
            self.currentTemp = self.previousCurrentTemp
            return self.currentTemp

class MyFan(AirControl):
    def __init__(self):
        super(MyFan, self).__init__()
        GPIO.setmode(GPIO.BCM)
        self.pin = 18
        self.value = 0
        self.step = 5
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, 0)
        self.p = GPIO.PWM(self.pin, 50)
        self.p.start(0)
        self.value = 0

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value
        self.p.ChangeDutyCycle(value)

    def __del__(self):
        self.p.stop()
        GPIO.cleanup()

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.debug("starting up!")
myBBQ = BBQ()
tempSensor = MyTempSensor()
airControl = MyFan()
myBBQ.tempSensor = tempSensor
myBBQ.airControl = airControl
myBBQ.algorithm = LinearControl(myBBQ, airControl, tempSensor)
myBBQ.setMode(BBQ.MODES.MAINTAIN)
myBBQ.goal = 250

class BBQStatus(Resource):
    def render_GET(self, request):
        print("get BBQ called\n")
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        info = { "pit" : myBBQ.temp,
                 "goal" : myBBQ.goal,
                 "fan" : myBBQ.airValue,
                 "history" : list(myBBQ.history)}
        return json.dumps(info, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def render_PUT(self, request):
        print("I got a PUT!");
        jsonString = request.content.getvalue()
        decoded = json.loads(jsonString)
        goal = decoded[u'goal']
        print("goal: %d" % goal)
        myBBQ.goal = int(goal)
        request.setResponseCode(200)
        # FIXME: better response
        return ""


class BBQResource(Resource):
    def getChild(self, name, request):
        return BBQStatus()

root = File("static/html")
root.putChild("jq", File("jq"))
root.putChild("js", File("static/js"))
root.putChild("css", File("static/css"))
root.putChild("BBQ", BBQResource())

factory = Site(root)
reactor.listenTCP(8880, factory)

l = task.LoopingCall(myBBQ.runIteration)
l.start(1)

reactor.run()

#
# Editor modelines  -  https://www.wireshark.org/tools/modelines.html
#
# Local variables:
# c-basic-offset: 4
# indent-tabs-mode: nil
# End:
#
# vi: set shiftwidth=4 expandtab:
# :indentSize=4:noTabs=true:
#
