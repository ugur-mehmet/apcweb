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
				cache.clear()
				cache.set('outlet_state_dict',self.set_outlet(cache_checked_cur,HIGH)) #Donecek deger {1:HIGH, 3:HIGH} gibi
			
			#action_name='3' (Delayed On) Beginning 
			'''Oncelikle pwr_on_delay parametresine gore her bir outlet icin dictionary olustur.
				Ornek: {'Immmediate':[1,2], '15 Seconds':[0],}
					
				cache.set('delay_on_dict',delay_on_dict) '''
			if cache.get('action_name') == '3': # State i ON olanlar gelmeyecek sadece OFF olanlari delay on a gore ON yap
				cache_all_cur = cache.get('all_pins_state')  #{0:LOW, 1: HIGH, 7:LOW} gibi
				delay_on_dict_cur=cache.get('delay_on_dict') #Formati {'IMMEDIATE':[0,1].'SECONDS15':[4,7]} gibi 0,1,4,7 OFF durumda geliyor.
				cache_checked_cur = cache.get('checked_outlets_state')  # Secilen outletlerin o anki durumu {1:HIGH, 3:LOW} gibi
				delay_on_pins_updated={}
				time.sleep(2)
				for delay_key in delay_on_dict_cur.keys():
					if delay_key=='IMMEDIATE':
						immediate_pins_state=defaultdict(list)
						for i in delay_on_dict_cur['IMMEDIATE']:
							immediate_pins_state[i]=HIGH
						#immediate_pins_state=self.set_outlet(delay_on_dict_cur['IMMEDIATE'],HIGH) #Immediate pinlarin hepsini HIGH yap
						cache_all_cur.update(immediate_pins_state) #Iki dictionary update ediliyor.
						startupMode(cache_all_cur, True)
						self.save_db(cache_all_cur)
						delay_on_pins_updated.update(immediate_pins_state)
							
						cache.set('outlet_state_dict',delay_on_pins_updated)
					
					if delay_key=='NEVERON':
						neveron_pins_state=defaultdict(list)
						for i in delay_on_dict_cur['NEVERON']:
							neveron_pins_state[i]=LOW
						#neveron_pins_state=self.set_outlet(delay_on_dict_cur['NEVERON'],LOW) #Never on pinlarin hepsini LOW yap
						cache_all_cur.update(neveron_pins_state) #Iki dictionary update ediliyor.
						startupMode(cache_all_cur, True)
						self.save_db(cache_all_cur)
						delay_on_pins_updated.update(neveron_pins_state)
						cache.set('outlet_state_dict',delay_on_pins_updated)
						
					if delay_key=='SECONDS15' or delay_key=='SECONDS30' or delay_key=='SECONDS45' or \
						delay_key=='MINUTE1' or delay_key=='MINUTES2' or delay_key=='MINUTES5':
						start_time=time.time()
						elapsed_time=0
						max_time=0
						delay_all_pins=[]
						if 	delay_key=='SECONDS15':
							delay_all_pins=delay_on_dict_cur['SECONDS15']+delay_all_pins
							max_time=15
						if 	delay_key=='SECONDS30':
							delay_all_pins=delay_on_dict_cur['SECONDS30']+delay_all_pins
							max_time=30
						if 	delay_key=='SECONDS45':
							delay_all_pins=delay_on_dict_cur['SECONDS45']+delay_all_pins
							max_time=45
						if 	delay_key=='MINUTE1':
							delay_all_pins=delay_on_dict_cur['MINUTE1']+delay_all_pins	
							max_time=60
						if 	delay_key=='MINUTES2':
							delay_all_pins=delay_on_dict_cur['MINUTES2']+delay_all_pins	
							max_time=120
						if 	delay_key=='MINUTES5':
							delay_all_pins=delay_on_dict_cur['MINUTES5']+delay_all_pins
							max_time=300	
						delay_all_pins_dict=defaultdict(list)
						for pin in delay_all_pins:
							delay_all_pins_dict[pin]='*OFF'
						delay_on_pins_updated.update(delay_all_pins_dict)
						#delay_all_pins_state=self.set_outlet(delay_all_pins,'*OFF')
						
						cache.set('outlet_state_dict',delay_on_pins_updated)
						devam15=devam30=devam45=devam1=devam2=devam5=True

						while True:
							now=time.time()
							elapsed_time=now-start_time

							if elapsed_time>=15 and devam15==True:
								seconds15_pins_state=defaultdict(list)
								for i in delay_on_dict_cur['SECONDS15']:
									seconds15_pins_state[i]=HIGH
								#seconds15_pins_state=self.set_outlet(delay_on_dict_cur['SECONDS15'],HIGH) #Seconds15 pinlarin hepsini HIGH yap
								cache_all_cur.update(seconds15_pins_state) #Iki dictionary update ediliyor.
								startupMode(cache_all_cur, True)
								self.save_db(cache_all_cur)
								delay_on_pins_updated.update(seconds15_pins_state)
								cache.set('outlet_state_dict',delay_on_pins_updated)
								devam15=False

							if elapsed_time>=30 and devam30==True:
								#seconds30_pins_state=self.set_outlet(delay_on_dict_cur['SECONDS30'],HIGH) #Seconds15 pinlarin hepsini HIGH yap
								seconds30_pins_state=defaultdict(list)
								for i in delay_on_dict_cur['SECONDS30']:
									seconds30_pins_state[i]=HIGH
								cache_all_cur.update(seconds30_pins_state) #Iki dictionary update ediliyor.
								startupMode(cache_all_cur, True)
								self.save_db(cache_all_cur)
								delay_on_pins_updated.update(seconds30_pins_state)
								cache.set('outlet_state_dict',delay_on_pins_updated)
								devam30=False

							if elapsed_time>=45 and devam45==True:
								#seconds45_pins_state=self.set_outlet(delay_on_dict_cur['SECONDS45'],HIGH) #Seconds15 pinlarin hepsini HIGH yap
								seconds45_pins_state=defaultdict(list)
								for i in delay_on_dict_cur['SECONDS45']:
									seconds45_pins_state[i]=HIGH
								cache_all_cur.update(seconds45_pins_state) #Iki dictionary update ediliyor.
								startupMode(cache_all_cur, True)
								self.save_db(cache_all_cur)
								delay_on_pins_updated.update(seconds45_pins_state)
								cache.set('outlet_state_dict',delay_on_pins_updated)
								devam45=False

							if elapsed_time>=60 and devam1==True:
								#minute1_pins_state=self.set_outlet(delay_on_dict_cur['MINUTE1'],HIGH) #Seconds15 pinlarin hepsini HIGH yap
								minute1_pins_state=defaultdict(list)
								for i in delay_on_dict_cur['MINUTE1']:
									minute1_pins_state[i]=HIGH
								cache_all_cur.update(minute1_pins_state) #Iki dictionary update ediliyor.
								startupMode(cache_all_cur, True)
								self.save_db(cache_all_cur)
								delay_on_pins_updated.update(minute1_pins_state)
								cache.set('outlet_state_dict',delay_on_pins_updated)
								devam1=False
							
							if elapsed_time>=120 and devam2==True:
								#minutes2_pins_state=self.set_outlet(delay_on_dict_cur['MINUTES2'],HIGH) #Seconds15 pinlarin hepsini HIGH yap
								minutes2_pins_state=defaultdict(list)
								for i in delay_on_dict_cur['MINUTES2']:
									minutes2_pins_state[i]=HIGH
								cache_all_cur.update(minutes2_pins_state) #Iki dictionary update ediliyor.
								startupMode(cache_all_cur, True)
								self.save_db(cache_all_cur)
								delay_on_pins_updated.update(minutes2_pins_state)
								cache.set('outlet_state_dict',delay_on_pins_updated)
								devam2=False	
							if elapsed_time>=300 and devam5==True:
								minutes5_pins_state=defaultdict(list)
								for i in delay_on_dict_cur['MINUTES5']:
									minutes5_pins_state[i]=HIGH
								#minutes5_pins_state=self.set_outlet(delay_on_dict_cur['MINUTES5'],HIGH) #Seconds15 pinlarin hepsini HIGH yap
								cache_all_cur.update(minutes5_pins_state) #Iki dictionary update ediliyor.
								startupMode(cache_all_cur, True)
								self.save_db(cache_all_cur)
								delay_on_pins_updated.update(minutes5_pins_state)
								cache.set('outlet_state_dict',delay_on_pins_updated)
								devam5=False
							if 	elapsed_time>=max_time+2:
								break
			#action_name='3' (Delayed On) End 					
													
				
			time.sleep(0.2)



app = GPIO_Daemon()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
