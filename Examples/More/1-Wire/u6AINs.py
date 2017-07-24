"""
Simple U6 example that reads AIN0, AIN1 and AIN2 with high-res resolution
index 12.

"""

import u6

# Open first found U6
d = u6.U6()
d.getCalibrationData()

# Commands for the Feedback function
coms = []
# AIN0
coms.append(u6.AIN24(PositiveChannel=0, ResolutionIndex=12, GainIndex=0,
                     SettlingFactor=0, Differential=False))
# AIN1
coms.append(u6.AIN24(PositiveChannel=1, ResolutionIndex=12, GainIndex=0,
                     SettlingFactor=0, Differential=False))
# AIN2
coms.append(u6.AIN24(PositiveChannel=2, ResolutionIndex=12, GainIndex=0,
                     SettlingFactor=0, Differential=False))

# Perform commands and get results
results = d.getFeedback(coms)

# Convert binary readings to voltages
ain0 = d.binaryToCalibratedAnalogVoltage(gainIndex=0, bytesVoltage=results[0],
                                         is16Bits=False, resolutionIndex=12)
ain1 = d.binaryToCalibratedAnalogVoltage(gainIndex=0, bytesVoltage=results[1],
                                         is16Bits=False, resolutionIndex=12)
ain2 = d.binaryToCalibratedAnalogVoltage(gainIndex=0, bytesVoltage=results[2],
                                         is16Bits=False, resolutionIndex=12)

print("AIN0 = %f V" % ain0)
print("AIN1 = %f V" % ain1)
print("AIN2 = %f V" % ain2)
