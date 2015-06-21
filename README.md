# robosmoker
Robotic Smoking overlord

# Tips for Converting a Smoker to a RoboSmoker
## Sealing
To keep temperature under control, you need to have a good seal around the edges of the smoker.  I reccommend using [fireplace gasket](http://amzn.com/B002YGO1WG) (a fiberglass/carbon fiber rope) held in place with [high temperature silicone](http://amzn.com/B001GP3AE6).  The high temperatue silicone is usefull for plugging bolt holes, dampers, and seams.

## Fan
I think the hardest problem to solve was the high-temperature/low temperature junction that needs to happen for the fan.  I found that using a plumbing flange, pipe nipple, and PVC adapters work well.  I use a 2"x2" pipe nipple, which attenuates the heat nicely.

## Temperature Sensing
I use a [K type thermocouple](http://amzn.com/B00899A4LY) connected to an Adafruit [Thermocouple Amplifier](https://www.adafruit.com/products/269).  I drilled a little hole and put it just below the grates.  It might be better to place it slightly above (more at food level).  Or perhaps multiple.  If you want to use more than one thermouple, it might be best to use their 1-wire variant.
