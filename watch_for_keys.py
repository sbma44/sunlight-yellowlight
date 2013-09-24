#!/home/pi/.virtualenvs/yellowlight/bin/python

import requests
import wiringpi
import time
import json
from settings import *

last_check = None
last_count = None

def on():
	wiringpi.digitalWrite(6, wiringpi.HIGH)

def off():
	wiringpi.digitalWrite(6, wiringpi.LOW)

def get_count():
	new_count = None
	try:
		r = requests.get('http://sunlightfoundation.com/api/analytics/data/keys/issued/yearly/?ignore_internal_keys=false', cookies=dict(sessionid=SESSION_ID))
		new_count = json.loads(r.text)
	except:
		pass
	
	if new_count is not None:
		target_year = new_count['latest_year']
		for y in new_count['yearly']:
			if y['year']==target_year:
				return y['issued']

	return None

def blink_once(delay=1):
	on()
	time.sleep(delay)
	off()
	time.sleep(delay)

def setup():
	wiringpi.wiringPiSetup()
        wiringpi.pinMode(6, wiringpi.OUTPUT)

def main():
	setup()

	last_count = None
	while last_count is None:
		print "Attempting to retrieve starting count..."
		last_count = get_count()
		time.sleep(1)

	print "Starting count is %d" % last_count

	for i in range(1, 4):
		for j in range(0, i):
			blink_once(delay=0.5)
		time.sleep(0.5)

	while True:
		new_count = get_count()
		if new_count is not None:
			print "retrieved current count: %d keys" % new_count

			delta = new_count - last_count
			for i in range(0, delta):
				blink_once()
			last_count = new_count
			last_check = time.time()

			time.sleep(max(0, 10 - (delta * 2)))
		else:
			time.sleep(10)

if __name__ == '__main__':
	main()
