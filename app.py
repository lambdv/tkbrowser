from dataclasses import dataclass
from tkinter import *
from tkinter import ttk

from logic import fetch_url, parse_html, render_element, show_error


@dataclass
class App:
    root: Tk
    menu: Menu
    # tab_bar: ttk.Frame
    search_bar: ttk.Entry
    view_port: ttk.Frame


def new():
    root = Tk()
    root.title("Browser")
    root.geometry("1200x800")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(2, weight=1)

    menu = _build_menu(root)
    # tab_bar = _build_tab_bar(root)
    view_port = _build_viewport(root)
    search_bar = _build_controls(root, view_port)

    return App(
        root=root,
        menu=menu,
        # tab_bar=tab_bar,
        search_bar=search_bar,
        view_port=view_port,
    )


def run(app):
    app.root.mainloop()


def _build_menu(root):
    menu = Menu(root)
    root.config(menu=menu)
    file_menu = Menu(menu, tearoff=False)
    menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New")
    file_menu.add_command(label="Open...")
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    return menu


# def _build_tab_bar(parent):
#     tab_bar = ttk.Frame(parent)
#     tab_bar.grid(row=0, column=0, sticky="nsew")
#     tab_bar.columnconfigure(0, weight=1)
#     tab_bar.columnconfigure(1, weight=1)

#     ttk.Button(tab_bar, text="New Tab").grid(row=0, column=0, sticky="nsew", padx=2)
#     ttk.Button(tab_bar, text="+").grid(row=0, column=1, sticky="nsew", padx=0)

#     return tab_bar


def _build_controls(parent, view_port):
    container = ttk.Frame(parent, padding=10)
    container.grid(row=1, column=0, sticky="ew")
    container.columnconfigure(4, weight=1)

    history = []
    history_pos = -1

    def update_nav_buttons():
        state = "normal" if history_pos > 0 else "disabled"
        back_btn.configure(state=state)
        state = "normal" if history_pos < len(history) - 1 else "disabled"
        forward_btn.configure(state=state)

    def navigate_to(url, add_to_history=True):
        nonlocal history_pos
        if not url.strip():
            return
        if add_to_history:
            if history_pos < len(history) - 1:
                del history[history_pos + 1 :]
            history.append(url)
            history_pos = len(history) - 1
        response, error = fetch_url(url)
        if error:
            print(f"[Browser Error] {error}")
            show_error(view_port, f"Request failed: {error}")
            return
        if not response.ok:
            msg = f"HTTP {response.status_code}: {response.reason}"
            print(f"[Browser Error] {msg}")
            show_error(view_port, msg)
            return
        if "text/html" in response.headers.get("Content-Type", ""):
            for widget in view_port.winfo_children():
                widget.destroy()
            soup = parse_html(response.content)
            render_element(soup.html, view_port, on_link=navigate_to, base_url=url)
        search_bar.delete(0, END)
        search_bar.insert(0, url)
        update_nav_buttons()

    def go_back():
        nonlocal history_pos
        if history_pos > 0:
            history_pos -= 1
            navigate_to(history[history_pos], add_to_history=False)

    def go_forward():
        nonlocal history_pos
        if history_pos < len(history) - 1:
            history_pos += 1
            navigate_to(history[history_pos], add_to_history=False)

    def refresh():
        if history:
            navigate_to(history[history_pos], add_to_history=False)

    back_btn = ttk.Button(container, text="back", width=10, command=go_back)
    back_btn.grid(row=0, column=0, padx=(0, 2))
    forward_btn = ttk.Button(container, text="forward", width=10, command=go_forward)
    forward_btn.grid(row=0, column=1, padx=(0, 2))
    refresh_btn = ttk.Button(container, text="refresh", width=10, command=refresh)
    refresh_btn.grid(row=0, column=2, padx=(0, 4))

    ttk.Label(container, text="Browser").grid(row=0, column=3, padx=(0, 8))

    search_bar = ttk.Entry(container)
    search_bar.grid(row=0, column=4, sticky="ew", padx=(0, 8), ipady=3)

    update_nav_buttons()

    def search(event=None):
        navigate_to(search_bar.get())

    search_bar.bind("<Return>", search)
    ttk.Button(container, text="Search", command=search).grid(row=0, column=5)

    return search_bar


def _build_viewport(parent):
    container = ttk.Frame(parent)
    container.grid(row=2, column=0, sticky="nsew")
    container.columnconfigure(0, weight=1)
    container.rowconfigure(0, weight=1)

    canvas = Canvas(container, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    inner = ttk.Frame(canvas)

    inner.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind("<MouseWheel>", _on_mousewheel)

    return inner
