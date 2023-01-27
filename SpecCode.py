data = "Hello There \n"  # This will be changed to whatever is output by spectrometer

f = open("specdata.txt", "w+")
f.write(data)
f.close()
