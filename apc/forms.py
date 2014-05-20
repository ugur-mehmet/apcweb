from django import forms
from apc.models import Config
#from django.forms import CharField
from django.core import validators




class ConfigForm(forms.ModelForm):
	#outlet_num = forms.IntegerField()
	
	class Meta:
		model=Config

		fields = ('name','pwr_on_delay','pwr_off_delay','reboot_duration')
		labels= {
			'name':'','pwr_on_delay':'',
			'pwr_off_delay':'','reboot_duration':''

		}

class NetForm(forms.Form):
	OPTIONS = (
                ("1", "Static"),
                ("2", "DHCP"),
               )
	bootmode = forms.ChoiceField(choices=OPTIONS)
	#ipaddress = forms.IPAddressField(max_length=15,required=True, validators=[validators.validate_ipv46_address])
	ipaddress = forms.IPAddressField()
	validate_mask = validators.RegexValidator(regex=r'^255\.255\.255\.[0-5]{1,3}',message='Invalid subnet mask', code='invalid')
	subnetmask = forms.CharField(max_length=15, required=True, validators=[validate_mask])
	gateway = forms.CharField(max_length=15,required=True, validators=[validators.validate_ipv4_address])
	hostname = forms.CharField(max_length=25,required=True)
		