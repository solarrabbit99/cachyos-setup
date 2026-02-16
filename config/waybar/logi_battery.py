#!/usr/bin/env python3
import hid
import json
import sys
import argparse

HIDPP_REPORT_ID_SHORT = 0x10
HIDPP_REPORT_ID = 0x11
HIDPP_RECEIVER_ID = 0xFF
HIDPP_BATTERY_FEATURE_ID = 0x06
HIDPP_BATTERY_LEVEL_ID = 0x11
MAX_PACKET_SIZE = 64

# refer to https://github.com/pwr-Solaar/Solaar/blob/master/lib/logitech_receiver/hidpp20.py#L1992
def estimate_battery_level_percentage(value_millivolt: int) -> int | None:
    battery_voltage_to_percentage = [
        (4186, 100),
        (4067, 90),
        (3989, 80),
        (3922, 70),
        (3859, 60),
        (3811, 50),
        (3778, 40),
        (3751, 30),
        (3717, 20),
        (3671, 10),
        (3646, 5),
        (3579, 2),
        (3500, 0),
    ]

    if value_millivolt >= battery_voltage_to_percentage[0][0]:
        return battery_voltage_to_percentage[0][1]

    if value_millivolt <= battery_voltage_to_percentage[-1][0]:
        return battery_voltage_to_percentage[-1][1]

    for i in range(len(battery_voltage_to_percentage) - 1):
        v_high, p_high = battery_voltage_to_percentage[i]
        v_low, p_low = battery_voltage_to_percentage[i + 1]

        if v_low <= value_millivolt <= v_high:
            percent = p_low + (
                (p_high - p_low)
                * (value_millivolt - v_low)
                / (v_high - v_low)
            )
            return round(percent)

    return None

def request_feature(handle, report_id, feature_id, function_id = 0x00):
    handle.write([report_id, HIDPP_RECEIVER_ID, feature_id, function_id] + [0x00] * 3)
    buf = []
    while len(buf) == 0 or buf[0] != HIDPP_REPORT_ID:
        buf = handle.read(MAX_PACKET_SIZE, 100) # 100ms timeout
    return buf[4:]

def main():
    parser = argparse.ArgumentParser(prog='Logitech Battery Fetcher',
                                     description='Fetches Logitech devices\' battery status (mainly for waybar)',
                                     usage=f'{sys.argv[0]} vendor_id product_id')
    parser.add_argument('vendor_id', help='first part of usbid')
    parser.add_argument('product_id', help='wpid or second part of usbid')
    parser.add_argument('-r', '--receiver', help='query receiver itself and not its subproducts', action='store_true', default=False)
    args = parser.parse_args()

    vendor_id = int(args.vendor_id, 16)
    product_id = int(args.product_id, 16)
    handle = hid.device()
    for device in hid.enumerate():
        if device['vendor_id'] == vendor_id and device['product_id'] == product_id:
            handle.open_path(device['path'])
            break
    if args.receiver:
        buf = request_feature(handle, HIDPP_REPORT_ID, HIDPP_BATTERY_FEATURE_ID)
        batt_level = estimate_battery_level_percentage((buf[0] << 8) + buf[1])
    else:
        buf = request_feature(handle, HIDPP_REPORT_ID, HIDPP_BATTERY_FEATURE_ID, HIDPP_BATTERY_LEVEL_ID)
        batt_level = buf[0]

    battery_text = f"{batt_level}%" if batt_level else "Off"
    output = {"text": battery_text,
              "tooltip": handle.get_product_string()}
    sys.stdout.write(json.dumps(output) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
