from django.shortcuts import render, render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from apc.models import Config, Log, Parameter
from django.http import HttpResponse, HttpResponseRedirect
from apc.forms import ConfigForm
#from django.forms.models import modelformset_factory
import json
from collections import defaultdict
from django.core.cache import cache

HIGH = 0
LOW = 1
# Create your views here.
@login_required
def index(request):

	outlet_list=Config.objects.all()
	c={'outlets':outlet_list}
	return render_to_response("status.html",c)
	#return render_to_response("config.html")


def login(request):
	if request.method=='POST':
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			if user.is_active:
				auth.login(request,user)
				request.session['kullanici_id']=user.id 
				response = redirect('status')
				#response.set_cookie('remind_me', True)
				return response
	'''elif 'cancel' in request.POST:
		return redirect('login')'''
	c = {}
	c.update(csrf(request))
	return render_to_response("login.html",c)

@login_required
def logout(request):
	auth.logout(request)
	#return redirect('/')
	return redirect('login')

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
			

@login_required
def control(request,**kwargs):
	
	c={}
	c.update(csrf(request))
	if request.method != 'POST':

		outlet_list = Config.objects.all()
		c['outlets'] = outlet_list
		if 'outlet_id' in kwargs.keys():
			c['outlet_id'] = int(kwargs['outlet_id'])

		return render_to_response('control.html',c)
	else:
		check_list=['checkbox_1', 'checkbox_2','checkbox_3','checkbox_4',
					'checkbox_5','checkbox_6','checkbox_7','checkbox_8']
		#checked_list = []
		outlet_ids = []
		outlet_pins = []
		action_name=request.POST['action_list']
		
		for check in check_list:
			if check in request.POST:
				#checked_list.append(check)
				outlet_ids.append(int(check[-1])) 
				outlet_pins.append(int(check[-1])-1) #Convert checked_list from outlet id to pins [0,1,2 ..]
		
		if action_name != '1' and len(outlet_ids)>0:

			cache.set('checked_outlet_pins', outlet_pins)
			cache.set('all_pins_state', all_pins_state())
			cache.set('checked_outlets_state',all_pins_state(*outlet_pins))
			cache.set('action_name', action_name)
					
			if action_name == '3':  #Delayed on ise Tum outletler icin pwr_on_delay degerlerini al
				'''Oncelikle pwr_on_delay parametresine gore her bir outlet icin dictionary olustur.
				Ornek: {'Immmediate':[1,2], '15 Seconds':[0],}
				Bi dictionary olusurken sadece off durumda olan outletler secilecek. On durumda olanlari
				pwr_on_delay yapmaya gerek yok.

				'''
				delay_on_dict = defaultdict(list)
				for id in outlet_ids:
					pwr_on_delay = Config.objects.get(pk=id).pwr_on_delay
					state = Config.objects.get(pk=id).state
					if state==0:
						delay_on_dict[pwr_on_delay].append(id)
				cache.set('delay_on_dict',delay_on_dict)

			if action_name == '5':  #Delayed off ise Tum outletler icin pwr_off_delay degerlerini al
				'''Oncelikle pwr_off_delay parametresine gore her bir outlet icin dictionary olustur.
				Ornek: {'Immmediate':[1,2], '15 Seconds':[0],}

				'''
				delay_off_dict = defaultdict(list)
				for id in outlet_ids:
					pwr_off_delay = Config.objects.get(pk=id).pwr_off_delay
					delay_off_dict[pwr_off_delay].append(id)
				cache.set('delay_off_dict',delay_off_dict)	

			if action_name == '7':  #Delayed reboot ise Tum outletler icin reboot_duration degerlerini al
				'''Oncelikle reboot_duration parametresine gore her bir outlet icin dictionary olustur.
				Ornek: {'05 Seconds':[1,2], '15 Seconds':[0],}

				'''
				delay_reboot_dict = defaultdict(list)
				for id in outlet_ids:
					reboot_duration = Config.objects.get(pk=id).reboot_duration
					delay_reboot_dict[reboot_duration].append(id)	
				cache.set('delay_reboot_dict',delay_reboot_dict)
			
		return HttpResponseRedirect(reverse("apc.views.index"))
		#return HttpResponse(cache.get('outlet_state_dict'))
		
		# for id in outlet_ids:
		# 	if action_list == '1':
		# 		pass
		# 	elif action_list == '2':
		# 		Digital
		

		# #if action_list == 
		# '''
		# "1" 'No Action'
  #       "2" 'Immediate On'
  #       "3" 'Delayed On'
  #       "4" 'Immediate Off'
  #       "5" 'Delayed Off'
  #       "6" 'Immediate Reboot'
  #       "7" 'Delayed Reboot'
  #       "8" 'Cancel Pending Commands'
		# '''	
		

		

	

@login_required
def config(request):
	#config_lists = Config.objects.all()
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
	#if out_id:
		outlet=Config(id=int(out_id), name=name, pwr_on_delay=pwr_on_delay,
		 			pwr_off_delay=pwr_off_delay, reboot_duration=reboot_duration)
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
			# result['pwr_on_delay'] = outlet.get_pwr_on_delay_display()
			# result['pwr_off_delay'] = outlet.get_pwr_off_delay_display()
			# result['reboot_duration'] = outlet.get_reboot_duration_display()
			result['pwr_on_delay'] = outlet.pwr_on_delay
			result['pwr_off_delay'] = outlet.pwr_off_delay
			result['reboot_duration'] = outlet.reboot_duration

	return HttpResponse(json.dumps(result),mimetype='application/json')
	#return HttpResponse(id_num)

