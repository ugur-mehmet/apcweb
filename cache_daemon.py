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
		#self.stdout_path = '/dev/null'
		self.stderr_path = '/dev/tty'
		#self.stderr_path = '/dev/null'
		#self.pidfile_path = os.path.dirname(os.path.abspath(__file__)) + 'gpio_daemon.pid'
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
		# elif on_off == '*OFF':
		# 	for key, value in outlet_dict.iteritems():
		# 		outlet_dict[key]='*OFF'
		# else:
		# 	for key, value in outlet_dict.iteritems():
		# 		outlet_dict[key]='*ON'
	
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
		cache_all_cur = {}
		cache_checked_cur = {}
		outlet_state_dict={}
		action_name=''
		#cache.clear()
		while True:
			update_checked_out = {}
			if cache.get('action_name') == '2' or cache.get('action_name') == '4': # Selected outlets will be on immediately
				cache_all_cur = cache.get('all_pins_state')  #{0:LOW, 1: HIGH, 7:LOW} gibi
				cache_checked_cur = cache.get('checked_outlets_state')  # Secilen outletlerin o anki durumu {1:HIGH, 3:LOW} gibi
				
				if cache.get('action_name') == '2':
					update_checked_out=self.set_outlet(cache_checked_cur,HIGH)
					
				else:
					update_checked_out=self.set_outlet(cache_checked_cur,LOW)
					
				cache_all_cur.update(update_checked_out)
				startupMode(cache_all_cur, True)
				self.save_db(cache_all_cur)
				#cache.clear()
				cache.set('outlet_state_dict',update_checked_out) #Donecek deger {1:HIGH, 3:HIGH} gibi
			
			#action_name='3' (Delayed On) Beginning 
			'''Oncelikle pwr_on_delay parametresine gore her bir outlet icin dictionary olustur.
				Ornek: {'Immmediate':[1,2], '15 Seconds':[0],}
					
				cache.set('delay_on_dict',delay_on_dict) '''
			if cache.get('action_name') == '3':
				devam15=devam30=devam45=devam1=devam2=devam5=True
				delay_on_pins_updated=cache.get('delay_all_pins_dict')
				
				cache_all_cur = cache.get('all_pins_state')
				start_time=cache.get('start_time')
				#seconds15_pins_state=cache.get(seconds15_pins_state)

				if cache.get('immediate_pins_state'): #IMMEDIATE pinler var ise hemen ON yap 
					cache_all_cur.update(cache.get('immediate_pins_state'))
					startupMode(cache_all_cur, True)
					self.save_db(cache_all_cur)
					delay_on_pins_updated.update(cache.get('immediate_pins_state'))
					cache.set('outlet_state_dict',delay_on_pins_updated) #IMMEDIATE pin ler ON yapildi bilgisini ver

				while True:
					now=time.time()
					elapsed_time=now-start_time
					

					if devam15==True and cache.get('seconds15_pins_state') and elapsed_time>=15:
						cache_all_cur.update(cache.get('seconds15_pins_state'))
						startupMode(cache_all_cur, True)
						self.save_db(cache_all_cur)
						delay_on_pins_updated.update(cache.get('seconds15_pins_state'))
						cache.set('outlet_state_dict',delay_on_pins_updated)
						devam15=False
						break
						


			time.sleep(0.2)



app = GPIO_Daemon()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
