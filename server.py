import sqlite3
import datetime
import calendar
import time 
import threading

class SensorStore:
    def get_conn(self):
        return sqlite3.connect('test.db', check_same_thread=False)
        
    # return id
    def create_sensor(self, name, units):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("insert into sensor(name, unit) values ( ?, ? )", ( name, units ) )
        conn.commit()
        conn.close()
        
    def get_sensor(self, name):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("select id from sensor where name = ?", (name,))
        result = c.fetchone()
        conn.close()
        if result is None:
            return None
        else:
            return result[0]
        
    def put_float_data(self, sensor, value, time):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("insert into sensor_float_data(val, timestamp, sensor_id) values( ?, ?, ? )", (value, calendar.timegm(time.utctimetuple()), sensor))
        conn.commit()
        
    def get_latest_float_reading(self, sensor):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("select max(timestamp), val from sensor_float_data where sensor_id = ?", (sensor, ))
        result = c.fetchone()
        conn.close()
        return result
    
class SlowWriter(threading.Thread):
    
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
    
    def __init__(self, sensor, sleep_delay, sensor_store):
        threading.Thread.__init__(self)
        self.sensor = sensor
        self.sleep_delay = sleep_delay
        self.sensor_store = sensor_store
        self.shutdown = False
        
    def run ( self ):
        while True:
            reading = self.sensor_store.get_latest_float_reading(self.sensor)
            if reading is None:
                print "No reading available"
            else:
                print "Reading is {} at {}".format(reading[1], datetime.datetime.utcfromtimestamp(reading[0]).strftime('%Y %m %d %H %M %S'))
            time.sleep(self.sleep_delay)
            
            if self.shutdown:
                print "Shutting down updater thread!"
                return None


store = SensorStore()
sensor_name = "thermometer"
therm = store.get_sensor(sensor_name)
if therm is None:
    print "Creating sensor"
    store.create_sensor(sensor_name, "C")
    therm = store.get_sensor(sensor_name)

try:
  thread1=SlowWriter(therm, 2, store)
  thread1.start()
  thread2=UpdateReader(therm, 2, store)
  thread2.start()
  while True:
      time.sleep(1)
except (KeyboardInterrupt, SystemExit):
  print '\n! Received keyboard interrupt, quitting threads.\n'
  thread1.shutdown = True
  thread1.join()
  thread2.shutdown = True
  thread2.join()
  print "Thread joined, exiting for real"


#latest = store.get_latest_float_reading(therm)
#print "Lastest result is {}", latest

#conn = sqlite3.connect('test.db')

#def get_sensor(name):
    
#def save_sensor_float_reading(sensor, value, time ):
    # insert sensor data

#    c = conn.cursor()
#    c.execute("insert into sensor_float_data(val, timestamp, sensor_id) values( ?, ?, ? )", (value, calendar.timegm(time.utctimetuple()), sensor))
#    conn.commit()

#save_sensor_float_reading(12, 13, datetime.datetime.utcnow())

#conn.close()
