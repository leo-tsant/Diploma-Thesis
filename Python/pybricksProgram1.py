from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.tools import wait
from usys import stdout

hub = PrimeHub()

leftWheel = Motor(Port.C)
rightWheel = Motor(Port.D)
distanceSensor = UltrasonicSensor(Port.F)

while True:
    if distanceSensor.distance() > 100:
        leftWheel.run(300)
        rightWheel.run(300)
        betweenDistance = distanceSensor.distance()
        stdout.write( 'Between Distance: ' + str(betweenDistance) + '\n')
        wait(100)
    else:
        endDistance = distanceSensor.distance()
        stdout.write('End Distance: ' + str(endDistance) + '\n')
        leftWheel.stop()
        rightWheel.stop()
        
        break  # Break out of the while loop
