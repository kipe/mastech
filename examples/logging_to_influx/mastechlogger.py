from mastech import Mastech
from influxdb import InfluxDBClient


class MastechLogger(Mastech):
    def __init__(self, *args, **kwargs):
        super(MastechLogger, self).__init__(*args, **kwargs)
        self.influx = InfluxDBClient(host='127.0.0.99', database='mastech')
        if 'mastech' not in [x['name'] for x in self.influx.get_list_database()]:
            self.initial_setup()

    def initial_setup(self):
        import requests
        from requests.auth import HTTPBasicAuth

        import initial

        print('Running initial setup!')
        r = requests.post(
            'http://127.0.0.99:3000/api/datasources',
            auth=HTTPBasicAuth('admin', 'admin'),
            json=initial.DATASOURCE
        )
        try:
            r.raise_for_status()
        except Exception as e:
            print(r.content)
            raise

        # Create 'mastech' database
        self.influx.create_database('mastech')

    def callback(self, timestamp, value, unit):
        self.influx.write_points(
            [{
                'measurement': 'mastech',
                'time': timestamp,
                'fields': {
                    'value': value,
                },
            }],
            tags={
                'address': self.address,
                'unit': unit,
            }
        )


if __name__ == '__main__':
    import time

    # Search for device
    device_address = None
    # Loop the search while a device is not found
    while device_address is None:
        print('Searching for Mastech...')
        # Get first found device
        device_address = next(Mastech.discover(timeout=1.0), None)

    mastechlogger = MastechLogger(device_address)
    mastechlogger.start()

    while True:
        time.sleep(1)

    mastechlogger.stop()
