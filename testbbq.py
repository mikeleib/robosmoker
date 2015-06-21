from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.static import File
from twisted.internet import task
import random
import json
import time
import sys
from bbq import *

class BogusTempSensor(TempSensor):
    def __init__(self):
        self.lastTemp = random.randint(50, 500)

    def getTemp(self):
        self.lastTemp += random.randint(-5,5)
        return self.lastTemp


class BogusAirControl(AirControl):
    value = 0

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value


logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.debug("starting up!")
myBBQ = BBQ()
tempSensor = BogusTempSensor()
airControl = BogusAirControl()
myBBQ.tempSensor = tempSensor
myBBQ.airControl = airControl
myBBQ.algorithm = LinearControl(myBBQ, airControl, tempSensor)
myBBQ.setMode(BBQ.MODES.STOKE)
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
