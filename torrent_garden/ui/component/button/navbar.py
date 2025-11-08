from typing import Optional

import reflex as rx
from reflex import Component


class NavbarButton(rx.ComponentState):
    @rx.var
    def get_current_path(self) -> str:
        return self.router.url.path

    @classmethod
    def get_component(cls, *children, **props) -> Component:
        text: str = props.pop("text", "")
        href: str = props.pop("href", "")
        icon: Optional[str] = props.pop("icon", None)

        button_width = props.pop("width", None)

        return rx.link(
            rx.button(
                rx.cond(icon, rx.icon(icon)),
                rx.text(text),
                disabled=href == cls.get_current_path,
                width=button_width,
            ),
            href=href,
        )

navbar_button = NavbarButton.create
