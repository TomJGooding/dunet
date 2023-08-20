from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Footer, Input
from textual_html import HTML


class AddressBar(Input):
    def __init__(self, value: str | None = None) -> None:
        super().__init__(value, placeholder="Enter web address")


class NavigationBar(Widget):
    DEFAULT_CSS = """
    NavigationBar {
        dock: top;
        width: 100%;
        height: auto;
        background: $panel;
        border: hkey $background;
    }

    NavigationBar Horizontal {
        height: auto;
    }

    NavigationBar Button {
        min-width: 5;
        margin: 0 1;
    }

    NavigationBar AddressBar {
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Button("\u2190", id="back-btn", disabled=True)
            yield Button("\u2192", id="forward-btn", disabled=True)
            yield Button("\u21BB", id="reload-btn")
            yield AddressBar()


class DunetApp(App):
    BINDINGS = [("ctrl+q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield NavigationBar()
        with VerticalScroll():
            yield HTML(use_readability=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(AddressBar).focus()

    @on(AddressBar.Submitted)
    def on_address_bar_submitted(self, event: AddressBar.Submitted) -> None:
        if not event.value:
            return
        html = self.query_one(HTML)
        html.load_url(event.value)
        self.query_one(VerticalScroll).focus()

    @on(HTML.LinkClicked)
    def on_html_link_clicked(self, event: HTML.LinkClicked) -> None:
        event.html.load_url(event.href)
        self.query_one(Input).value = event.href


if __name__ == "__main__":
    app = DunetApp()
    app.run()
