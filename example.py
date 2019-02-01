import time
from mastech import Mastech


# Callback function for the measurements
def callback(timestamp, value, unit):
    print('%s - %.3f %s' % (timestamp.isoformat(), value, unit))


# Search for device
device_address = None
# Loop the search while a device is not found
while device_address is None:
    print('Searching for Mastech...')
    # Get first found device
    device_address = next(Mastech.discover(timeout=1.0), None)

print('Found Mastech at address %s' % (device_address))

# Initialize Mastech instance
m = Mastech(device_address, callback=callback)
print('Starting measurement')
# Start the measurement loop
m.start()

try:
    # Sleep for 999999999 seconds, the measurement loop takes over...
    time.sleep(999999999)
except KeyboardInterrupt:
    pass
finally:
    # Stop the measurement
    print('Stopping measurement')
    m.stop()
