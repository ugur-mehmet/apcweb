#!/usr/bin/env python
######################################################################################
## 					APC AC POWER CONTROL SYSTEM			                            ##
## ---------------------------------------------------------------------------------##
## Mehmet UGUR Aralik 2013                                                          ##
## Canakkale GTH                                                                    ##
## Revision History                                                                 ## 
## V1.00 - APC system                                                               ##
######################################################################################

# This program shutdowns the raspberry pi output ports and sets from output mode to input mode them before shutdown or restart. 
#

import RPi.GPIO as GPIO
import sys

#sys.path.append('/home/apc')

from apc_5821A import *


##Main Program##
digitalWrite(ALL,LOW)
GPIO.cleanup()
