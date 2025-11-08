import reflex as rx


class PageRootState(rx.State):
    @rx.event
    def on_load(self):
        yield rx.redirect("/browse")
