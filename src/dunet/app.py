from httpx import URL
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Input
from textual_html import HTML


class DunetApp(App):
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Input("http://example.com/", placeholder="Enter web address")
        yield HTML(use_readability=True)
        yield Footer()

    @on(Input.Submitted)
    def _on_input_submitted(self, event: Input.Submitted) -> None:
        event.input.blur()

        html = self.query_one(HTML)
        html.load(URL(event.value))


if __name__ == "__main__":
    app = DunetApp()
    app.run()
