import sqlite3
import datetime
import calendar
import time 
import threading
import subprocess
import re
import sys
import time

class SensorStore:
    def __init__(self):
        # reentrant lock used for all sqlite3 operations
        self.lock = threading.RLock()
        
    def __acquire_lock(self):
        self.lock.acquire()
        
    def __release_lock(self):
        self.lock.release()
        
    def get_conn(self):
        return sqlite3.connect('test.db', check_same_thread=False, timeout=20)
        
    # return id
    def create_sensor(self, name, units):
        self.__acquire_lock()
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("insert into sensor(name, unit) values ( ?, ? )", ( name, units ) )
        conn.commit()
        conn.close()
        self.__release_lock()
        
    def get_sensor(self, name):
        self.__acquire_lock()
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("select id from sensor where name = ?", (name,))
        result = c.fetchone()
        conn.close()
        self.__release_lock()
        
        if result is None:
            return None
        else:
            return result[0]
        
    def put_float_data(self, sensor, value, time):
        self.__acquire_lock()
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("insert into sensor_float_data(val, timestamp, sensor_id) values( ?, ?, ? )", (value, calendar.timegm(time.utctimetuple()), sensor))
        conn.commit()
        self.__release_lock()
        
    def get_latest_float_reading(self, sensor):
        self.__acquire_lock()
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("select max(timestamp), val from sensor_float_data where sensor_id = ?", (sensor, ))
        result = c.fetchone()
        if result is not None and type(result) is tuple and result[0] is None:
            result = None
        conn.close()
        self.__release_lock()
        return result
        
    def init_sensor(self, name, units):
        self.__acquire_lock()
        sensor = self.get_sensor(name)
        
        if sensor is None:
            sensor = self.create_sensor(name, units)
        self.__release_lock()
        
        return sensor
    
    
temperature = "temp1"
humidity = "hum1"

class DHTSensorSource(threading.Thread):
    def __init__(self, temp, hum, pin, sensor_store):
        threading.Thread.__init__(self)
        self.temperature = temp
        self.humidity = hum
        self.pin = pin
        self.sensor_store = sensor_store
        self.shutdown = False
        
    def run ( self ):
        while(not self.shutdown):
            # Run the DHT program to get the humidity and temperature readings!
            
            output = subprocess.check_output(["./Adafruit_DHT", "2302", self.pin]);
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
            
            timestamp = datetime.datetime.utcnow()
            self.sensor_store.put_float_data(self.temperature, float(temp), timestamp )
            self.sensor_store.put_float_data(self.humidity, float(humidity), timestamp )
            
            time.sleep(40)
        print "Shutting down DHT writer for pin {}".format(self.pin)
        return None
  
class SlowWriter(threading.Thread):
    '''Testing class simulating a thread writing sensor data'''
    def __init__(self, sensor, sleep_delay, sensor_store):
        threading.Thread.__init__(self)
        self.sensor = sensor
        self.sleep_delay = sleep_delay
        self.sensor_store = sensor_store
        self.shutdown = False
        
    def run ( self ):
        for i in range(0, 2000):
            self.sensor_store.put_float_data(self.sensor, i * 1.1, datetime.datetime.utcnow())
            time.sleep(self.sleep_delay)
            
            if self.shutdown:
                print "Shutting down slow writer thread!"
                return None
          
class UpdateReader(threading.Thread):
    
    def __init__(self, sensor, name, sleep_delay, sensor_store):
        threading.Thread.__init__(self)
        self.sensor = sensor
        self.name = name
        self.sleep_delay = sleep_delay
        self.sensor_store = sensor_store
        self.shutdown = False
        
    def run ( self ):
        while True:
            try:
                reading = self.sensor_store.get_latest_float_reading(self.sensor)
                
                if reading is None:
                    print "No reading available"
                else:
                    if reading[0] is not None:
                        timestamp=datetime.datetime.utcfromtimestamp(reading[0])
                        delta = datetime.datetime.utcnow() - timestamp
                        print "{} reading is {} at {} ({} ago)".format(self.name, reading[1], timestamp.strftime('%Y-%m-%d %H:%M:%S'), delta)
                time.sleep(self.sleep_delay)
            except sqlite3.OperationalError:
                print "Databasetimeout, will try again"
                time.sleep(self.sleep_delay)
                
            if self.shutdown:
                print "Shutting down updater thread!"
                return None


store = SensorStore()

therm = store.init_sensor(temperature, "C")
hum = store.init_sensor(humidity, "%")

try:
  thread1=DHTSensorSource(therm, hum, "4", store)
  thread1.start()
  thread2=UpdateReader(therm, "Temperature", 1, store)
  #thread3=UpdateReader(hum, 2, store)
  thread2.start()
  #thread3.start()
  while True:
      time.sleep(1)
except (KeyboardInterrupt, SystemExit):
  print '\n! Received keyboard interrupt, quitting threads.\n'
  thread1.shutdown = True
  thread2.shutdown = True
  #thread3.shutdown = True
  thread1.join()
  thread2.join()
  #thread3.join()
  print "Exit main"

