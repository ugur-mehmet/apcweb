from django.shortcuts import render, render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from apc.models import Config, Log, Parameter
from django.http import HttpResponse

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
	return render_to_response('config.html')