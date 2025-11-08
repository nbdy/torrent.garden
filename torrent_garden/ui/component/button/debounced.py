from asyncio import sleep
from typing import Optional

import reflex as rx
from reflex import Component


class DebouncedButton(rx.ComponentState):
    is_debounced: bool = False
    timeout: int = 5

    @rx.event(background=True)
    async def on_click(self):
        async with self:
            self.is_debounced = True
        while self.is_debounced:
            await sleep(self.timeout)
            async with self:
                self.is_debounced = False

    @classmethod
    def get_component(cls, *children, **props) -> Component:
        on_click = props.pop("on_click", None)

        timeout: Optional[int] = props.pop("timeout", None)
        if timeout is not None:
            cls.__fields__["timeout"].default = timeout

        return rx.button(
            *children,
            on_click=[
                cls.on_click,
                on_click,
            ],
            disabled=cls.is_debounced,
            loading=cls.is_debounced,
            **props,
        )


debounced_button = DebouncedButton.create
