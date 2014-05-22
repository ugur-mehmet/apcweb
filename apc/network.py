
import subprocess
from django.http import HttpResponse
import time

class interfaces:
	def write_template(self,template,**net_dict):
		# Back up the old interfaces file.
		subprocess.call(['sudo', 'mv', self.INTERFACES, self.BACKUP])
		# Prepare to write the new interfaces file.
		interfaces = open(self.TEMP_INTERFACES, "a")
		proc=subprocess.Popen(["hostname"], stdout=subprocess.PIPE, shell=True)
		(hostname,err)=proc.communicate()
		current_hostname=hostname[:-1]
		#change_hostname_cmd='sudo sed -e \'s/'+current_hostname+'/'+net_dict['hostname']+'/g\''+' -i /etc/hosts'
		change_hostname_cmd='sudo sed -e \'/127.0.1.1/ c 127.0.1.1\t'+net_dict['hostname']+'\''+' -i /etc/hosts'
		cmd='echo '+net_dict['hostname']+'|sudo tee /etc/hostname'
		#cmd2='echo '+ '127.0.1.1	' + net_dict['hostname']+'|sudo tee -a /etc/hosts'
		subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
		#subprocess.Popen(cmd2,stdout=subprocess.PIPE,shell=True)
		subprocess.Popen(change_hostname_cmd,stdout=subprocess.PIPE,shell=True)
		cmd_reboot='sudo sleep 10;sudo shutdown -r now'
		#cmd_reboot='date'
		if template=='2':
			interfaces.write(self.dhcp)
			subprocess.call(['sudo', 'mv', self.TEMP_INTERFACES, self.INTERFACES])
		if template=='1':
			net_dict['bootmode']='static'
			interfaces.write(self.static_template.substitute(net_dict))
			subprocess.call(['sudo', 'mv', self.TEMP_INTERFACES, self.INTERFACES])
		#response = HttpResponse()
		#response.write('Please wait... The system is rebooting now to effeckt the changes')
		
		#time.sleep(5)
		subprocess.Popen(cmd_reboot,stdout=subprocess.PIPE,shell=True)


			

	def __init__(self):

		from string import Template
		self.INTERFACES = '/etc/network/interfaces'
		self.TEMP_INTERFACES = '/tmp/interfaces'
		self.BACKUP = '/etc/network/interfaces.old'


		self.dhcp='''
auto lo\n
iface lo inet loopback\n
iface eth0 inet dhcp\n
allow-hotplug wlan0\n
iface wlan0 inet manual\n
wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf\n
iface default inet dhcp\n
'''
		self.static='''
auto lo\n
iface lo inet loopback\n
iface eth0 inet $bootmode\n
address $ipaddress\n
netmask $subnetmask\n
gateway $gateway\n
#hostname $hostname
'''
		#dhcp_template=Template(dhcp)
		self.static_template=Template(self.static)





