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
	outlet_list = Config.objects.all()
	c={'outlets':outlet_list}
	if 'outlet_id' in kwargs.keys():
		c['outlet_id'] = int(kwargs['outlet_id'])

	return render_to_response('control.html',c)
	#return HttpResponse(c['outlet_id'])

@login_required
def config(request):
	#config_lists = Config.objects.all()
	data=[]
	outlet_dict={}
	for i in range(1,9):
		outlet_dict={}
		outlet=Config.objects.get(id=i)
		outlet_dict['outlet_num']=outlet.id
		outlet_dict['name']=outlet.name
		outlet_dict['pwr_on_delay']=outlet.pwr_on_delay
		outlet_dict['pwr_off_delay']=outlet.pwr_off_delay
		outlet_dict['reboot_duration']=outlet.reboot_duration
		data.append(outlet_dict)

	'''
	c = {}
	c['config_list'] = configs'''
	ConfigFormSet = modelformset_factory(Config,ConfigForm, extra=0)
	configset = ConfigFormSet(initial=data)
	#form=ConfigForm()
	return render_to_response('config.html',{'formsets':configset})

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
			result['pwr_on_delay'] = outlet.get_pwr_on_delay_display()
			result['pwr_off_delay'] = outlet.get_pwr_off_delay_display()
			result['reboot_duration'] = outlet.get_reboot_duration_display()
	# id_num = 5
	return HttpResponse(json.dumps(result),mimetype='application/json')
	#return HttpResponse(id_num)

