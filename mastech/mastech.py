from __future__ import unicode_literals
import logging
import threading
from binascii import hexlify

try:
    from queue import Queue, Full
except ImportError:
    from Queue import Queue, Full

import pendulum
from bluepy import btle
from bitstring import BitArray


def _get_bit(src, index):
    return (src >> index) & 1 == 1


class Mastech(threading.Thread):
    # MEASUREMENT_CHARACTERISTIC_UUID = '0000ffb2-0000-1000-8000-00805f9b34fb'
    MEASUREMENT_CHARACTERISTIC = 0x14
    MEASUREMENT_NOTIFICATION_DESCRIPTOR = 0x16

    class Delegate(btle.DefaultDelegate):
        def __init__(self, mastech):
            super(Mastech.Delegate, self).__init__()
            self.mastech = mastech

        def handleNotification(self, cHandle, data):
            timestamp = pendulum.now()
            data = bytearray(data)
            # Based on the decompiled binary of Mastech APK
            # Look for LCDSegment.java ;)
            try:
                value = list(hexlify(data[10:8:-1]).decode('utf-8'))

                if value != ['f', 'f', 'f', 'f']:
                    if _get_bit(data[11], 6):
                        value.insert(-3, '.')
                    if _get_bit(data[11], 5):
                        value.insert(-2, '.')
                    if _get_bit(data[11], 4):
                        value.insert(-1, '.')
                    value = float(''.join(value))
                else:
                    value = float('inf')

                if _get_bit(data[11], 7):
                    value *= -1

                value_max = _get_bit(data[11], 3)
                value_min = _get_bit(data[11], 2)
                value_minmax = _get_bit(data[11], 1)
                auto_range = _get_bit(data[11], 0)

                low_battery = _get_bit(data[12], 7)
                diode = _get_bit(data[12], 6)
                speaker = _get_bit(data[12], 5)
                f5n = _get_bit(data[12], 4)
                u1 = _get_bit(data[12], 3)
                m1 = _get_bit(data[12], 2)
                f2F = _get_bit(data[12], 1)
                f1A = _get_bit(data[12], 0)

                dc = _get_bit(data[13], 7)
                ac = _get_bit(data[13], 6)
                f4V = _get_bit(data[13], 5)
                k1 = _get_bit(data[13], 4)
                f3M = _get_bit(data[13], 3)
                res = _get_bit(data[13], 2)
                Hz = _get_bit(data[13], 1)
                percent = _get_bit(data[13], 0)

                hold = _get_bit(data[14], 7)
                ncv_non_contact_voltage_detection = _get_bit(data[14], 6)
                C0 = _get_bit(data[14], 5)
                F0 = _get_bit(data[14], 4)
                usb = _get_bit(data[14], 3)
                REL = _get_bit(data[14], 2)
                apo = _get_bit(data[14], 1)
                hFE = _get_bit(data[14], 0)

                unit = ''

                if f5n:
                    value /= 1e9
                if u1:
                    value /= 1e6
                if m1:
                    value /= 1e3
                if k1:
                    value *= 1e3
                if f3M:
                    value *= 1e6

                if f4V:
                    unit += 'V'
                if f1A:
                    unit += 'A'
                if dc:
                    unit += 'dc'
                if ac:
                    unit += 'ac'
                if res:
                    unit += 'Ω'
                if Hz:
                    unit += 'Hz'
                if C0:
                    unit += '°C'
                if F0:
                    unit += '°F'
                if percent:
                    unit += '%'

                # print(value, unit)
                try:
                    self.mastech.log.debug(
                        '%s - Got measurement %.3f %s' % (
                            timestamp.isoformat(),
                            value,
                            unit
                        )
                    )
                    self.mastech.measurement_queue.put(
                        (timestamp, value, unit),
                        block=False
                    )
                except Full:
                    self.mastech.log.error('Measurement queue is full')

            except:
                self.mastech.log.exception('Exception in parsing message')

    def __init__(self, address, interface_index=0):
        super(Mastech, self).__init__()
        self.address = address
        self.interface_index = 0
        self.__stop = threading.Event()
        self.log = logging.getLogger(self.__class__.__name__)
        self.measurement_queue = Queue()

    def run(self):
        self.log.info('Starting to listen Mastech meter %s' % (self.address))
        peripheral = btle.Peripheral(self.address, iface=self.interface_index)
        peripheral.setDelegate(self.Delegate(self))
        peripheral.writeCharacteristic(
            self.MEASUREMENT_NOTIFICATION_DESCRIPTOR,
            bytearray([0x01, 0x00])
        )
        while not self.__stop.is_set():
            peripheral.waitForNotifications(1.0)
        peripheral.writeCharacteristic(
            self.MEASUREMENT_NOTIFICATION_DESCRIPTOR,
            bytearray([0x00, 0x00])
        )
        self.log.info('Stopped listening')

    def stop(self):
        self.__stop.set()

    @classmethod
    def discover(cls, interface_index=0, timeout=10):
        for device in btle.Scanner(interface_index).scan(timeout=timeout):
            if device.getValueText(9) == 'bde spp dev':
                yield device.addr
