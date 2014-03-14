from django.shortcuts import render, render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from apc.models import Config, Log, Parameter
from django.http import HttpResponse
from apc.forms import ConfigForm
from django.forms.models import modelformset_factory
import json

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
		checked_list = []
		outlet_ids = []
		action_list=request.POST['action_list']
		
		for check in check_list:
			if check in request.POST:
				checked_list.append(check)
				outlet_ids.append(int(check[-1])) #Convert checked_list to outlet id
		return HttpResponse(outlet_ids[0])
		
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

