import asyncio
import colorsys
import copy
import dataclasses
import random
from importlib.resources import files
from typing import Any, Callable, Dict, Tuple

import asyncio_for_robotics
import sdl2
import sdl2.ext
from asyncio_for_robotics.core.sub import BaseSub


def scancode_to_color(scancode: int) -> Tuple[int, int, int]:
    if scancode == 0:
        return 255, 0, 0
    brightness = 255
    r, g, b = colorsys.hsv_to_rgb((scancode % 30) / 30, 0.5, 1)
    return int(r * brightness), int(g * brightness), int(b * brightness)


@dataclasses.dataclass(frozen=True)
class Key:
    symbol: str
    code: int
    modifiers: int
    is_pressed: bool
    sdl_event: sdl2.SDL_KeyboardEvent

    @classmethod
    def from_sdl(cls, sdl_event: sdl2.SDL_KeyboardEvent) -> "Key":
        return cls(
            symbol=sdl2.SDL_GetKeyName(sdl_event.keysym.sym).decode(),
            code=sdl_event.keysym.scancode,
            modifiers=sdl_event.keysym.mod,
            is_pressed=bool(sdl_event.state),
            sdl_event=sdl_event,
        )


def raise_keyboard_interupt():
    raise KeyboardInterrupt


class KeySub(BaseSub[Key]):
    def __init__(
        self,
        termination_callback: Callable[[], Any] = raise_keyboard_interupt,
    ) -> None:
        """Creates a sdl2 window with an asyncio_for_robotics subcriber getting
        the key presses inputed in the window.

        Args:
            termination_callback: Will be called when the Gorilla window is
                closed by the user.
        """
        self.termination_callback: Callable[[], Any] = termination_callback
        r, g, b = colorsys.hsv_to_rgb(random.random(), (random.random() + 1) / 2, 1)
        self.idle_color: Tuple[int, int, int] = int(r * 255), int(g * 255), int(b * 255)

        self._pressed_keys: Dict[int, Key] = dict()
        self._surface_icon = sdl2.ext.load_img(
            str(files("gogo_keyboard").joinpath("icons/gogo.png"))
        )
        super().__init__()
        self.window: sdl2.ext.Window
        self.renderer: sdl2.ext.Renderer
        self._init_sdl()
        self._sdl_thread: asyncio.Task = asyncio.create_task(self._sdl_loop())

        print(str(files("gogo_keyboard").joinpath("gogo.png")))
        self.texture_idle = sdl2.SDL_CreateTextureFromSurface(
            self.renderer.sdlrenderer,
            sdl2.ext.load_img(
                str(files("gogo_keyboard").joinpath("icons/gogo.png")),
            ),
        )
        self.texture_loop = [
            sdl2.SDL_CreateTextureFromSurface(
                self.renderer.sdlrenderer,
                sdl2.ext.load_img(
                    str(files("gogo_keyboard").joinpath("icons/gogo_happy.png"))
                ),
            ),
            sdl2.SDL_CreateTextureFromSurface(
                self.renderer.sdlrenderer,
                sdl2.ext.load_img(
                    str(files("gogo_keyboard").joinpath("icons/gogo_happy2.png"))
                ),
            ),
        ]
        self.tex_ind: int = 0
        self._draw()
        self.renderer.present()

    @property
    def pressed_keys(self) -> Dict[int, Key]:
        return copy.deepcopy(self._pressed_keys)

    @property
    def name(self) -> str:
        return "Gorillinput"

    def close(self):
        self.window.close()
        sdl2.ext.quit()
        self._sdl_thread.cancel()

    def _scancode_to_color(self, scancode):
        return scancode_to_color(scancode)

    def _init_sdl(self):
        sdl2.ext.init()
        self.window = sdl2.ext.Window(
            "Input",
            size=(150, 150),
            # flags=sdl2.SDL_WINDOW_RESIZABLE, # icon disapears if used
        )
        sdl2.SDL_SetWindowIcon(self.window.window, self._surface_icon)
        self.renderer = sdl2.ext.Renderer(self.window)
        self.window.show()
        self.texture_frame = sdl2.SDL_Rect(0, 0, 150, 150)  # x, y, width, height

    def _on_window_close(self):
        self.close()
        self.termination_callback()

    def _draw(self):
        self.renderer.color = (
            self._scancode_to_color(list(self._pressed_keys.keys())[-1])
            if len(self._pressed_keys) > 0
            else self.idle_color
        )
        self.renderer.clear()
        if len(self._pressed_keys) > 0 and self.texture_loop != []:
            self.tex_ind = (self.tex_ind + 1) % len(self.texture_loop)
            sdl2.SDL_RenderCopy(
                self.renderer.sdlrenderer,
                self.texture_loop[self.tex_ind],
                None,
                self.texture_frame,
            )
        else:
            sdl2.SDL_RenderCopy(
                self.renderer.sdlrenderer, self.texture_idle, None, self.texture_frame
            )

    async def _sdl_loop(self):
        async for t in asyncio_for_robotics.Rate(30).listen():
            events = sdl2.ext.get_events()
            for e in events:
                if e.type == sdl2.SDL_QUIT:

                    self._on_window_close()
                    return

                elif e.type == sdl2.SDL_KEYDOWN:
                    if e.key.repeat:
                        continue
                    k = Key.from_sdl(e.key)
                    self.input_data(k)
                    self._pressed_keys[k.code] = k

                elif e.type == sdl2.SDL_KEYUP:
                    k = Key.from_sdl(e.key)
                    self.input_data(k)
                    del self._pressed_keys[k.code]

                elif e.type in [
                    sdl2.SDL_WINDOWEVENT,
                ]:
                    sdl2.SDL_SetWindowIcon(self.window.window, self._surface_icon)
                    self.window.show()
                    if e.window.event in [
                        sdl2.SDL_WINDOWEVENT_SIZE_CHANGED,
                        sdl2.SDL_WINDOWEVENT_RESIZED,
                    ]:
                        pass  # continues to update the window to new size
                    else:
                        continue  # does nothing
                else:
                    continue  # does nothing
                self._draw()
                self.renderer.present()
