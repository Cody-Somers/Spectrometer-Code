import time  # Check whether this is compatible with the pi.
# You might have to do conda install time to get this to work

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
inttime = 50   # 1-498000 ms
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
while i == 1:  # Infinite while loop
    start = time.perf_counter()  # Get time at start
    # Get spectrometer data - Get BOTH X and Y in single return
    data = sn.array_spectrum(spectrometer, wav)  # get specturm for the spectrometer
    f = open("specdata"+str(j)+".txt", "w+")
    for line in f:
        f.write(str(data[line])) # if this doesnt work, remove for loop and line index
    f.close()
    # print('First data:', data )
    amplitude_data = sn.getSpectrum_Y(spectrometer)  # Get only the y value
    max_spectrum = max(amplitude_data)  # This is the maximum of the y values
    # Change the integration time so that the spectrum stays within the range. Make this better please
    if max_spectrum > 50000:
        inttime = inttime/2  # 1-498000 ms
    elif max_spectrum < 10000:
        inttime = inttime*2  # 1-498000 ms
    j += 1  # Increment file name
    if j == 10:  # Delete this eventually, this is for testing purposes so it does not run forever
        i = 2
    end = time.perf_counter()  # Get time at end
    while end - start < 1:  # This waits until at least 1 second has elapsed
        end = time.perf_counter()
        print(end-start)


#==============================================
# Burst FIFO mode: Not recommended with high integration time.
# burst_data_2 = sn.getBurstFifo_Y(spectrometer)
#==============================================

# Release the spectrometer before ends the program
sn.reset(spectrometer)

# For Windows ONLY: Must be run in administrator mode
# sn.uninstallDeviceDriver() 
