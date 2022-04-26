from time import sleep
from subprocess import call
import os
import picamera
from picamera import PiCamera

# import the necessary packages for face recognition
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2

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

def recognize_face():
	currentname = "Unknown"
	encodingsP = "encodings.pickle"

	print("[INFO] loading encodings + face detector...")
	data = pickle.loads(open(encodingsP, "rb").read())
	
	#print("Loading stream...")
	#vs = VideoStream(usePiCamera=True).start()
	#time.sleep(2.0)

	#start_time = datetime.now()
	
	#vs = cv2.VideoCapture('/home/raspberry/Desktop/video.h264')

	#while True:
	#ret, frame = vs.read()
	frame = cv2.imread('/home/raspberry/Desktop/visitor.jpg')
	frame = imutils.resize(frame, width=500)
	boxes = face_recognition.face_locations(frame)
	encodings = face_recognition.face_encodings(frame, boxes)

	for encoding in encodings:
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown"

		if True in matches:
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			name = max(counts, key=counts.get)

			if currentname != name:
				currentname = name
				break
	
	#vs.stop()
	#camera = PiCamera()
	#camera.start_preview()
	
	return currentname

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
			#filename = datetime.now().strftime("/home/raspberry/Desktop/%Y-%m-%d-%H-%M-%S.jpg")
			filename = "/home/raspberry/Desktop/visitor.jpg"
			camera.capture(filename)
			
			#dev = pb.devices[0]
			#push1 = pb.push_note("Alert!!", "Someone at yor doorstep!")
			visitor_name = recognize_face()
			print(visitor_name)
			with open(filename, "rb") as pic:
				file_data = pb.upload_file(pic, "visitor.jpg")
			if visitor_name == "Unknown":
				msg_text = "Someone is at your doorstep!"
			else:
				msg_text = visitor_name + " is at your doorstep"
			push = pb.push_file(**file_data, body=msg_text)
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
