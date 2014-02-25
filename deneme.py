from apc.models import Config

from apc.forms import ConfigForm
from django.forms.models import modelformset_factory

data=[]
	
for i in range(1,9):
	outlet_dict={}
	outlet=Config.objects.get(id=i)
	outlet_dict['outlet_num']=outlet.id
	outlet_dict['name']=outlet.name
	outlet_dict['pwr_on_delay']=outlet.pwr_on_delay
	outlet_dict['pwr_off_delay']=outlet.pwr_off_delay
	outlet_dict['reboot_duration']=outlet.reboot_duration
	data.append(outlet_dict)