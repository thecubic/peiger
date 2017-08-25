#!/usr/bin/env python3

class Commands:
    get_serial    = b"<GETSERIAL>>"
    get_version   = b"<GETVER>>"
    get_voltage   = b"<GETVOLT>>"
    get_cpm       = b"<GETCPM>>"
    get_cps       = b"<GETCPS>>"
    get_cfg       = b"<GETCFG>>"
    erase_cfg     = b"<ECFG>>"
    update_cfg    = b"<CFGUPDATE>>"
    auto_cps_on   = b"<HEARTBEAT1>>"
    auto_cps_off  = b"<HEARTBEAT0>>"
    power_off     = b"<POWEROFF>>"
    power_on      = b"<POWERON>>"
    reboot        = b"<REBOOT>>"
    get_datetime  = b"<GETDATETIME>>"
    get_temp      = b"<GETTEMP>>"
    factoryreset  = b"<FACTORYRESET>>"
    key_S1        = b"<key0>>"
    key_S2        = b"<key1>>"
    key_S3        = b"<key2>>"
    key_S4        = b"<key3>>"

    @staticmethod
    def build_set_date_year(year):
        return b"<SETDATEYY"

    @staticmethod
    def build_set_date_month(month):
        return b"<SETDATEMM"

    @staticmethod
    def build_set_date_day(day):
        return b"<SETDATEDD"

    @staticmethod
    def build_set_time_hour(hour):
        return b"<SETTIMEHH"

    @staticmethod
    def build_set_time_minute(minute):
        return b"<SETTIMEMM"

    @staticmethod
    def build_set_time_second(second):
        return b"<SETTIMESS"

    @staticmethod
    def build_set_datetime(datetime):
        return b"<SETDATETIME"

    @staticmethod
    def build_userdata_read(offset_b, size_b):
        return b"<SPIR" + offset_b + size_b + b">>"
