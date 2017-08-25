#!/usr/bin/env python3

import datetime
import code
import serial
import asyncio
import binascii
import struct
import time
import logging
import warnings

from commands import Commands

if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

def warn_untested(fn):
    def _warn_wrap(*args, **kwargs):
        warnings.warn(f"{fn.__name__} untested!")
        fn(*args, **kwargs)
    return _warn_wrap

def warn_seems_broken(fn):
    def _warn_wrap(*args, **kwargs):
        warnings.warn(f"{fn.__name__} seems broken...")
        fn(*args, **kwargs)
    return _warn_wrap


class GM:

    def __init__(self, port):
        self.serial = serial.Serial(port=port,
                                    baudrate=57600,
                                    timeout=1.0)

    def get_serial(self):
        self.serial.write(Commands.get_serial)
        serblob = self.serial.read(7)
        return binascii.hexlify(serblob).decode('ascii')

    def get_version(self):
        self.serial.write(Commands.get_version)
        return self.serial.read(14).decode('ascii')

    def get_voltage(self):
        self.serial.write(Commands.get_voltage)
        return ord(self.serial.read(1)) / 10.0

    @staticmethod
    def cp_calc(data):
        return struct.unpack("h", data)[0] & 0x3f00

    def get_cpm(self):
        self.serial.write(Commands.get_cpm)
        return self.read_cps()

    def get_cps(self):
        self.serial.write(Commands.get_cps)
        return self.read_cps()

    def auto_cps_on(self):
        self.serial.write(Commands.auto_cps_on)

    def auto_cps_off(self):
        self.serial.write(Commands.auto_cps_off)

    def read_cps(self):
        return self.cp_calc(self.serial.read(2))

    def get_datetime(self):
        self.serial.write(Commands.get_datetime)
        data = self.serial.read(7)
        print(len(data), binascii.hexlify(data))
        # assert data[6] == 0xAA
        return datetime.datetime((2000+data[0]), *data[1:5])

    def power_off(self):
        self.serial.write(Commands.power_off)

    def power_on(self):
        self.serial.write(Commands.power_on)

    def reboot(self):
        self.serial.write(Commands.reboot)

    def test(self):
        print(f"serial: {self.get_serial()}")
        print(f"version: {self.get_version()}")
        print(f"voltage: {self.get_voltage()}V")
        print(f"cpm: {self.get_cpm()}")
        print(f"cps: {self.get_cps()}")
        print(f"datetime: {self.get_datetime()}")

    def test_autocps(self):
        with self.auto_cps(count=5) as cps:
            for reading in cps:
                print(f"autocps: {reading}")

    class AutoCPS:
        def __init__(self, device, count=None):
            self.device = device
            self.remaining = count

        def __iter__(self):
            return self

        def __enter__(self):
            self.device.auto_cps_on()
            return self

        def __exit__(self, typ, value, tb):
            self.device.auto_cps_off()

        def __next__(self):
            if self.remaining is not None:
                if not self.remaining:
                    raise StopIteration()
                self.remaining -= 1
            return self.device.read_cps()

    def auto_cps(self, count=None):
        return self.AutoCPS(self, count=count)

    FULL_USER_SIZE = 65536
    PAGE_SIZE = 2048
    @warn_seems_broken
    def fetch_page(self, num, size=PAGE_SIZE):
        offset = num * size
        offset_b = struct.pack(">I", offset)[1:]
        # bug: request A-1 when want A
        size_b = struct.pack(">H", size - 1)
        cmd = Commands.build_userdata_read(offset_b, size_b)
        if self.serial.in_waiting:
            self.serial.reset_input_buffer()
        self.serial.write(cmd)
        return self.serial.read(size)

    @warn_seems_broken
    def fetch_pages(self, num=None, size=None):
        if size is None:
            size = self.PAGE_SIZE
        if num is None:
            num = self.FULL_USER_SIZE // size
        ret = b""
        for n in range(num):
            while True:
                b = self.fetch_page(n, size)
                print(n, len(b), len(b) - size)
                if len(b) < size:
                    self.serial.reset_input_buffer()
                    self.serial.reset_output_buffer()
                else:
                    break
            ret += b
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        return ret

    @warn_seems_broken
    def gen_history_records(self, data=None):
        if data is None:
            data = self.fetch_pages()
        # remove after-data bits
        ham = data.rstrip(b"\xff")
        records = ham.split(b"\x55\xaa")
        # now, each record is:
        # 0x00 date
        # 0x01 data

        basedate = None
        interval = None
        duration = None
        for record in records:
            print(len(record), binascii.hexlify(record))
            if not record:
                continue
            elif record[0] == b"\x00" and not basedate:
                basedate = datetime.datetime(
                    # HAVE WE LEARNED NOTHING!?
                    year=(2000 + record[1]),
                    month=record[2],
                    day=record[3],
                    hour=record[4],
                    minute=record[5],
                    second=record[6]
                )
            elif basedate:
                # fuckin' math(s)
                # 1 - per second
                # 60 - per minute
                # 3600 - per hour
                interval = 60 ** (record[0] - 1)
                duration = datetime.timedelta(seconds=interval)
                for i in range(1, len(record), 2):
                    sample = record[i:i+2]
                    cpx = self.cp_calc(sample)
                    time_at = basedate + (i//2) * duration
                    yield cpx, time_at
            else:
                print(f"??? {record}")

    @warn_untested
    def get_cfg(self):
        self.serial.write(Commands.get_cfg)
        return self.serial.read(256)

# hint: device = GM('/dev/ttyUSB0')
#       device.test()

code.interact(local=dict(globals(), **locals()))
