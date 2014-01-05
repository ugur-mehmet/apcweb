'''
APC AP9212 model MasterSwitch Power Distribution unit uzerindeki Web Modul arizali oldugundan onun isini yapmasi icin
Raspberry Pi kullanilacak. Bu program ile APC uzerindeki outletleri kontrolden UCN5821A 8-BIT SERIAL-INPUT, LATCHED DRIVERS
entegresi kontrol edilecek.
Entegre Pinouts:
1- CLOCK						16- OUT1
2- SERIAL DATA IN				15- OUT2
3- LOGIC GROUN					14- OUT3
4- LOGIC SUPPLY					13- OUT4
5- SERIAL DATA OUT				12- OUT5
6- STROBE						11- OUT6
7- OUTPUT ENABLE (ACTIVE LOW)	10- OUT7
8- POWER GROUND					9-	OUT8

DATA IN hazir olduktan sonra shift register icin CLOCK pozitif yukselen kenara cekilir.
Bu sekilde 8 bit data shift register a aktarildiktan sonra en son STROBE High yapildiginda cikista 8 bit gorulur.  
'''
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

#Define modes
ALL = -1
HIGH = 0
LOW = 1

#Define pins
_DATA_pin = 16		#pin 2 on the UCN5821A 	(16 - > P4 on RASPI)
_CLOCK_pin = 18		#pin 1 on the UCN5821A	(18 - > P5 on RASPI)
_STROBE_pin = 22	#pin 6 on the UCN5821A	(22 - > P6 on RASPI)

#is used to store states of all pins
_registers = list()

#How many of the shift registers - you can change them with shift registers method
_number_of_shiftregisters = 1 #We have one register on the APC unit.

def pinsSetup(**kwargs):
	'''
	Allows the user to define custom pins
	'''
	global _DATA_pin, _CLOCK_pin, _STROBE_pin
	
	custompins = 0
	datapin = _DATA_pin
	clockpin = _CLOCK_pin
	strobepin = _STROBE_pin
	
	if len(kwargs) > 0:
		custompins = 1
		
		_DATA_pin = kwargs.get('data', _DATA_pin)
		_CLOCK_pin = kwargs.get('clock', _CLOCK_pin)
		_STROBE_pin = kwargs.get('strobe', _STROBE_pin)
	
	if custompins:
		if _DATA_pin != datapin or _CLOCK_pin != clockpin or _STROBE_pin != strobepin:
			GPIO.setwarnings(True)
	
	else:
		GPIO.setwarnings(False)
	
	GPIO.setup(_DATA_pin, GPIO.OUT)
	GPIO.setup(_CLOCK_pin, GPIO.OUT)
	GPIO.setup(_STROBE_pin, GPIO.OUT)
	
def startupMode(mode, execute = False):
	'''
	Allows the user to change the default state of the shift registers outputs
	'''
	
	if isinstance(mode, int):
		if mode is HIGH or mode is LOW:
			_all(mode, execute)
		else:
			raise ValueError('The mode can be only HIGH or LOW or Dictionary with specisific pins and modes')
	elif isinstance(mode, dict):
		for pin, mode in mode.items():
			_setPin(pin, mode)
		if execute:
			_execute()
	else:
		raise ValueError('The mode can be only HIGH or LOW or Dictionary with specisific pins and modes')
	
def shiftRegisters(num):
	'''
	Allows the user to define the number of shift registers are connected
	'''
	global _number_of_shiftregisters
	_number_of_shiftregisters = num
	_all(LOW)
	
def digitalWrite(pin,mode):
	'''
	Allows the user to set the state of a pin on the shift register
	'''
	
	if pin == ALL:
		_all(mode)
	else:
		if len(_registers) == 0:
			_all(LOW)
		_setPin(pin,mode)
	_execute()
	
def delay(millis):
	'''
	Used for creating a delay between commands
	'''
	millis_to_seconds = float(millis)/1000
	return sleep(millis_to_seconds)
	
def _all_pins():
	return _number_of_shiftregisters * 8
	
def _all(mode, execute = True):
	all_shr = _all_pins()
	
	for pin in range(0,all_shr):
		_setPin(pin, mode)
	if execute:
		_execute()
	return _registers
	
def _setPin(pin, mode):
	try:
		_registers[pin] = mode
	except IndexError:
		_registers.insert(pin, mode)
		
def _execute():
	all_pins = _all_pins()
	GPIO.output(_STROBE_pin, GPIO.HIGH) #Cikislar RASPI cikisinda invert edildigi icin UCN5821A entegresine uydurmak icin ters calisiyor. 8 bit Cikis yok
	
	# for dongusu 7 6 5 4 3 2 1 0 degerlerini alacak
	for pin in range(all_pins -1, -1, -1):
		GPIO.output(_CLOCK_pin, GPIO.HIGH) # Invert dolayisiyla ters gonderildi. CLOCK pasif
		
		pin_mode = _registers[pin]
		
		GPIO.output(_DATA_pin, pin_mode)
		delay(20)
		GPIO.output(_CLOCK_pin, GPIO.LOW) #Invert dolayisiyla ters gondeildi. Shift Register
		delay(5)
	GPIO.output(_STROBE_pin, GPIO.LOW) #Invert nedeniyle ters gonderildi. 8 bit cikis ver
	
pinsSetup()