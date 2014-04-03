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
	
	# Donus tipi dictionary {0:HIGH, 1:HIGH ,,,} gibi
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
		

		while True:
			cache_tmp_action_name=cache.get('action_name')
			if cache_tmp_action_name=='2' or cache_tmp_action_name=='4':
				cache_tmp_all_pins=cache.get('all_pins_state')
				startupMode(cache_tmp_all_pins, True)
				self.save_db(cache_tmp_all_pins)
				cache.set('action_name','1')

			if cache_tmp_action_name=='3' and cache.get('don_immediate'):
				cache_tmp_all_pins=cache.get('all_pins_state')
				startupMode(cache_tmp_all_pins, True)
				self.save_db(cache_tmp_all_pins)
				cache.set('don_immediate',False)

			if cache_tmp_action_name=='3' and cache.get('max_time') and cache.get('don_immediate')==False:
				max_delay=cache.get('max_time')
				cache_tmp_delay_on_dict=cache.get('delay_on_dict')
				start_time=cache.get('start_time',0)

				elapsed_time=0
				while True:
					for delay_key in sorted(cache_tmp_delay_on_dict.keys()):
						now=time.time()
						elapsed_time=now-start_time
						try:
							if cache.get('don_seconds15') and elapsed_time>=15:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds15_pins_state'))
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins)
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds15_pins_state'))
								cache.set('temp_all_pins_state',cache_tmp_all_pins)
								cache.set('don_seconds15',False)

							if cache.get('don_seconds30') and elapsed_time>=30:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds30_pins_state'))
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins)
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds30_pins_state'))
								cache.set('temp_all_pins_state',cache_tmp_all_pins)
								cache.set('don_seconds30',False)

							if cache.get('don_seconds45') and elapsed_time>=45:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds45_pins_state'))
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins)
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds45_pins_state'))
								cache.set('temp_all_pins_state',cache_tmp_all_pins)
								cache.set('don_seconds45',False)
							
							if cache.get('don_minute1') and elapsed_time>=60:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('minute1_pins_state'))
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins)
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state')
								cache_tmp_all_pins.update(cache.get('minute1_pins_state'))
								cache.set('temp_all_pins_state',cache_tmp_all_pins)
								cache.set('don_minute1',False)
							
							if cache.get('don_minutes2') and elapsed_time>=120:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('minutes2_pins_state'))
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins)
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state')
								cache_tmp_all_pins.update(cache.get('minutes2_pins_state'))
								cache.set('temp_all_pins_state',cache_tmp_all_pins)
								cache.set('don_minutes2',False)

							if cache.get('don_minutes5') and elapsed_time>=300:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('minutes5_pins_state'))
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins)
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state')
								cache_tmp_all_pins.update(cache.get('minutes5_pins_state'))
								cache.set('temp_all_pins_state',cache_tmp_all_pins)
								cache.set('don_minutes5',False)



						except ValueError:
							continue
					if elapsed_time>=max_delay+3:
						break
				cache.set('max_time',0)			
				cache.set('action_name','1')

			if cache_tmp_action_name == '7': #Delayed Reboot 
				tmp_checked_pins=cache.get('checked_pins') #hemen off konumuna cekilecek outletler ve digerleri
				checked_pins_off=self.set_outlet(tmp_checked_pins,LOW)
				cache_tmp_all_pins=cache.get('all_pins_state')
				cache_tmp_all_pins.update(checked_pins_off)
				startupMode(cache_tmp_all_pins, True) #Secilen outletler OFF yapildi.
				self.save_db(cache_tmp_all_pins)
				cache.set('all_pins_state',cache_tmp_all_pins)
				#baslangic_all_pins=cache.get('all_pins_state') #Off sonrasi eski haline donecegi durum yani baslangic durumu


				max_delay=cache.get('max_time')
				cache_tmp_delay_on_reboot_dict=cache.get('delay_on_reboot_dict')
				start_time=cache.get('start_time',0)

				elapsed_time=0
				while True:
					for delay_reboot in sorted(cache_tmp_delay_on_reboot_dict.keys()):
						now=time.time()
						elapsed_time=now-start_time
						try:
							if cache.get('dor_seconds05') and elapsed_time>=5:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds05_pins_state')) #5 saniye doldu ON yap
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins) #Database e yaz
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state') #Pinlerin son durumunu gosteriyor
								cache.set('temp_all_pins_state',cache_tmp_all_pins.update(cache.get('seconds05_pins_state'))) #*OFF olanlar ON yapildi.
								cache.set('dor_seconds05',False)

							if cache.get('dor_seconds10') and elapsed_time>=10:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds10_pins_state')) #10 saniye doldu ON yap
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins) #Database e yaz
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state') #Pinlerin son durumunu gosteriyor
								cache.set('temp_all_pins_state',cache_tmp_all_pins.update(cache.get('seconds10_pins_state'))) #*OFF olanlar ON yapildi.
								cache.set('dor_seconds10',False)

							if cache.get('dor_seconds15') and elapsed_time>=15:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds15_pins_state')) #15 saniye doldu ON yap
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins) #Database e yaz
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state') #Pinlerin son durumunu gosteriyor
								cache.set('temp_all_pins_state',cache_tmp_all_pins.update(cache.get('seconds15_pins_state'))) #*OFF olanlar ON yapildi.
								cache.set('dor_seconds15',False)

							if cache.get('dor_seconds20') and elapsed_time>=20:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds20_pins_state')) #20 saniye doldu ON yap
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins) #Database e yaz
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state') #Pinlerin son durumunu gosteriyor
								cache.set('temp_all_pins_state',cache_tmp_all_pins.update(cache.get('seconds20_pins_state')))
								cache.set('dor_seconds20',False)

							if cache.get('dor_seconds30') and elapsed_time>=30:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds30_pins_state')) #30 saniye doldu ON yap
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins) #Database e yaz
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state') #Pinlerin son durumunu gosteriyor
								cache.set('temp_all_pins_state',cache_tmp_all_pins.update(cache.get('seconds30_pins_state')))
								cache.set('dor_seconds30',False)

							if cache.get('dor_seconds45') and elapsed_time>=45:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('seconds45_pins_state')) #45 saniye doldu ON yap
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins) #Database e yaz
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state') #Pinlerin son durumunu gosteriyor
								cache.set('temp_all_pins_state',cache_tmp_all_pins.update(cache.get('seconds45_pins_state')))
								cache.set('dor_seconds45',False)

							if cache.get('dor_minute1') and elapsed_time>=60:
								cache_tmp_all_pins=cache.get('all_pins_state')
								cache_tmp_all_pins.update(cache.get('minute1_pins_state')) #60 saniye doldu ON yap
								startupMode(cache_tmp_all_pins, True)
								self.save_db(cache_tmp_all_pins) #Database e yaz
								cache.set('all_pins_state',cache_tmp_all_pins)
								cache_tmp_all_pins=cache.get('temp_all_pins_state') #Pinlerin son durumunu gosteriyor
								cache.set('temp_all_pins_state',cache_tmp_all_pins.update(cache.get('minute1_pins_state')))
								#cache_tmp_all_pins.update(cache.get('minute1_pins_state')) #*OFF olanlar ON yapildi.
								cache.set('dor_minute1',False)

						except ValueError:
							continue
					if elapsed_time>=max_delay+3:
						break
				cache.set('max_time',0)			
				cache.set('action_name','1')

			time.sleep(0.2)
app = GPIO_Daemon()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

