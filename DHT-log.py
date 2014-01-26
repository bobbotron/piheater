#!/usr/bin/python

import subprocess
import re
import sys
import time
import datetime

# ===========================================================================
# Google Account Details
# ===========================================================================

# Account details for google docs

# ===========================================================================
# Example Code
# ===========================================================================



# Continuously append data
while(True):
  # Run the DHT program to get the humidity and temperature readings!

  output = subprocess.check_output(["./Adafruit_DHT", "2302", "4"]);
  # print output
  matches = re.search("Temp =\s+([0-9.]+)", output)
  if (not matches):
	time.sleep(3)
	continue
  temp = float(matches.group(1))
  
  # search for humidity printout
  matches = re.search("Hum =\s+([0-9.]+)", output)
  if (not matches):
	time.sleep(3)
	continue
  humidity = float(matches.group(1))

  print "Temperature: %.1f C" % temp
  print "Humidity:    %.1f %%" % humidity
 
  # Append the data in the spreadsheet, including a timestamp
  try:
    with open("temp.txt", "a") as myfile:
	s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        myfile.write("%.1f C" % temp)
	myfile.write(";")
	myfile.write("hum %.1f" % humidity)
	myfile.write(";")
        myfile.write(s)
	myfile.write("\n")

  except:
    print "Unable to append data.  Check your connection?"
    sys.exit()

  # Wait 30 seconds before continuing
  time.sleep(30)
