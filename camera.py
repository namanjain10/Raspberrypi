# import the necessary packages
from picamera import PiCamera
import time
import datetime
import cv2
import requests
import RPi.GPIO as GPIO
from git import Repo
import threading


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


def send_to_phone(dat) :
	url = 'https://api.line.me/v2/bot/message/push'

	head = {"Authorization": "Bearer  hI/pVkQgmgafBcFa60RYqpny1+3MmyX0XBh86N48y2SwKCOQHG7Z9y3oqN1y1teRFy8u67rEmXGd+8HNbsAvi+HcTWasi/47Ew3qF4xwq/0RGXn9DpmWBi/aZaZaMuKFHbBnnnWgh2aiUVWPXAwqBQdB04t89/1O/w1cDnyilFU=", "Content-Type": "application/json"}

	files1 = {
		"to": "U458fcb6e751b210cac030aa491357587",
		"messages":[
			{
				"type": "text",
				"text": "Sent from RaspberryPi"
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


def take_photo():
	global time_till, start
	
	print "seconds", (datetime.datetime.now() - time_till).seconds, "start var ", start
	
	if (datetime.datetime.now() - time_till).seconds > 10 or start == 0:

		camera = PiCamera()

		print ("taking photo!!")
		start = 1
		dat = datetime.datetime.now().strftime('%s')
		camera.capture('/home/pi/Documents/Raspberrypi/image_%s.jpg' % dat)
		print('A photo has been captured')
		time_till = datetime.datetime.now()

		camera.close()
		
		git_push(dat)
		send_to_phone(dat)


exitFlag = 0

class myThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print "Starting " + self.name
		take_photo()
		# print_time(self.name, 5, self.counter)
		print "Exiting " + self.name


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
start = 0

time_till = datetime.datetime.now()

while True :
	inp = GPIO.input(4)
	inp1 = GPIO.input(14)

	if inp1 == 0 :
		GPIO.output(21, False)
		time_till = datetime.datetime.now()

	else :
		thread1 = myThread(i, "Thread-%s" % i, i)
		i += 1
		thread1.start()
		GPIO.output(21, True)

	if inp == 0 :
		GPIO.output(10, False)
		time_till = datetime.datetime.now()

	else :				
		thread1 = myThread(i, "Thread-%s" % i, i)
		i += 1
		thread1.start()
		GPIO.output(10, True)

	time.sleep(0.3)