import RPi.GPIO as GPIO

class Fan:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.pin = 18
        self.value = 0
        self.step = 5
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, 0)
        self.p = GPIO.PWM(self.pin, 50)
        self.p.start(0)

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value
        self.p.ChangeDutyCycle(value)

    def increase(self):
        value = self.value+self.step
        if value > 100:
            print "tried to increase beyond limit"
        else:
            self.setValue(value)

    def decrease(self):
        value = self.value - self.step
        if value < 0:
            print "tried to decrease beyond limit"
        else:
            self.setValue(value)

    def __del__(self):
        self.p.stop()
        GPIO.cleanup()

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
