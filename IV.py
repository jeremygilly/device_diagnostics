#Call both python scripts.
#~ Capture initial resistance for current measurements
# Apply x1 to x2 V
# Measure y1 to y2 V
# Draw graph

import sys

path_to_ads1261evm = "/home/pi/Documents/ads1261evm/"
ads1261evm_file = "ads1261evm.py"
path_to_dac7562evm = "/home/pi/Documents/dac7562evm/"
dac7562evm_file = "dac7562evm.py"

sys.path.insert(0,path_to_ads1261evm)
sys.path.insert(0,path_to_dac7562evm)

import ads1261evm as ads1261
import dac7562evm as dac7562

import numpy as np
import matplotlib.pyplot as plt
import time
import statistics

# create array of desired V
def create_array(min_V = 0, max_V = 2450, datapoints = 100):
	x = np.linspace(min_V, max_V, datapoints+1, endpoint = True)
	return x

# create array of measured V
#~ def 

def setup():
	# set up DAC
	dac = dac7562.DAC7562()
	dac.power(mode = 'power_up', dac = 'ab')
	dac.ldac(ldac_a = 'synchronous', ldac_b = 'synchronous')
	Vref = dac.reference(reference = 'internal')
	dac_a, dac_b = dac.gain(dac_a = 1, dac_b = 1)

	# set up ADC
	adc = ads1261.ADC1261()
	# Set pins, Check for external clock, DRDY pin check, Set start pin low
	adc.setup_measurements()
	# Configure and verify ADC settings
	DeviceID, RevisionID = adc.check_ID() 
	return dac, adc, Vref, dac_a, dac_b
	
def main():
	ripple_time = 5/1000000
	dac, adc, Vref, dac_a, dac_b = setup()
	R = 3300 # Rds in Ohms
	Vin_array = create_array() # array of voltages [in mV] created
	
	adc.set_frequency(data_rate=19200, digital_filter='sinc1')
	adc.print_status()
	adc.print_mode3()
	adc.PGA(BYPASS=1)
	adc.print_PGA()
	adc.reference_config(reference_enable=1)
	adc.print_reference_config()
	adc.calibration()
	adc.start1()
	adc.mode1(CHOP='normal', CONVRT='continuous', DELAY = '50us')
	adc.print_mode1()
	
	response_array = []
	IV_array = []
	DAC_array_raw = []
	ADC_array_raw = []
	DAC_array_averaged = []
	ADC_array_averaged = []
	
	for Vin in Vin_array:
		print(Vin)
		Vout = dac.Vout(dac = 'a', command = 'write_update', Vout = Vin, Vref = Vref, gain = dac_a)
		time.sleep(ripple_time)
		for i in range(100):
			# measure output from DAC
			adc.choose_inputs(positive = 'AIN6', negative = 'AIN7')
			response_DAC = adc.collect_measurement(method='hardware', reference=5000, gain = 1)
			
			# measure output from sensor
			adc.choose_inputs(positive = 'AIN6', negative = 'AIN7')
			response_ADC = adc.collect_measurement(method='hardware', reference=5000, gain = 1)
			
			if response_DAC != None and response_ADC != None:
				DAC_array_raw.append(response_DAC)
				ADC_array_raw.append(response_ADC)
			else:
				pass
			
		DAC_array_averaged.append(np.nanmean(DAC_array_raw))
		ADC_array_averaged.append(np.nanmean(ADC_array_raw))
		DAC_array_raw = []
		ADC_array_raw = []
		
	plt.scatter(DAC_array_averaged,ADC_array_averaged)
	plt.show()
	#~ dac.
	#~ print(x)
	
if __name__ == "__main__":
	main()
