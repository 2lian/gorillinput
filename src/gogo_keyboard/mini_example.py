import asyncio
from gogo_keyboard.keyboard import KeySub

async def async_main():
    key_sub = KeySub()
    async for key in key_sub.listen_reliable():
        print(key)

asyncio.run(async_main())
