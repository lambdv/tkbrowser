import requests
from bs4 import BeautifulSoup, Tag
from tkinter import ttk
from urllib.parse import urljoin

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def fetch_url(url):
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response, None
    except requests.exceptions.RequestException as e:
        return None, str(e)


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup


def render_element(element, parent, on_link=None, base_url=None, depth=0):
    if not isinstance(element, Tag):
        return

    tag = element.name

    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        sizes = {
            "h1": ("", 22, "bold"), "h2": ("", 18, "bold"), "h3": ("", 16, "bold"),
            "h4": ("", 14, "bold"), "h5": ("", 12, "bold"), "h6": ("", 11, "bold"),
        }
        text = element.get_text().strip()
        if text:
            ttk.Label(parent, text=text, font=sizes[tag]).grid(
                sticky="w", pady=(10, 4)
            )

    elif tag == "p":
        text = element.get_text().strip()
        if text:
            ttk.Label(parent, text=text, wraplength=800).grid(
                sticky="w", pady=2
            )

    elif tag == "a":
        href = element.get("href", "")
        text = element.get_text().strip()
        if text:
            label = ttk.Label(
                parent, text=text, foreground="#0000ee", cursor="hand2"
            )
            label.grid(sticky="w", pady=2)
            if href and on_link:
                full = urljoin(base_url, href) if base_url else href
                label.bind("<Button-1>", lambda e, url=full: on_link(url))

    elif tag == "img":
        alt = element.get("alt", "") or element.get("src", "")
        ttk.Label(parent, text=f"[Image: {alt}]", foreground="gray").grid(
            sticky="w", pady=2
        )

    elif tag in ("ul", "ol"):
        for child in element.children:
            if isinstance(child, Tag) and child.name == "li":
                render_element(child, parent, on_link, base_url, depth + 1)

    elif tag == "li":
        bullet = "\u2022" if depth % 2 == 0 else "\u25e6"
        text = element.get_text().strip()
        if text:
            ttk.Label(parent, text=f"  {bullet} {text}", wraplength=780).grid(
                sticky="w", pady=1
            )

    elif tag == "br":
        ttk.Label(parent, text="").grid()

    elif tag in ("b", "strong"):
        text = element.get_text().strip()
        if text:
            ttk.Label(parent, text=text, font=("", 10, "bold")).grid(
                sticky="w", pady=1
            )

    elif tag in ("i", "em"):
        text = element.get_text().strip()
        if text:
            ttk.Label(parent, text=text, font=("", 10, "italic")).grid(
                sticky="w", pady=1
            )

    elif tag == "blockquote":
        text = element.get_text().strip()
        if text:
            frame = ttk.Frame(parent)
            frame.grid(sticky="ew", pady=4)
            ttk.Label(
                frame, text=text, wraplength=760, foreground="#555"
            ).grid(sticky="w", padx=(20, 0))

    elif tag in ("pre", "code"):
        text = element.get_text()
        ttk.Label(
            parent, text=text, font=("Courier", 9), wraplength=800
        ).grid(sticky="w", pady=2)

    elif tag == "hr":
        ttk.Separator(parent, orient="horizontal").grid(sticky="ew", pady=8)

    elif tag in (
        "div", "span", "body", "html", "head", "header", "main",
        "section", "article", "nav", "footer", "form", "figure",
        "figcaption", "table", "thead", "tbody", "tfoot", "tr",
        "td", "th", "dl", "dt", "dd",
    ):
        for child in element.children:
            render_element(child, parent, on_link, base_url, depth)


def show_error(view_port, message):
    for widget in view_port.winfo_children():
        widget.destroy()
    ttk.Label(
        view_port, text=message, foreground="red", wraplength=800
    ).grid(sticky="w")
