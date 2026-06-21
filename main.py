from tkinter import *
from tkinter import ttk

import requests
from bs4 import BeautifulSoup, Tag

HISTORY = []


# logic handlers
def search(event=None):
    url = search_bar.get()
    if url.strip() == "":
        return
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    if not response.ok:
        # contentLabel.config(text=response.text)
        return
    if "text/html" in response.headers.get("Content-Type", ""):
        for widget in container.winfo_children():
            widget.destroy()
        parse(response.content)


def parse(htmltext):
    soup = BeautifulSoup(htmltext, "html.parser")
    print("parsing")
    handle(soup.html)
    print("parsing end")


def handle(element, depth=0):
    if not isinstance(element, Tag):
        return

    if element.name == "p":
        ttk.Label(view_port, text=element.get_text()).grid()

    for child in element.children:
        handle(child, depth + 1)


# components
def build_tab_bar(parentFrame):
    tab_bar = ttk.Frame(parentFrame)
    tab_bar.grid(row=0, column=0, sticky="nsew")

    tab_bar.columnconfigure(0, weight=1)
    tab_bar.columnconfigure(1, weight=1)

    tab_button = ttk.Button(tab_bar, text="New Tab")
    tab_button.grid(row=0, column=0, sticky="nsew", padx=2)

    tab_button = ttk.Button(tab_bar, text="+")
    tab_button.grid(row=0, column=1, sticky="nsew", padx=0)
    return tab_bar


# page controls, search bar
def build_page_controls(parent):
    # Top navigation bar
    container = ttk.Frame(parent, padding=10)
    container.grid(row=0, column=0, sticky="ew")

    # Make the search bar expand
    container.columnconfigure(1, weight=1)

    # Title
    ttk.Label(container, text="Browser").grid(
        row=0,
        column=0,
        padx=(0, 8),
    )

    # Search entry
    search_bar = ttk.Entry(container)
    search_bar.grid(
        row=0,
        column=1,
        sticky="ew",
        padx=(0, 8),
        ipady=3,
    )

    search_bar.bind("<Return>", search)

    # Search button
    ttk.Button(
        container,
        text="Search",
        command=search,
    ).grid(
        row=0,
        column=2,
    )
    return container


def build_browser_header(parent):
    (container) = build_tab_bar(parent)
    build_page_controls(parent)
    return container


# window
def build_window():
    root = Tk()
    root.title("Browser")
    root.geometry("1980x1080")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # menu
    menu = Menu(root)
    root.config(menu=menu)
    file_menu = Menu(menu, tearoff=False)
    menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New")
    file_menu.add_command(label="Open...")
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    return (root, menu)


def build_viewport(parent):
    # view port
    view_port = ttk.Frame(parent, padding=10)
    contentLabel = ttk.Label(view_port, text="Content")
    contentLabel.grid(row=0, column=0)

    view_port.grid(row=2, column=0, sticky="nsew")
    return view_port


# main
(root, menu) = build_window()
(containers) = build_browser_header(root)
(view_port) = build_viewport(root)
root.mainloop()
