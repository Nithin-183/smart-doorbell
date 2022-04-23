from pushbullet import Pushbullet
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.IN)
GPIO.setup(3,GPIO.OUT)
GPIO.output(3,0)
pb = Pushbullet("o.tAXhoWMOW1LVQpOyLYcdpEd36o8HmIn7")
print("Started")
while True:
    i=GPIO.input(11)
    if i==0:
       print("no intruder",i)
       GPIO.output(3,0)
       time.sleep(0.2)
    elif i==1:
       print ("intruder", i)
       dev = pb.get_device('HMD Global Nokia 6.1 Plus')
       GPIO.output(3,1)
       #push = dev.push_note("Alert!!", "A wild Sandra appeared")
       #break
       time.sleep(0.2)