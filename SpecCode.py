import time 
import numpy as np
import math
from pijuice import PiJuice
import gpiozero as gz
pijuice = PiJuice(1,0x14)
cpu_temp = gz.CPUTemperature().temperature

verystart = time.perf_counter() # Get time when the program was turned on

try:
    from stellarnet_driverLibs import stellarnet_driver3 as sn
except:
    print("\n\n************************************ ERROR *****************************************")
    print("             ERROR:    Compatible Python Driver DOES NOT EXIST")
    print(" ** See \"stellarnet_driverLibs\" and documentation for all available compiled Drivers")
    print(" **      Contact Stellarnet Inc. ContactUs@StellarNet.us for additional support.")
    print("************************************ ERROR *****************************************\n\n")
    quit()

# For Windows ONLY: Must be run in administrator mode
# Only need to run it one time after switch back from the SpectraWiz.
#sn.installDeviceDriver()

# This resturn a Version number of compilation date of driver
version = sn.version()
print(version)	

# Device parameters to set       
inttime = 2000   # 1-498000 ms
scansavg = 1   # > 1
smooth = 0     # 1-4
xtiming = 3    # 1-4


#init Spectrometer - Get BOTH spectrometer and wavelength
spectrometer, wav = sn.array_get_spec(0) # 0 for first channel and 1 for second channel , up to 127 spectrometers
"""
# Equivalent to get spectrometer and wav separately:
spectrometer = sn.array_get_spec_only(0) 
wav = sn.getSpectrum_X(spectrometer)
"""

print(spectrometer)
sn.ext_trig(spectrometer, True)

# Get device ID
deviceID = sn.getDeviceId(spectrometer)
print('\nMy device ID: ', deviceID)

# Get current device parameter
currentParam = sn.getDeviceParam(spectrometer)

# Call to Enable or Disable External Trigger to by default is Disbale=False -> with timeout
# Enable or Disable Ext Trigger by Passing True or False, If pass True than Timeout function will be disable, so user can also use this function as timeout enable/disbale 
sn.ext_trig(spectrometer,True)

# Only call this function on first call to get spectrum or when you want to change device setting.
# -- Set last parameter to 'True' throw away the first spectrum data because the data may not be true for its inttime after the update.
# -- Set to 'False' if you want to throw away the first data, however your next spectrum data might not be valid.
sn.setParam(spectrometer, inttime, scansavg, smooth, xtiming, True) 

"""
# Get Y value ONLY :
first_data = sn.getSpectrum_Y(spectrometer)
"""
i = 1
j = 1  # Counter for the while loop
temp = inttime

while i == 1:  # Infinite while loop
    actualstart = time.perf_counter()  # Get time at start
    # Reset the parameters so that inttime updates
    if temp != inttime:
        sn.setParam(spectrometer, inttime, scansavg, smooth, xtiming, False)
    temp = inttime
    print("The integration time is " + str(inttime))
    
    start = time.perf_counter()  # Get time at start
    print("Started collection")
    # Get spectrometer data - Get BOTH X and Y in single return
    data = sn.array_spectrum(spectrometer, wav)  # get specturm for the spectrometer
    print("Finished collection")
    end = time.perf_counter()  # Get time at end
    
    # Get all the info from the PiJuice and Pi
    batt_temp = pijuice.status.GetBatteryTemperature()['data']
    charge = pijuice.status.GetChargeLevel()['data']
    volt = pijuice.status.GetBatteryVoltage()['data']
    cpu_temp = gz.CPUTemperature().temperature
    
    # Flash the led
    pijuice.status.SetLedBlink('D2',1,[127,0,200],50, [0,0,0],50)

    f = open("DataStorage/specdata"+str(j)+".txt", "w+")
    np.savetxt(f,data,fmt='%5.9f',delimiter=' ',header='Spectrum started at t = ' + str(start-verystart) + ' seconds. \nCollection time of spectrum is ' + str(end-start) + ' seconds. \nIntegration time is inttime = ' + str(inttime) + ' ms. \nBattery temperature is battemp = ' + str(batt_temp)+ ' C. \nCPU temperature is cputemp = ' + str(cpu_temp)+ ' C. \nBattery charge is charge = ' + str(charge)+ ' %. \nBattery voltage is volt = ' + str(volt) + ' mV')
    
    max_spectrum = 0
    for row in data:
        if row[1] > max_spectrum:
            max_spectrum = row[1]
    f.close()
    print("The max spectral value is " + str(max_spectrum))
    # Change the integration time so that the spectrum stays within the range. Make this better please
    if max_spectrum > 65000:
        inttime = int(inttime/10)  # 1-498000 ms
    elif max_spectrum < 5000:
        inttime = int(inttime*10)  # 1-498000 ms
    else:
        y = 0.5*(max_spectrum/3000 - 10) # This will slowly centre the function towards a value of 30000 counts
        if y > 1:
            inttime = int(inttime/y)
        elif y < -1:
            inttime = int(inttime*-y)
        # If the value is in between 36000 and 24000 the integration time will do nothing
    print("The integration time was calculated at " + str(inttime))
    
    if inttime > 30000:
        inttime = 30000 # Have a max integration time of "thirty" seconds but is more around 1min:30
    
    j += 1  # Increment file name
    if j == 20000:  # Once 20000 files have been collected it will shut off. This is 5h30min at 1 second each spectrum.
        i = 2
    actualend = time.perf_counter()  # Get time at end
    print("It took " + str(actualend-actualstart) + " seconds to run through the code")
    print("It took " + str(end-start) + " seconds to collect spectrum\n")
    while actualend - actualstart < 1:  # This waits until at least 1 second has elapsed
        actualend = time.perf_counter()


#==============================================
# Burst FIFO mode: Not recommended with high integration time.
# burst_data_2 = sn.getBurstFifo_Y(spectrometer)
#==============================================

# Release the spectrometer before ends the program
sn.reset(spectrometer)

# For Windows ONLY: Must be run in administrator mode
# sn.uninstallDeviceDriver() 


