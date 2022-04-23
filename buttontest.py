from pushbullet import Pushbullet
import RPi.GPIO as GPIO
import time
pb = Pushbullet("o.tAXhoWMOW1LVQpOyLYcdpEd36o8HmIn7")

print("Started")
def button_callback(channel):
	if GPIO.input(16):
		print("Button was pushed!")
		dev = pb.get_device('HMD Global Nokia 6.1 Plus')
		#push = dev.push_note("Alert!!", "Ahhh. Push it!!!!")
		GPIO.output(18,1)
		#time.sleep(60)
	elif not GPIO.input(16):
		print("Button was released!")
		GPIO.output(18,0)


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(18,GPIO.OUT)
GPIO.output(18,0)
GPIO.add_event_detect(16,GPIO.BOTH,callback=button_callback)
message = input("Press enter to quit\n\n")
GPIO.cleanup()