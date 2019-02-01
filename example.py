import time
import logging
from mastech import Mastech

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('main')

# Search for device
device_address = None
# Loop the search while a device is not found
while device_address is None:
    logger.info('Searching for Mastech...')
    # Get first found device
    device_address = next(Mastech.discover(timeout=1.0), None)

logger.info('Found Mastech at address %s' % (device_address))

# Initialize Mastech instance
m = Mastech(device_address)
logger.info('Starting measurement')
# Start the measurement loop
m.start()

try:
    # Sleep for 999999999 seconds, the measurement loop takes over...
    time.sleep(999999999)
except KeyboardInterrupt:
    pass
finally:
    # Stop the measurement
    logger.info('Stopping measurement')
    m.stop()
