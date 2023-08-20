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

    browsing_history = BrowsingHistory()

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
        if (
            self.browsing_history.current_url is None
            or event.value != self.browsing_history.current_url.url
        ):
            self.browsing_history.add_new_url(event.value)

    @on(HTML.LinkClicked)
    def on_html_link_clicked(self, event: HTML.LinkClicked) -> None:
        event.html.load_url(event.href)
        self.query_one(Input).value = event.href
        assert self.browsing_history.current_url is not None
        if event.href != self.browsing_history.current_url.url:
            self.browsing_history.add_new_url(event.href)


if __name__ == "__main__":
    app = DunetApp()
    app.run()
