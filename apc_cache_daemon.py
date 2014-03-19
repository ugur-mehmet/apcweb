import os
import time

from daemon import runner
import RPi.GPIO as GPIO

os.environ['DJANGO_SETTINGS_MODULE'] = 'apcweb.settings'
from django.core.cache import cache
from apc_5821A import *
import sqlite3 as lite

	
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
		else:
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
		cache_all_cur = {}
		cache_checked_cur = {}
		outlet_state_dict={}
		
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
				cache.set('outlet_state_dict',self.set_outlet(cache_checked_cur,HIGH)) #Donecek deger {1:HIGH, 3:HIGH} gibi
			'''Oncelikle pwr_on_delay parametresine gore her bir outlet icin dictionary olustur.
				Ornek: {'Immmediate':[1,2], '15 Seconds':[0],}
					
				cache.set('delay_on_dict',delay_on_dict) '''

			if cache.get('action_name') == '3': # State i ON olanlar gelmeyecek sadece OFF olanlari delay on a gore ON yap
				cache_all_cur = cache.get('all_pins_state')  #{0:LOW, 1: HIGH, 7:LOW} gibi
				delay_on_dict_cur=cache.get('delay_on_dict') #Formati {'IMMEDIATE':[0,1].'SECONDS15':[4,7]} gibi 0,1,4,7 OFF durumda geliyor.
				cache_checked_cur = cache.get('checked_outlets_state')  # Secilen outletlerin o anki durumu {1:HIGH, 3:LOW} gibi
				
				for delay_key in delay_on_dict_cur.keys():
					if delay_key=='IMMEDIATE':
						immediate_pins_state=self.set_outlet(delay_on_dict_cur['IMMEDIATE'],HIGH) #Immediate pinlarin hepsini HIGH yap
						cache_all_cur.update(immediate_pins_state) #Iki dictionary update ediliyor.
						startupMode(cache_all_cur, True)
						self.save_db(cache_all_cur)
						cache.set('outlet_state_dict',immediate_pins_state)
					if delay_key=='NEVERON':
						neveron_pins_state=self.set_outlet(cache_checked_cur,LOW) #Never on pinlarin hepsini LOW yap
						cache_all_cur.update(neveron_pins_state) #Iki dictionary update ediliyor.
						startupMode(cache_all_cur, True)
						self.save_db(cache_all_cur)
						cache.set('outlet_state_dict',self.set_outlet(cache_checked_cur,LOW))
					if delay_key=='SECONDS15' or delay_key=='SECONDS30' or delay_key=='SECONDS45' or \
						delay_key=='MINUTE1' or delay_key=='MINUTES2' or delay_key=='MINUTES5':
						start_time=time.time()
						elapsed_time=0
						while True:
							now=time.time()
							elapsed_time=now-start_time
							if elapsed_time>=15:
								seconds15_pins_state=self.set_outlet(delay_on_dict_cur['SECONDS15'],HIGH) #Seconds15 pinlarin hepsini HIGH yap
								cache_all_cur.update(seconds15_pins_state) #Iki dictionary update ediliyor.
								startupMode(cache_all_cur, True)
								self.save_db(cache_all_cur)
								cache.set('outlet_state_dict',self.set_outlet(,HIGH))
							if elapsed_time>=30:
								seconds30_pins_state=self.set_outlet(delay_on_dict_cur['SECONDS30'],HIGH) #Seconds30 pinlarin hepsini HIGH yap
								cache_all_cur.update(seconds30_pins_state) #Iki dictionary update ediliyor.
								startupMode(cache_all_cur, True)
								self.save_db(cache_all_cur)
								cache.set('outlet_state_dict',self.set_outlet(cache_checked_cur,HIGH))
								
								
								
								
								
							
							
							
						
						
						
		startupMode1(all_pins_init, True)
	elif delay_key=='Never On':
		never_pins=state(delay_pins_dict['Never On'])
		'''for pin in delay_pins_dict['Never On']: #Bu pinleri OFF a cek
			digitalWrite(pin,LOW)'''
		all_pins_init.update(never_pins)
		startupMode1(all_pins_init, True)
				



				


				
				
			
			time.sleep(1)



app = GPIO_Daemon()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
