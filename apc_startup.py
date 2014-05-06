#!/usr/bin/env python
#/home/pi/python_virtualenv/django-pi/bin/python
######################################################################################
## 					APC AC POWER CONTROL SYSTEM			                            ##
## ---------------------------------------------------------------------------------##
## Mehmet UGUR 05/05 2014                                                          ##
## Canakkale GTH                                                                    ##
## Revision History                                                                 ## 
## V1.00 - APC system                                                               ##
######################################################################################

# This program sets the initial outlet settings from sqlite3 db file after reboot or power on
# You must use the web interface program  to control or configure the APC device
# log into raspberry pi with apc/apc through http://ip of raspberry to run the apc program


import os
import sys
import time
from apc_5821A import *
import sqlite3 as lite
from collections import defaultdict
sys.path.append('/home/pi/projects/apcweb')
os.environ['DJANGO_SETTINGS_MODULE'] = 'apcweb.settings'
from apc.models import Config
max_delay_time=0
HIGH=0
LOW=1

def get_max_delay_time(delay_dict):
	global max_delay_time
	for delay_key in delay_dict.keys():
		
		if delay_key[1:7]=='MINUTE':
			duration=int(delay_key[-1:])*60
			if duration>=max_delay_time:
				max_delay_time=duration
		
		if delay_key[1:8]=='SECONDS':
			duration=int(delay_key[-2:])
			if duration>=max_delay_time:
				max_delay_time=duration
	return max_delay_time
	
		
def all_pins_state(*pin_list):
	all_pins_dict = defaultdict(list) #{0:LOW, :1:HIGH, 2:HIGH gibi}
	if not pin_list:
		for outlet in Config.objects.all():
			if outlet.state == 1:
				all_pins_dict[int(outlet.id)-1] = HIGH
			elif outlet.state == 0:
				all_pins_dict[int(outlet.id)-1] = LOW
			else:
				all_pins_dict[int(outlet.id)-1] = '*'
		return(all_pins_dict)
	else:
		for each in pin_list[0]:
			id_num=int(each)+1
			outlet_state = Config.objects.get(pk=id_num).state
			if outlet_state==1:
				all_pins_dict[each] = HIGH
			elif outlet_state == 0:
				all_pins_dict[each] = LOW
			else:
				all_pins_dict[each] = '*'
		return(all_pins_dict)
		

delay_on_dict = defaultdict(list)

outlet_list=Config.objects.all()
for outlet in outlet_list:
	if outlet.state==1:
		pwr_on_delay=outlet.pwr_on_delay
		delay_on_dict[pwr_on_delay].append(int(outlet.id)-1) #delay_on_dict{'SECONDS 15':[0,1], 'IMMEDIATE':[2,4]} gibi olacak


all_pins_init={0:LOW,1:LOW,2:LOW,3:LOW,4:LOW,5:LOW,6:LOW,7:LOW}

max_delay=get_max_delay_time(delay_on_dict)

for delay_key in sorted(delay_on_dict.keys()):
	if delay_key=='1NEVERON':
		pass
	elif delay_key=='2IMMEDIATE':
		immediate_pins=delay_on_dict['2IMMEDIATE']
		immediate_pins_dict=all_pins_state(immediate_pins)
		all_pins_init.update(immediate_pins_dict) #Iki dictionary update ediliyor.
		startupMode(all_pins_init, True)

delay_15,delay_30,delay_45,delay_1,delay_2,delay_5=True,True,True,True,True,True
start_time=time.time()
elapsed_time=0

while True:
	for delay_key in sorted(delay_on_dict.keys()):
		now=time.time()
		elapsed_time=now-start_time
		try:
			if 	delay_key=='3SECONDS15' and elapsed_time>=15 and delay_15==True:
				seconds15_pins=delay_on_dict['3SECONDS15']
				seconds15_pins_dict=all_pins_state(seconds15_pins)
				all_pins_init.update(seconds15_pins_dict) #Iki dictionary update ediliyor.
				startupMode(all_pins_init, True)
				delay_15=False
			if 	delay_key=='4SECONDS30' and elapsed_time>=30 and delay_30==True:
				seconds30_pins=delay_on_dict['4SECONDS30']
				seconds30_pins_dict=all_pins_state(seconds30_pins)
				all_pins_init.update(seconds30_pins_dict) #Iki dictionary update ediliyor.
				startupMode(all_pins_init, True)
				delay_30=False
			if 	delay_key=='5SECONDS45' and elapsed_time>=45 and delay_45==True:
				seconds45_pins=delay_on_dict['5SECONDS45']
				seconds45_pins_dict=all_pins_state(seconds45_pins)
				all_pins_init.update(seconds45_pins_dict) #Iki dictionary update ediliyor.
				startupMode(all_pins_init, True)
				delay_45=False
			if 	delay_key=='6MINUTE1' and elapsed_time>=60 and delay_1==True:
				minute1_pins=delay_on_dict['6MINUTE1']
				minute1_pins_dict=all_pins_state(minute1_pins)
				all_pins_init.update(minute1_pins_dict) #Iki dictionary update ediliyor.
				startupMode(all_pins_init, True)
				delay_1=False
				
			if 	delay_key=='7MINUTES2' and elapsed_time>=120 and delay_2==True:
				minutes2_pins=delay_on_dict['7MINUTES2']
				minutes2_pins_dict=all_pins_state(minutes2_pins)
				all_pins_init.update(minutes2_pins_dict) #Iki dictionary update ediliyor.
				startupMode(all_pins_init, True)
				delay_2=False
			if 	delay_key=='8MINUTES5' and elapsed_time>=360 and delay_5==True:
				minutes5_pins=delay_on_dict['8MINUTES5']
				minutes5_pins_dict=all_pins_state(minutes5_pins)
				all_pins_init.update(minutes5_pins_dict) #Iki dictionary update ediliyor.
				startupMode(all_pins_init, True)
				delay_5=False
		except ValueError:
			continue
	if elapsed_time>=max_delay+3:
		break