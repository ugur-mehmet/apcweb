from django.db import models

# Create your models here.
class Config(models.Model):
	outlet = models.CharField(max_length=100)
	name = models.CharField(max_length=100)
	state = models.BooleanField()
	pwr_on_delay = models.CharField(max_length=10)
	pwr_off_delay = models.CharField(max_length=10)
	reboot_duration = models.CharField(max_length=10)

	def __str__(self):
		return self.name

	
class Log(models.Model):
	log_type_choices = (
		('SYS', 'System'),
		('MS', 'MasterSwitch'),)
	outlet_name = models.ForeignKey(Config)
	text = models.CharField(max_length=200)
	created_at = models.DateTimeField(auto_now_add=True)
	mod_by = models.CharField(max_length=50)
	log_type = models.CharField(max_length=50, choices=log_type_choices, default='MS')
	outlet_name.short_description = "Outlet Name"
	
class Parameter(models.Model):
	device_name = models.CharField(max_length=100)
	location = models.CharField(max_length=100)
	contact = models.CharField(max_length=100)




