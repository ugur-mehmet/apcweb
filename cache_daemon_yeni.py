import os
import time
from daemon import runner
import RPi.GPIO as GPIO
os.environ['DJANGO_SETTINGS_MODULE'] = 'apcweb.settings'
from django.core.cache import cache
from apc_5821A import *
import sqlite3 as lite
from collections import defaultdict

	# 		"1" 'No Action'
	#       "2" 'Immediate On'		DONE
	#       "3" 'Delayed On'
	#       "4" 'Immediate Off'		DONE
	#       "5" 'Delayed Off'
	#       "6" 'Immediate Reboot'
	#       "7" 'Delayed Reboot'
	#       "8" 'Cancel Pending Commands'
	
class GPIO_Daemon():
	
	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/tty'
		self.stderr_path = '/dev/tty'
		self.pidfile_path = '/run/apc_gpio_daemon.pid'
		self.pidfile_timeout = 5
	
	# Donus dictionary {0:HIGH, 1:HIGH ,,,} gibi
	def set_outlet(self,outlet_dict, on_off):
		if on_off == HIGH:
			for key, value in outlet_dict.iteritems():
				outlet_dict[key]=HIGH
			return outlet_dict
		if on_off == LOW:
			for key, value in outlet_dict.iteritems():
				outlet_dict[key]=LOW
			return outlet_dict
	
	def save_db(self,outlet_state_dict):
		con = lite.connect('/home/pi/projects/apcweb/db.sqlite3')

		with con:

			cur = con.cursor()    
			for key,value in outlet_state_dict.iteritems(): # {0:HIGH, 1:LOW, 2: LOW ... 7:LOW} gibi
				if value==HIGH:
					cur.execute("UPDATE apc_config SET state=? WHERE Id=?", (True,int(key)+1))        
					con.commit()
				if value==LOW:
					cur.execute("UPDATE apc_config SET state=? WHERE Id=?", (False,int(key)+1))  
					con.commit()
	
	def run(self):
		cache_tmp_action_name = ''
		cache_tmp_all_pins = {}
    	cache_tmp_delay_on_dict = {}
    	max_time=0

    	while True:
			cache_tmp_action_name=cache.get('action_name')
			if cache_tmp_action_name=='2' or cache_tmp_action_name=='4':
				cache_tmp_all_pins=cache.get('all_pins_state')
				startupMode(cache_tmp_all_pins, True)
				self.save_db(cache_tmp_all_pins)
				cache.set('action_name','1')

			if cache_tmp_action_name=='3' and cache.get('don_immediate',0):
				cache_tmp_all_pins=cache.get('all_pins_state')
				startupMode(cache_tmp_all_pins, True)
				self.save_db(cache_tmp_all_pins)
				cache.set('action_name','1')
				cache.set('don_immediate',False)

			if cache_tmp_action_name=='3' and cache.get('max_time'):
				max_delay=cache.get('max_time')
				cache_tmp_delay_on_dict=cache.get('delay_on_dict')
				start_time=cache.get('start_time',0)
				#delay_15=delay_30=delay_45=delay_1=delay_2=delay_5=True
				elapsed_time=0
				while True:
					for delay_key in cache_tmp_delay_on_dict:
						now=time.time()
						elapsed_time=now-start_time
						try:
							if cache.get('don_seconds15') and elapsed_time>=15:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds15_pins_state'))
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins)
								cache.set('temp_all_pins_state',cache.get('seconds15_pins_state'))
								cache.set('action_name','1')
								cache.set('don_seconds15',False)

							if cache.get('don_seconds30') and elapsed_time>=30:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds30_pins_state'))
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins)
								cache.set('temp_all_pins_state',cache.get('seconds30_pins_state'))
								cache.set('action_name','1')
								cache.set('don_seconds30',False) 


						except ValueError:
							continue
					if elapsed_time>=max_delay+3:
						break

			time.sleep(0.2)



app = GPIO_Daemon()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()


				



			
