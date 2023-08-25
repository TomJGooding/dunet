from __future__ import annotations

from dataclasses import dataclass

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Footer, Input
from textual_html import HTML


@dataclass
class URLNode:
    url: str
    next_url: URLNode | None = None
    prev_url: URLNode | None = None


class BrowsingHistory:
    def __init__(
        self,
        first_url: URLNode | None = None,
        current_url: URLNode | None = None,
    ) -> None:
        self.first_url = first_url
        self.current_url = current_url

    def add_new_url(self, url: str) -> None:
        new_url = URLNode(url)
        if self.first_url is None:
            self.first_url = new_url
        if self.current_url is not None:
            self.current_url.next_url = new_url
            new_url.prev_url = self.current_url

        self.current_url = new_url

    def go_back(self) -> URLNode | None:
        if self.current_url is None or self.current_url.prev_url is None:
            return None
        self.current_url = self.current_url.prev_url
        return self.current_url

    def go_forward(self) -> URLNode | None:
        if self.current_url is None or self.current_url.next_url is None:
            return None
        self.current_url = self.current_url.next_url
        return self.current_url


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
            yield Button("\u2190", id="back-btn")
            yield Button("\u2192", id="forward-btn")
            yield Button("\u21BB", id="reload-btn")
            yield AddressBar()


class DunetApp(App):
    BINDINGS = [("ctrl+q", "quit", "Quit")]

    browsing_history = BrowsingHistory()

    def compose(self) -> ComposeResult:
        yield NavigationBar()
        with VerticalScroll():
            yield HTML(use_readability=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(AddressBar).focus()
        self.update_navigation_buttons()

    def update_navigation_buttons(self) -> None:
        back_button = self.query_one("#back-btn", Button)
        forward_button = self.query_one("#forward-btn", Button)

        current_url = self.browsing_history.current_url
        if current_url is None:
            back_button.disabled = True
            forward_button.disabled = True
            # Workaround for https://github.com/Textualize/textual/issues/3130
            back_button.mouse_over = False
            forward_button.mouse_over = False
            return

        if current_url.prev_url is None:
            back_button.disabled = True
            # Workaround for https://github.com/Textualize/textual/issues/3130
            back_button.mouse_over = False
        else:
            back_button.disabled = False

        if current_url.next_url is None:
            forward_button.disabled = True
            # Workaround for https://github.com/Textualize/textual/issues/3130
            forward_button.mouse_over = False
        else:
            forward_button.disabled = False

        # back_button.disabled = current_url.prev_url is None
        # forward_button.disabled = current_url.next_url is None

    @on(AddressBar.Submitted)
    def on_address_bar_submitted(self, event: AddressBar.Submitted) -> None:
        if not event.value:
            return
        html = self.query_one(HTML)
        html.load_url(event.value)
        self.query_one(VerticalScroll).focus()

        if (
            self.browsing_history.current_url is None
            or event.value != self.browsing_history.current_url.url
        ):
            self.browsing_history.add_new_url(event.value)
            self.update_navigation_buttons()

    @on(HTML.LinkClicked)
    def on_html_link_clicked(self, event: HTML.LinkClicked) -> None:
        self.query_one(AddressBar).value = event.href
        event.html.load_url(event.href)
        self.query_one(VerticalScroll).focus()

        assert self.browsing_history.current_url is not None
        if event.href != self.browsing_history.current_url.url:
            self.browsing_history.add_new_url(event.href)
            self.update_navigation_buttons()

    @on(Button.Pressed, "#reload-btn")
    def on_reload_button_pressed(self) -> None:
        if self.browsing_history.current_url is not None:
            url = self.browsing_history.current_url.url
            self.query_one(AddressBar).value = url
            self.query_one(HTML).load_url(url)

    @on(Button.Pressed, "#back-btn")
    def on_back_button_pressed(self) -> None:
        prev_url: URLNode | None = self.browsing_history.go_back()
        if prev_url is None:
            return
        self.query_one(AddressBar).value = prev_url.url
        self.query_one(HTML).load_url(prev_url.url)
        self.update_navigation_buttons()

    @on(Button.Pressed, "#forward-btn")
    def on_forward_button_pressed(self) -> None:
        next_url: URLNode | None = self.browsing_history.go_forward()
        if next_url is None:
            return
        self.query_one(AddressBar).value = next_url.url
        self.query_one(HTML).load_url(next_url.url)
        self.update_navigation_buttons()


if __name__ == "__main__":
    app = DunetApp()
    app.run()
