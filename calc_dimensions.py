from math import pi

#compute the internal volume of the tube
tubeLength = 20 #meters
tubeDiameter = 0.0127 #meters
#volume of a cylinder is pi * r**2 * height
totalVolume = pi * (tubeDiameter/2)**2 * tubeLength
print(totalVolume)
#total volume is in cubic meters, want it in gallons
volumeGalons = 0.6692897735
