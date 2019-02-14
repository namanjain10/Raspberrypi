from picamera import PiCamera
import time
import datetime
import cv2
import requests
import RPi.GPIO as GPIO
from git import Repo
import threading
import numpy as np

def git_push (dat) :
	repo_dir = '.'
	repo = Repo(".")
	file_list = [
		'/home/pi/Documents/Raspberrypi/image_%s.jpg' % dat
	]
	commit_message = 'push image_%s' % dat
	repo.index.add(file_list)
	repo.index.commit(message=commit_message)
	origin = repo.remote('origin')
	origin.push(repo.head)
	print "photo pushed to git" 


def send_to_phone(dat, message) :
	url = 'https://api.line.me/v2/bot/message/push'

	head = {"Authorization": "Bearer  hI/pVkQgmgafBcFa60RYqpny1+3MmyX0XBh86N48y2SwKCOQHG7Z9y3oqN1y1teRFy8u67rEmXGd+8HNbsAvi+HcTWasi/47Ew3qF4xwq/0RGXn9DpmWBi/aZaZaMuKFHbBnnnWgh2aiUVWPXAwqBQdB04t89/1O/w1cDnyilFU=", "Content-Type": "application/json"}

	files1 = {
		"to": "U458fcb6e751b210cac030aa491357587",
		"messages":[
			{
				"type": "text",
				"text": message
			},
			{
				"type": "image",
				"originalContentUrl": "https://namanjain10.github.io/Raspberrypi/image_%s.jpg" % dat,
				"previewImageUrl": "https://namanjain10.github.io/Raspberrypi/image_%s.jpg" % dat       	
			}
		]
	}
	r1 = requests.post( url, headers=head, json=files1 )
	print "photo sent to mobile"


def capture() :
	global cam_var
	print "starting camera"
	camera = PiCamera()
	cam_var = 1
	image = np.empty((640*480*3), dtype=np.uint8)
	camera.capture(image, 'bgr')
	image = image.reshape((640,480,3))
	camera.close()
	time_face = datetime.datetime.now()
	cam_var = 0
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(gray, 1.3, 5)
	return faces, image


def face_detected(faces, image, dat):
	print "faces detected"
	for (x,y,w,h) in faces:
		cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),1)
	cv2.imwrite('/home/pi/Documents/Raspberrypi/image_%s.jpg' % dat, image)
	# git_push(dat)
	# send_to_phone(dat, "Face Detected")


def take_photo_door():
	global time_door, start_door, face_cascade, cam_var, time_face
	
	if (datetime.datetime.now() - time_face).seconds > 1  and cam_var == 0 :		
		faces, image = capture()
		dat = datetime.datetime.now().strftime('%s')

		if len(faces) > 0 :
			face_detected(faces, image, dat)

		elif (datetime.datetime.now() - time_door).seconds >= 10 or start_door == 0:
			print "taking photo!!"
			start_door = 1
			dat = datetime.datetime.now().strftime('%s')
			cv2.imwrite('/home/pi/Documents/Raspberrypi/image_%s.jpg' % dat, image)
			print('A photo has been captured')
			time_door = datetime.datetime.now()
			# git_push(dat)
			# send_to_phone(dat, "Sent from RaspberryPi")


def take_photo_motion(last_motion):
	global time_motion, face_cascade, cam_var, time_face
	
	if (datetime.datetime.now() - time_face).seconds > 1  and cam_var == 0 :		
		faces, image = capture()
		dat = datetime.datetime.now().strftime('%s')

		if len(faces) > 0 :
			face_detected(faces, image, dat)

		elif (datetime.datetime.now() - time_motion).seconds > 3 or last_motion == 0:
			print "taking photo!!"
			cv2.imwrite('/home/pi/Documents/Raspberrypi/image_%s.jpg' % dat, image)
			print('A photo has been captured')
			time_motion = datetime.datetime.now()
			# git_push(dat)
			# send_to_phone(dat, "Sent from RaspberryPi")


class DoorThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		# print "Starting " + self.name
		take_photo_door()
		# print "Exiting " + self.name


class MotionThread (threading.Thread):
	def __init__(self, threadID, name, counter, last_motion):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
		self.last_motion = last_motion
	def run(self):
		# print "Starting " + self.name
		take_photo_motion(self.last_motion)
		# print "Exiting " + self.name


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)					# Magnet Sensor input Pin

GPIO.setup(10, GPIO.OUT)											# Magnet Sensor LED
GPIO.output(10, False)
face_cascade = cv2.CascadeClassifier('/home/pi/Documents/haarcascade_frontalface_default.xml') 

GPIO.setup(21, GPIO.OUT)											# Motion Sensor LED
GPIO.output(21, False)

GPIO.setup(14, GPIO.IN)												# Motion Sensor input pin

i = 0
start_door = 0
cam_var = 0

time_door = datetime.datetime.now()
time_motion = datetime.datetime.now()
time_face = datetime.datetime.now()
last_motion = 0

while True :
	inp = GPIO.input(4)				# door magnet sensor
	inp1 = GPIO.input(14)			# motion sensor 

	if inp1 == 1 and inp == 1 :
		GPIO.output(10, True)
		GPIO.output(21, True)
		door_thread = DoorThread(i, "Thread-%s" % i, i)
		i += 1
		door_thread.start()		

	elif inp1 == 1 and inp == 0 :
		GPIO.output(10, False)
		GPIO.output(21, True)
		motion_thread = MotionThread(i, "Thread-%s" % i, i, last_motion)
		i += 1
		motion_thread.start()
		time_door = datetime.datetime.now()
		start_door = 0		

	elif inp1 == 0 and inp == 1 :
		GPIO.output(21, False)
		GPIO.output(10, True)
		door_thread = DoorThread(i, "Thread-%s" % i, i)
		i += 1
		door_thread.start()		
		time_motion = datetime.datetime.now()

	else :
		GPIO.output(21, False)
		GPIO.output(10, False)
		time_motion = datetime.datetime.now()
		time_door = datetime.datetime.now()
		start_door = 0

	last_motion = inp1	
	time.sleep(0.5)