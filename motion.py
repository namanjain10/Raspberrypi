from picamera import PiCamera
import time
import datetime
import cv2
import requests
import RPi.GPIO as GPIO

from git import Repo

def take_photo():
	global time_till, start
	print (datetime.datetime.now() - time_till).seconds
	if (datetime.datetime.now() - time_till).seconds > 10 or start == 0:
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
			json=files1
		)

		print('A photo has been taken')
		time_till = datetime.datetime.now()


GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.OUT)
GPIO.output(21, False)

GPIO.setup(14, GPIO.IN)

i = 0
start = 0

time_till = datetime.datetime.now()

while True :
	inp = GPIO.input(14)
	print inp

	if inp == 0 :
		GPIO.output(21, False)
		# time_till = datetime.datetime.now()
			

	else :
		
		# take_photo()
		GPIO.output(21, True)

	time.sleep(0.3)