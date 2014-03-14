from django import forms
from apc.models import Config



class ConfigForm(forms.ModelForm):
	#outlet_num = forms.IntegerField()
	
	class Meta:
		model=Config

		fields = ('name','pwr_on_delay','pwr_off_delay','reboot_duration')
		labels= {
			'name':'','pwr_on_delay':'',
			'pwr_off_delay':'','reboot_duration':''

		}
		