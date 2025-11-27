# Gogo Keyboard
## Press keyboard 🦍 Get key 🦍  Unga Bunga

Python Asyncio library to simply get keyboard presses (up and down). Gogo Keyboard creates a new independent SDL2 window that captures the key presses. And it also works with ROS 2.

```python3
pip install https://github.com/2lian/gogo_keyboard.git[dll]
python3 -m gogo_keyboard.example
```

Motivation:
- Nothing complicated. Safe.
- Get key presses in Asyncio.
- Leave the python terminal free for other tasks.
- User only interacts when clicking on the Gorilla.
- Works with if necessary ROS 2.

| ![python](./media/Screenshot1.png) | ![python](./media/Screenshot2.png) | ![python](./media/Screenshot3.png) |
|---|---|---|

## Installation

This library requires `sdl2` and `sdl2_image`. By specifying the `dll` optional dependency, those will be installed by pip.

```python3
pip install gogo_keyboard[dll]
```

Conda pacakge: soon!

## Python Example

Example is [provided here](./src/gogo_keyboard/example.py) and can be run with `python3 -m gogo_keyboard.example`.

Here is a minimal piece of code:

```python
import asyncio
from gogo_keyboard.keyboard import KeySub

async def async_main():
    key_sub = KeySub()
    async for key in key_sub.listen_reliable():
        print(key)

asyncio.run(async_main())
```

## ROS 2 Example (Humble, Jazzy, Kilted)

A very simple ROS 2 node is [provided here](./src/gogo_keyboard/ros_node.py) and can be run with `python3 -m gogo_keyboard.ros_node`. You can listen to its output using `ros2 topic echo /key_press`. The messages format is a `json` formatted `String`, 🦍 simple 🦍  Unga Bunga.
