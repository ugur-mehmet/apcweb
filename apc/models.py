from django.db import models

# Create your models here.
class Config(models.Model):
	outlet_choices=(
		('OUTLET1','Outlet 1'),
		('OUTLET2','Outlet 2'),
		('OUTLET3','Outlet 3'),
		('OUTLET4','Outlet 4'),
		('OUTLET5','Outlet 5'),
		('OUTLET6','Outlet 6'),
		('OUTLET7','Outlet 7'),
		('OUTLET8','Outlet 8'),
		)
	outlet = models.CharField(max_length=100,
								choices=outlet_choices,

								)
	name = models.CharField(max_length=100)
	state = models.NullBooleanField()
	#state = models.BooleanField(default=True)
	pwr_on_choices = (
		('IMMEDIATE', 'Immediate'),
		('SECONDS15', '15 Seconds'),
		('SECONDS30', '30 Seconds'),
		('SECONDS45', '45 Seconds'),
		('MINUTE1', '1 Minute'),
		('MINUTES2', '2 Minutes'),
		('MINUTES5', '5 Minutes'),
		('NEVERON', 'Never On'),	
		)
	pwr_on_delay = models.CharField(max_length=10,
									choices=pwr_on_choices,
									default='IMMEDIATE',
									blank=False,
									)
	pwr_off_choices = (
		('IMMEDIATE', 'Immediate'),
		('SECONDS15', '15 Seconds'),
		('SECONDS30', '30 Seconds'),
		('SECONDS45', '45 Seconds'),
		('MINUTE1', '1 Minute'),
		('MINUTES2', '2 Minutes'),
		('MINUTES5', '5 Minutes'),
		('NEVEROFF', 'Never Off'),	
		)
	pwr_off_delay = models.CharField(max_length=10,
									choices=pwr_off_choices,
									default='IMMEDIATE',
									blank=False,
									)
	reboot_choices = (
		('SECONDS05', '05 Seconds'),
		('SECONDS10', '10 Seconds'),
		('SECONDS15', '15 Seconds'),
		('SECONDS20', '20 Seconds'),
		('SECONDS30', '30 Seconds'),
		('SECONDS45', '45 Seconds'),
		('MINUTE1', '1 Minute'),
		)
	reboot_duration = models.CharField(max_length=10,
									choices = reboot_choices,
									default='SECONDS05',
									blank=False,
									)

	def __str__(self):
		return self.name

class Action(models.Model):
	action_name = models.CharField(max_length=200)


class Log(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	mod_by = models.CharField(max_length=50)
	log_type_chocies=(
				('SYS','System'),
				('MASTER', 'MasterSwitch'),	
				)
	log_type=models.CharField(max_length=20,
							choices = log_type_chocies,
							default = 'MASTER' 
							)
	event_text = models.CharField(max_length=250)
	
	event_text.short_description = "Events"
	
class Parameter(models.Model):
	device_name = models.CharField(max_length=100)
	location = models.CharField(max_length=100)
	contact = models.CharField(max_length=100)




