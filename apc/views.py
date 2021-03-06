from django.shortcuts import render, render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from apc.models import Config, Log, Parameter
from django.http import HttpResponse, HttpResponseRedirect
from apc.forms import ConfigForm
import json
from collections import defaultdict
from django.core.cache import cache
import time

HIGH = 0
LOW = 1
max_delay_time=0

@login_required
def index(request):

	outlet_list=Config.objects.all()
	c={'outlets':outlet_list}
	temperature=cache.get('temperature')
	reading_time=cache.get('reading_time')
	c['temperature'] = temperature
	c['reading_time'] = reading_time
	return render_to_response("status.html",c)

def login(request):
	if request.method=='POST':
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			if user.is_active:
				auth.login(request,user)
				request.session['kullanici_id']=user.id 
				response = redirect('status')
				return response

	c = {}
	c.update(csrf(request))
	return render_to_response("login.html",c)

@login_required
def logout(request):
	auth.logout(request)
	return redirect('login')

@login_required
def network(request):
	from ifconfig import ifconfig
	import subprocess
	from django.core.validators import validate_ipv46_address, RegexValidator
	from django.core.exceptions import ValidationError
	from apc.forms import NetForm
	from apc.network import interfaces
	c={}
	eth0=ifconfig('eth0')
	cmd_route="/sbin/ip route | awk \'/default/{print $3}\'"
	p_route=subprocess.Popen(cmd_route,stdout=subprocess.PIPE,shell=True)
	(gateway,err)=p_route.communicate()
	cmd_hostname="/bin/hostname"
	p_hostname=subprocess.Popen(cmd_hostname,stdout=subprocess.PIPE,shell=True)
	(hostname,err)=p_hostname.communicate()
	cmd_speed="dmesg|grep -i eth0:\\ link\\ up|cut -d\',\' -f2"
	cmd_speed_mode="dmesg|grep -i eth0:\\ link\\ up|cut -d\',\' -f3"
	speed_proc=subprocess.Popen(cmd_speed,stdout=subprocess.PIPE,shell=True)
	(speed,err)=speed_proc.communicate()
	speed_mode_proc=subprocess.Popen(cmd_speed_mode,stdout=subprocess.PIPE,shell=True)
	(speed_mode,err)=speed_mode_proc.communicate()
	c['gateway']=gateway[:-1]
	c['hostname']=hostname[:-1]
	c['ip']=eth0['addr']
	c['mask']=eth0['netmask']
	cmd_bootmode='cat /etc/network/interfaces |grep ^iface\\ eth0 | awk -F \' \' \'{print $4}\''
	proc_bootmode=subprocess.Popen(cmd_bootmode,stdout=subprocess.PIPE,shell=True)
	(bootmod,err)=proc_bootmode.communicate()
	if bootmod[:-1]=='static':
		bootmode='1'
	else:
		bootmode='2'

	if request.method == 'POST':
		form = NetForm(request.POST)
		
		if form.is_valid():
			net_dict={}
			net_dict['ipaddress']=form.cleaned_data.get('ipaddress')
			net_dict['subnetmask']=form.cleaned_data.get('subnetmask')
			net_dict['bootmode']=form.cleaned_data.get('bootmode')
			net_dict['gateway']=form.cleaned_data.get('gateway')
			net_dict['hostname']=form.cleaned_data.get('hostname')
			if (c['ip']==net_dict['ipaddress']) and (c['mask']==net_dict['subnetmask']) and \
			(c['gateway']==net_dict['gateway']) and (c['hostname']==net_dict['hostname']) and \
			(bootmode==net_dict['bootmode']):
				return redirect('/network/')
			else:
				network=interfaces()
				network.write_template(net_dict['bootmode'],**net_dict)
				return HttpResponse("The system is rebooting now to effect the changes, Please wait...")
	else:
		
		
		default_data = {'bootmode':'2','ipaddress': eth0['addr'], 'subnetmask': eth0['netmask'],'gateway':gateway[:-1], 'hostname':hostname[:-1]}
		form=NetForm(default_data,auto_id=True)

	

	
		#form=NetForm(auto_id=False)
	c['form'] = form
	c['bootmode']=bootmod[:-1]
	c['hwaddr']=eth0['hwaddr']
	if speed and speed_mode:
		c['speed']=speed
		c['speed_mode']=speed_mode
	else:
		c['speed']='Could not retrieved.'
		c['speed_mode']='...check interface card'

	#ip link show eth0 | awk '/ether/ {print $2}'
	c.update(csrf(request))
	return render_to_response("network.html",c)

def set_outlet(outlet_dict, on_off):
		if on_off == HIGH:
			for key, value in outlet_dict.iteritems():
				outlet_dict[key]=HIGH
			return outlet_dict
		elif on_off == LOW:
			for key, value in outlet_dict.iteritems():
				outlet_dict[key]=LOW
			return outlet_dict
		else:
			for key, value in outlet_dict.iteritems():
				outlet_dict[key]=on_off
			return outlet_dict
				
	
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
		for each in pin_list:
			id_num=int(each)+1
			outlet_state = Config.objects.get(pk=id_num).state
			if outlet_state==1:
				all_pins_dict[each] = HIGH
			elif outlet_state == 0:
				all_pins_dict[each] = LOW
			else:
				all_pins_dict[each] = '*'
		return(all_pins_dict)
			
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

	# 		"1" 'No Action'
	#       "2" 'Immediate On'		DONE
	#       "3" 'Delayed On'
	#       "4" 'Immediate Off'		DONE
	#       "5" 'Delayed Off'
	#       "6" 'Immediate Reboot'
	#       "7" 'Delayed Reboot'
	#       "8" 'Cancel Pending Commands'
@login_required
def control(request,**kwargs):
	global HIGH
	global LOW
	global max_delay_time
	HIGH=0
	LOW=1
	cache.set('go_on',True)

	if request.method == 'POST':
	
		check_list=['checkbox_1', 'checkbox_2','checkbox_3','checkbox_4',
					'checkbox_5','checkbox_6','checkbox_7','checkbox_8']

		outlet_ids = []
		outlet_pins = []
		checked_pins={}
		action_name=request.POST['action_list']
		cache.set('post_data',request.POST)
		for check in check_list:
			if check in request.POST:
				outlet_ids.append(int(check[-1])) 
				outlet_pins.append(int(check[-1])-1) #Convert checked_list from outlet id to pins [0,1,2 ..]
	
		if outlet_pins:
			checked_pins=all_pins_state(*outlet_pins)
			all_pins=all_pins_state()
			on_pins={}
			off_pins={}
			on_to_off_pins={}
			off_to_on_pins={}
		
			for pin,value in checked_pins.iteritems():
				if checked_pins[pin]==HIGH:
					on_pins[pin]=value
					on_to_off_pins[pin]=LOW
				else:
					off_pins[pin]=value
					off_to_on_pins[pin]=HIGH


		if action_name=='2' and off_pins: #Action=immediate on (OFF konumunda olan outletler ON yapilacak)
			all_pins.update(off_to_on_pins)
			cache.set('all_pins_state',all_pins)
			cache.set('action_name',action_name)
			cache.set('temp_all_pins_state',{})
		if action_name=='4' and on_pins: #Action=immediate off (ON konumunda olan outletler OFF yapilacak)
			all_pins.update(on_to_off_pins)
			cache.set('all_pins_state',all_pins)
			cache.set('action_name',action_name)
			cache.set('temp_all_pins_state',{})

		if action_name=='8':
			cache.set('action_name',1)
			cache.set('temp_all_pins_state',{})
			cache.set('go_on',False)

		if action_name=='6' and outlet_pins: #Immediate Reboot 
			cache.set('temp_all_pins_state',{})
		 	#delay_on_off_dict = defaultdict(list)
			#all_pins=all_pins_state()
			tmp_all_pins_state={}
			#cache.set('checked_pins',checked_pins)
			checked_pins_state=dict(checked_pins)
			checked_pins_off=set_outlet(checked_pins_state,LOW)
			checked_pins_state=dict(checked_pins)
			checked_pins_on=set_outlet(checked_pins_state,HIGH)
			checked_pins_state=dict(checked_pins)
			tmp_all_pins_state=set_outlet(checked_pins_state,'*OFF')
			start_time=time.time()
			cache.set('start_time',start_time)
			cache.set('action_name',action_name)
			cache.set('checked_pins_off',checked_pins_off)
			cache.set('checked_pins_on', checked_pins_on)
			cache.set('temp_all_pins_state',tmp_all_pins_state)
			cache.set('immediate_reboot',True)

		if action_name == '3' or action_name=='5':  #Delayed on ise Tum outletler icin pwr_on_delay degerlerini al
			'''Oncelikle pwr_on_delay parametresine gore her bir outlet icin dictionary olustur.
		 	Ornek: {'Immmediate':[1,2], '15 Seconds':[0],}
		 	Bu dictionary olusurken sadece off durumda olan outletler secilecek. On durumda olanlari
		 	pwr_on_delay yapmaya gerek yok.

		 	'''
		 	cache.set('temp_all_pins_state',{})
		 	delay_on_off_dict = defaultdict(list)
			all_pins=all_pins_state()
			tmp_all_pins_state={}
			
			if action_name=='3':
				column='pwr_on_delay'
				HIGH=0
				LOW=1
				tmp_state='*OFF'
			if action_name=='5':
				column='pwr_off_delay'
				HIGH=1
				LOW=0
				tmp_state='*ON'

			for id in outlet_ids:
				pwr_on_off_delay = getattr(Config.objects.get(pk=id),column)
				state = Config.objects.get(pk=id).state
				#HIGH=0 ise OFF konumunda olan pinler hesaba katilacak ve delay on parametresine gore ON olacak
				# HIGH=1 ise ON konumunda olan pinler hesaba katilacak ve delay off parametresine gore OFF olacak
				if state==HIGH: 
					delay_on_off_dict[pwr_on_off_delay].append(id-1)
						
			action_name='35'
			cache.set('delay_on_dict',delay_on_off_dict)
			for delay_key in sorted(delay_on_off_dict.keys()):
				if delay_key=='1NEVERON' or delay_key=='1NEVEROFF':
					pass
				elif delay_key=='2IMMEDIATE':
					immediate_pins_state=defaultdict(list)
					for i in delay_on_off_dict['2IMMEDIATE']:
						immediate_pins_state[i]=HIGH
					#immediate_pins_state=self.set_outlet(delay_on_dict_cur['IMMEDIATE'],HIGH) #Immediate pinlarin hepsini HIGH yap
					all_pins.update(immediate_pins_state)
					cache.set('all_pins_state',all_pins) #Iki dictionary update ediliyor.
					cache.set('don_immediate',True)	
					cache.set('action_name',action_name)
				
				else:
					
					start_time=time.time()
					max_delay_time=0
					max_time=get_max_delay_time(delay_on_off_dict)
					temp_pins_state=defaultdict(list)
					#temp_all_pins_state=dict(all_pins) #all_pins dicti copyala all_pins.copy() de calisiyor
					cache.set('max_time',max_time)
					cache.set('start_time',start_time)
					cache.set('action_name',action_name)

					if 	delay_key=='3SECONDS15':
						seconds15_pins_state=defaultdict(list)
						for i in delay_on_off_dict['3SECONDS15']:
							seconds15_pins_state[i]=HIGH
							temp_pins_state[i]=tmp_state
						
						tmp_all_pins_state.update(temp_pins_state)
						
						cache.set('temp_all_pins_state',tmp_all_pins_state)
						cache.set('don_seconds15',True)
						cache.set('seconds15_pins_state',seconds15_pins_state)
						cache.set('all_pins_state',all_pins)

					if 	delay_key=='4SECONDS30':
						seconds30_pins_state=defaultdict(list)
						for i in delay_on_off_dict['4SECONDS30']:
							seconds30_pins_state[i]=HIGH
							temp_pins_state[i]=tmp_state
						
						tmp_all_pins_state.update(temp_pins_state)
						cache.set('temp_all_pins_state',tmp_all_pins_state)
						cache.set('don_seconds30',True)
						cache.set('seconds30_pins_state',seconds30_pins_state)
						cache.set('all_pins_state',all_pins)
							
					if 	delay_key=='5SECONDS45':
						seconds45_pins_state=defaultdict(list)
						for i in delay_on_off_dict['5SECONDS45']:
							seconds45_pins_state[i]=HIGH
							temp_pins_state[i]=tmp_state
						
						tmp_all_pins_state.update(temp_pins_state)
						cache.set('temp_all_pins_state',tmp_all_pins_state)
						cache.set('don_seconds45',True)
						cache.set('seconds45_pins_state',seconds45_pins_state)
						cache.set('all_pins_state',all_pins)
						
					if 	delay_key=='6MINUTE1':
						minute1_pins_state=defaultdict(list)
						for i in delay_on_off_dict['6MINUTE1']:
							minute1_pins_state[i]=HIGH
							temp_pins_state[i]=tmp_state
						
						tmp_all_pins_state.update(temp_pins_state)
						cache.set('temp_all_pins_state',tmp_all_pins_state)
						cache.set('don_minute1',True)
						cache.set('minute1_pins_state',minute1_pins_state)
						cache.set('all_pins_state',all_pins)
						
					if 	delay_key=='7MINUTES2':
						minutes2_pins_state=defaultdict(list)
						for i in delay_on_off_dict['7MINUTES2']:
							minutes2_pins_state[i]=HIGH
							temp_pins_state[i]=tmp_state
						
						tmp_all_pins_state.update(temp_pins_state)
						cache.set('temp_all_pins_state',tmp_all_pins_state)
						cache.set('don_minutes2',True)
						cache.set('minutes2_pins_state',minutes2_pins_state)
						cache.set('all_pins_state',all_pins)
						
					if 	delay_key=='8MINUTES5':
						minutes5_pins_state=defaultdict(list)
						for i in delay_on_off_dict['8MINUTES5']:
							minutes5_pins_state[i]=HIGH
							temp_pins_state[i]=tmp_state
						
						tmp_all_pins_state.update(temp_pins_state)
						cache.set('temp_all_pins_state',tmp_all_pins_state)
						cache.set('don_minutes5',True)
						cache.set('minutes5_pins_state',minutes5_pins_state)
						cache.set('all_pins_state',all_pins)
									
		if action_name == '7' and outlet_ids: #'Delayed Reboot' reboot duration parametresine gore OFF ve ON yap
			# Secilen outletleri hemen off durumuna getirmek icin gerekli degiskenleri set et.
			all_pins=all_pins_state()
			tmp_all_pins=dict(all_pins)
			#tmp_all_pins_state=dict(all_pins)
			tmp_all_pins_state={}
			
			checked_pins_state=dict(checked_pins)
			checked_pins_off=set_outlet(checked_pins_state,LOW)
			cache.set('checked_pins_off',checked_pins_off)
			#tmp_all_pins.update(on_to_off_pins) #Secilen outletlerden on durumunda olanlari tum outletlerin o anki durumu ile birlestir. 
			temp_pins_state=defaultdict(list) #Gecici pin durumu *OFF veya *ON olacak
			#cache.set('tmp_all_pins',tmp_all_pins)
			cache.set('all_pins_state',all_pins)
			cache.set('action_name',action_name)
			

			delay_on_reboot_dict=defaultdict(list)
			'''Bu dictionary formati {'1SECONDS05':[1,2], '2SECONDS10':[0],} gibi olacak'''
			for id in outlet_ids:
				reboot_duration = Config.objects.get(pk=id).reboot_duration
				#state = Config.objects.get(pk=id).state
				delay_on_reboot_dict[reboot_duration].append(id-1) #(id-1) id den pin numarasina ceviriyor
			
			start_time=time.time()
			max_delay_time=0
			max_time=get_max_delay_time(delay_on_reboot_dict)
			
			cache.set('max_time',max_time)
			cache.set('start_time',start_time)
			cache.set('delay_on_reboot_dict',delay_on_reboot_dict)
			
			for delay_reboot in sorted(delay_on_reboot_dict.keys()):
				if 	delay_reboot=='1SECONDS05':
					seconds05_pins_state=defaultdict(list)
					for i in delay_on_reboot_dict['1SECONDS05']:
						seconds05_pins_state[i]=HIGH #5 saniye sonra HIGH olacak pinler
						temp_pins_state[i]='*OFF' #5 saniye dolana kadar bu pinler *OFF gozukecek
					tmp_all_pins_state.update(temp_pins_state)
					cache.set('temp_all_pins_state',tmp_all_pins_state) #Pinlerin son durumunu gosteriyor
					cache.set('seconds05_pins_state',seconds05_pins_state)
					cache.set('dor_seconds05',True)

				if 	delay_reboot=='2SECONDS10':
					seconds10_pins_state=defaultdict(list)
					for i in delay_on_reboot_dict['2SECONDS10']:
						seconds10_pins_state[i]=HIGH #10 saniye sonra HIGH olacak pinler
						temp_pins_state[i]='*OFF' #10 saniye dolana kadar bu pinler *OFF gozukecek
					tmp_all_pins_state.update(temp_pins_state)
					cache.set('temp_all_pins_state',tmp_all_pins_state) #Pinlerin son durumunu gosteriyor
					cache.set('seconds10_pins_state',seconds10_pins_state)
					cache.set('dor_seconds10',True)

				if 	delay_reboot=='3SECONDS15':
					seconds15_pins_state=defaultdict(list)
					for i in delay_on_reboot_dict['3SECONDS15']:
						seconds15_pins_state[i]=HIGH #15 saniye sonra HIGH olacak pinler
						temp_pins_state[i]='*OFF' #15 saniye dolana kadar bu pinler *OFF gozukecek
					tmp_all_pins_state.update(temp_pins_state)
					cache.set('temp_all_pins_state',tmp_all_pins_state) #Pinlerin son durumunu gosteriyor
					cache.set('seconds15_pins_state',seconds15_pins_state)
					cache.set('dor_seconds15',True)

				if 	delay_reboot=='4SECONDS20':
					seconds20_pins_state=defaultdict(list)
					for i in delay_on_reboot_dict['4SECONDS20']:
						seconds20_pins_state[i]=HIGH #20 saniye sonra HIGH olacak pinler
						temp_pins_state[i]='*OFF' #20 saniye dolana kadar bu pinler *OFF gozukecek
					tmp_all_pins_state.update(temp_pins_state)
					cache.set('temp_all_pins_state',tmp_all_pins_state) #Pinlerin son durumunu gosteriyor
					cache.set('seconds20_pins_state',seconds20_pins_state)
					cache.set('dor_seconds20',True)

				if 	delay_reboot=='5SECONDS30':
					seconds30_pins_state=defaultdict(list)
					for i in delay_on_reboot_dict['5SECONDS30']:
						seconds30_pins_state[i]=HIGH #30 saniye sonra HIGH olacak pinler
						temp_pins_state[i]='*OFF' #30 saniye dolana kadar bu pinler *OFF gozukecek
					tmp_all_pins_state.update(temp_pins_state)
					cache.set('temp_all_pins_state',tmp_all_pins_state) #Pinlerin son durumunu gosteriyor
					cache.set('seconds30_pins_state',seconds30_pins_state)
					cache.set('dor_seconds30',True)

				if 	delay_reboot=='6SECONDS45':
					seconds45_pins_state=defaultdict(list)
					for i in delay_on_reboot_dict['6SECONDS45']:
						seconds45_pins_state[i]=HIGH #45 saniye sonra HIGH olacak pinler
						temp_pins_state[i]='*OFF' #45 saniye dolana kadar bu pinler *OFF gozukecek
					tmp_all_pins_state.update(temp_pins_state)
					cache.set('temp_all_pins_state',tmp_all_pins_state) #Pinlerin son durumunu gosteriyor
					cache.set('seconds45_pins_state',seconds45_pins_state)
					cache.set('dor_seconds45',True)

				if 	delay_reboot=='7MINUTE1':
					minute1_pins_state=defaultdict(list)
					for i in delay_on_reboot_dict['7MINUTE1']:
						minute1_pins_state[i]=HIGH #60 saniye sonra HIGH olacak pinler
						temp_pins_state[i]='*OFF' #60 saniye dolana kadar bu pinler *OFF gozukecek
					tmp_all_pins_state.update(temp_pins_state)
					cache.set('temp_all_pins_state',tmp_all_pins_state) #Pinlerin son durumunu gosteriyor
					cache.set('minute1_pins_state',minute1_pins_state)
					cache.set('dor_minute1',True)

		time.sleep(1.2)	
		return redirect("/control/")
	c={}
	c.update(csrf(request))	
	outlet_list = Config.objects.all()
	c['outlets'] = outlet_list
	if 'outlet_id' in kwargs.keys():
		c['outlet_id'] = int(kwargs['outlet_id'])

	return render_to_response('control.html',c)
		
@login_required
def config(request):
	forms={}
	total_outlet=Config.objects.count()
	for i in range(1,total_outlet+1):
		forms['form_%s'%i]=ConfigForm(instance=Config.objects.get(id=i), prefix='form-'+str(i))
		form_list=sorted(forms.items())
	formset_list=[]
	for i in range(0,total_outlet):
		formset_list.append(form_list[i][1])

	counter=range(8)
	return render_to_response('config.html',{'formset':formset_list, 'loop_times':counter})

@login_required
def config_save(request):
	if request.method == 'GET':
		out_id = request.GET['out_number']
		name = request.GET['name']
		pwr_on_delay = request.GET['pwr_on_delay']
		pwr_off_delay = request.GET['pwr_off_delay']
		reboot_duration = request.GET['reboot_duration']
		state=Config.objects.get(id=int(out_id)).state
	
		outlet=Config(id=int(out_id), name=name, pwr_on_delay=pwr_on_delay,
		 			pwr_off_delay=pwr_off_delay, reboot_duration=reboot_duration,state=state)
		outlet.save()
		result="success"
	
	return HttpResponse(json.dumps(result),mimetype='application/json')	

#@login_required
def cancel_default(request):
	id_num=None

	if request.method == 'GET':
		id_num=request.GET['cancel_number']
	if id_num:
		outlet = Config.objects.get(id=int(id_num))
		if outlet:
			result={}
			result['id'] = outlet.id
			result['name'] = outlet.name
			result['pwr_on_delay'] = outlet.pwr_on_delay
			result['pwr_off_delay'] = outlet.pwr_off_delay
			result['reboot_duration'] = outlet.reboot_duration

	return HttpResponse(json.dumps(result),mimetype='application/json')

def check_last_state(request):
	
	last_state=cache.get('temp_all_pins_state')
	
	on_off=0
	if '*OFF' in last_state.values():
		on_off=1
	if '*ON' in last_state.values():
		on_off=1
	last_state['on_off']=on_off

	return HttpResponse(json.dumps(last_state),mimetype='application/json')