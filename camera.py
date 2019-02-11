# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import datetime
import cv2

import RPi.GPIO as GPIO

from git import Repo

def take_photo():
	global time_till, start
	print (datetime.datetime.now() - time_till).seconds
	if (datetime.datetime.now() - time_till).seconds > 2 or start == 0:
		start = 1
		dat = datetime.datetime.now().strftime('%s')
		camera.capture('/home/pi/Documents/Raspberrypi/image_%s.jpg' % dat)
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

		url = 'https://api.line.me/v2/bot/message/push'

		head = {"Authorization": "Bearer  hI/pVkQgmgafBcFa60RYqpny1+3MmyX0XBh86N48y2SwKCOQHG7Z9y3oqN1y1teRFy8u67rEmXGd+8HNbsAvi+HcTWasi/47Ew3qF4xwq/0RGXn9DpmWBi/aZaZaMuKFHbBnnnWgh2aiUVWPXAwqBQdB04t89/1O/w1cDnyilFU=", "Content-Type": "application/json"}

		files1 = {
			"to": "U458fcb6e751b210cac030aa491357587",
			"messages":[
				{
			"type": "image",
			"originalContentUrl": "https://namanjain10.github.io/Raspberrypi/image_%s.jpg" % dat,
			"previewImageUrl": "https://namanjain10.github.io/Raspberrypi/image_%s.jpg" % dat       	
				}
			]
		}

		r1 = requests.post(
			url,
			headers=head,
			data=files1
		)

		print (r1)
		print('A photo has been taken')
		time_till = datetime.datetime.now()

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(10, GPIO.OUT)
GPIO.output(10, False)
face_cascade = cv2.CascadeClassifier('/home/pi/Documents/haarcascade_frontalface_default.xml') 

i = 0
start = 0

time_till = datetime.datetime.now()

while True :
	inp = GPIO.input(4)
	if inp == 0 :
		GPIO.output(10, True)
		time_till = datetime.datetime.now()
		try :
			camera.close()
		except :
			pass

	else :
		try :
			camera = PiCamera()
			camera.start_preview()
		except :
			pass
		take_photo()
		GPIO.output(10, False)

	time.sleep(0.3)