from django.contrib import admin
from apc.models import Config, Log, Parameter

# Register your models here.
class ConfigAdmin(admin.ModelAdmin):
	list_display = ('outlet', 'name', 'state', 'pwr_on_delay', 'pwr_off_delay', 'reboot_duration')

class LogAdmin(admin.ModelAdmin):
	list_display = ('outlet_name', 'text', 'created_at', 'mod_by', 'log_type')

class ParameterAdmin(admin.ModelAdmin):
	list_display = ('device_name','location', 'contact')

admin.site.register(Config, ConfigAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Parameter,ParameterAdmin)