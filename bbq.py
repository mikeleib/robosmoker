from abc import ABCMeta, abstractmethod
from enum import Enum
import datetime
import logging
import collections

bbq_logger = logging.getLogger('bbq')

class TempSensor():
    __metaclass__ = ABCMeta

    class TempSensorError(Exception):
        """Base class for tempature sensor exceptions"""
        pass

    class TempLowException(TempSensorError):
        """Exception thrown if tempature is too low to measure"""
        def __init__(self, expr, msg):
            self.expr = expr
            self.msg = msg

    class TempHighException(TempSensorError):
        """Exception thrown if temperature is too high to measure"""
        def __init__(self, expr, msg):
            self.expr = expr
            self.msg = msg

    @abstractmethod
    def getTemp(self):
        pass


class AirControl():
    __metaclass__ = ABCMeta
    minimum = 0
    maximum = 100
    step = 5

    @abstractmethod
    def getValue(self):
        pass

    @abstractmethod
    def setValue(self, value):
        pass

    def increase(self):
        value = self.getValue()
        newValue = min(self.maximum, value + self.step)
        self.setValue(newValue)

    def decrease(self):
        value = self.getValue()
        newValue = max(self.minimum, value - self.step)
        self.setValue(newValue)

class ControlAlgorithm():
    """Base class for defining a control algorithm.  Control algorithms
       have one input (a tempSensor) and one output"""
    __metaclass__ = ABCMeta

    class ControlAlgorithmException(Exception):
        pass

    class RunAway(ControlAlgorithmException):
        pass

    def __init__(self, bbq, airControl, tempSensor):
        self.goalTemp = None
        self.overflowThreshold = 25
        self.overflowStart = None
        self.underflowThreshold = 25
        self.underflowStart = None
        self.overunderflowTimeThreshold = 60*5

        self.bbq= bbq
        self.airControl = airControl
        self.tempSensor = tempSensor

    def log(self):
        bbq_logger.info("goal: %d temp: %d damper: %d" %
                        (self.goalTemp,
                         self.bbq.temp,
                         self.bbq.airValue))


    def runIteration(self):
        self.log()
        self.doIteration()

    @abstractmethod
    def doIteration(self):
        pass

class LinearControl(ControlAlgorithm):
    deadband = 5

    def __init__(self, bbq, airControl, tempSensor):
        super(LinearControl, self).__init__(bbq, airControl, tempSensor)

    def doIteration(self):
        temp = self.bbq.temp
        airValue = self.bbq.airValue
        if (self.goalTemp - self.deadband) > temp:
            self.airControl.increase()
        elif (self.goalTemp - self.deadband) < temp:
            self.airControl.setValue(0)



class BBQ:
    class MODES(Enum):
        IDLE = 0
        STOKE = 1
        MAINTAIN = 2
        LIDOPEN = 3
        BURNOFF = 4

    STOKE_TIME = 3

    def __init__(self):
        self.tempSensor = None
        self.airControl = None
        self.algorithm = None
        self.mode = self.MODES.IDLE
        self.modeStartTime = datetime.datetime.now()
        self.goal = None
        self.temp = None
        self.tempQueue = collections.deque([], maxlen = 60)
        self.history = collections.deque([])
        self.historyLastTime = datetime.datetime.now()

    def setMode(self, mode):
        if mode != self.mode:
            bbq_logger.info("mode: %s -> %s" % (self.mode, mode))
            self.mode = mode
            self.modeStartTime = datetime.datetime.now()

    def updateHistory(self):
        now =  datetime.datetime.now()
        # if we've done this in the last minute, then don't do it
        if (now - self.historyLastTime).seconds < 60:
            return
            self.historyLastTime = now
            lastTemps = map(lambda x: x[0], self.tempQueue)
            minuteAverage = sum(lastTemps)/len(lastTemps)
            bbq_logger.info("updating history with avg temp of %d" % minuteAverage)
            self.history.append({ "pit" : self.temp,
                                  "goal" : self.goal,
                                  "airValue" : self.airValue,
                                  "time" : now.isoformat()})

    def runIteration(self):
        mode = self.mode
        timeSinceMode = (datetime.datetime.now() - self.modeStartTime).total_seconds()
        nextMode = mode

        #FIXME: handle exceptions from getting temp
        self.temp = self.tempSensor.getTemp()
        self.airValue = self.airControl.getValue()
        self.tempQueue.append((self.temp, datetime.datetime.now()))
        self.updateHistory()
        bbq_logger.debug("tick timeSinceMode=%d mode=%s" % (timeSinceMode, str(mode)))
        if mode == self.MODES.IDLE:
            # nop
            nextMode = self.MODES.IDLE
        elif mode == self.MODES.STOKE:
            self.airControl.setValue(100)
            if timeSinceMode > self.STOKE_TIME:
                nextMode = self.MODES.MAINTAIN
            elif mode == self.MODES.MAINTAIN:
                self.algorithm.goalTemp = self.goal
                self.algorithm.runIteration()
                nextMode = self.MODES.MAINTAIN
            else:
                bbq_logger.warning("unhandled state: %s" % (str(mode)))
                self.setMode(nextMode)

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
