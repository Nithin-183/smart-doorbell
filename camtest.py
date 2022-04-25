from time import sleep
from subprocess import call
import os
import picamera
from picamera import PiCamera

camera = PiCamera()
camera.start_preview()

from pushbullet import Pushbullet
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import time
pb = Pushbullet("o.tAXhoWMOW1LVQpOyLYcdpEd36o8HmIn7")
detection = {'value': False, 'button_press_time': None, 'intruder_confirmation_time': None}
pushbullet = {'sent_time': None}

print("Started")
def button_callback(channel):
	if GPIO.input(16):
		detection['value'] = False
		print("Button was pushed!")
		GPIO.output(18,1)
		try:
			camera.stop_recording()
		except picamera.PiCameraNotRecording:
			print("Not recording")
		if not pushbullet['sent_time'] or (pushbullet['sent_time']+timedelta(minutes=2))<datetime.now():
			filename = datetime.now().strftime("/home/raspberry/Desktop/%Y-%m-%d-%H-%M-%S.jpg")
			camera.capture(filename)
			
			#dev = pb.devices[0]
			#push1 = pb.push_note("Alert!!", "Someone at yor doorstep!")
			with open(filename, "rb") as pic:
				file_data = pb.upload_file(pic, "visitor.jpg")
			push = pb.push_file(**file_data, body="Someone at your doorstep!")
			pushbullet['sent_time'] = datetime.now()
	elif not GPIO.input(16):
		detection['button_press_time'] = datetime.now()
		print("Button was released!")
		GPIO.output(18,0)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(18,GPIO.OUT)
GPIO.output(18,0)
GPIO.add_event_detect(16,GPIO.BOTH,callback=button_callback)

GPIO.setup(11,GPIO.IN)
GPIO.setup(3,GPIO.OUT)
GPIO.output(3,0)
print("Started")

def intruder_confirmation_delay():
	return not detection['intruder_confirmation_time'] or (detection['intruder_confirmation_time']+timedelta(minutes=2))<datetime.now()

def button_press_delay():
	return not detection['button_press_time'] or (detection['button_press_time']+timedelta(minutes=2))<datetime.now()

while True:
	i=GPIO.input(11)
	if detection['value']:
		if intruder_confirmation_delay() and button_press_delay():
			if (detection['time']+timedelta(seconds=10))<datetime.now():
				print("Intruder confirmed")
				detection['intruder_confirmation_time'] = datetime.now()
				camera.stop_recording()
				#dev = pb.devices[0]
				filename = "/home/raspberry/Desktop/video.h264"
				outname  = "/home/raspberry/Desktop/video.mp4"
				command = "MP4Box -add " + filename + " " + outname
				call([command], shell=True)
				with open(outname, "rb") as vid:
					file_data = pb.upload_file(vid, "intruder.mp4")
				push = pb.push_file(**file_data, body="Intruder detected!")
				detection['value'] = False
				os.remove(outname)
				#time.sleep(120)
				continue
	if i==0:
		print("no intruder",i)
		GPIO.output(3,0)
		time.sleep(0.2)
	elif i==1:
		if not detection['value']:
			detection.update({'value': True, 'time': datetime.now()})
			if intruder_confirmation_delay() and button_press_delay():
				camera.start_recording('/home/raspberry/Desktop/video.h264')
		GPIO.output(3,1)
		print ("intruder", i)
		time.sleep(0.2)

GPIO.cleanup()
