#!/usr/bin/env python3

import sys
import json
import asyncio
from dbus_fast.aio import MessageBus
from dbus_fast import BusType

if len(sys.argv) < 3:
    print(json.dumps({"text": "Invalid args"}))
    sys.exit(1)

DEVICE_PATH = sys.argv[1]
ICON = sys.argv[2]


async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    introspection = await bus.introspect(
        "org.freedesktop.UPower",
        DEVICE_PATH
    )

    obj = bus.get_proxy_object(
        "org.freedesktop.UPower",
        DEVICE_PATH,
        introspection
    )

    props = obj.get_interface("org.freedesktop.DBus.Properties")

    async def print_status():
        variant = await props.call_get(
            "org.freedesktop.UPower.Device",
            "Percentage"
        )
        percentage = int(variant.value)

        print(json.dumps({
            "text": f"{ICON} {percentage}%"
        }), flush=True)

    await print_status()

    def properties_changed(interface_name, changed, invalidated):
        if interface_name != "org.freedesktop.UPower.Device":
            return

        if "Percentage" in changed:
            percentage = int(changed["Percentage"].value)

            print(json.dumps({
                "text": f"{ICON} {percentage}%"
            }), flush=True)

    props.on_properties_changed(properties_changed)

    # Keep running forever
    await asyncio.get_running_loop().create_future()


asyncio.run(main())

