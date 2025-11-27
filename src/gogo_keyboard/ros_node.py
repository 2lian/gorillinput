import asyncio
import json
from contextlib import suppress
from dataclasses import asdict

import rclpy
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

from gogo_keyboard.keyboard import Key, KeySub


def make_ros_msg(key: Key) -> String:
    dict_key = asdict(key)
    del dict_key["sdl_event"]
    return String(data=json.dumps(dict_key))


async def async_main():
    rclpy.init()
    node = rclpy.create_node("gogo_keyboard")
    pub = node.create_publisher(
        String,
        "key_press",
        QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_ALL,
            durability=DurabilityPolicy.VOLATILE,
        ),
    )
    key_sub = KeySub()
    try:
        async for key in key_sub.listen_reliable():
            msg = make_ros_msg(key)
            pub.publish(msg)
    finally:
        rclpy.shutdown()


def main():
    with suppress(
        asyncio.CancelledError, KeyboardInterrupt, rclpy._rclpy_pybind11.RCLError
    ):
        asyncio.run(async_main())


if __name__ == "__main__":
    main()
