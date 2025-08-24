import importlib.resources as res

import flet as ft


def configure_window_and_theme(page: ft.Page):
    page.window.center()
    page.title = "URL CUTTER"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.resizable = False
    page.adaptive = True
    page.window.width = 445
    page.window.height = 730
    page.window.title_bar_hidden = True
    page.window.frameless = False

    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme=ft.ColorScheme(primary=ft.Colors.RED))
    # Шрифт и картинка — оставляем как в исходнике
    font_path = res.files("urlcutter").joinpath("assets/fonts/rubik/Rubik-Medium.ttf")
    page.fonts = {"Rubik": str(font_path)}


def build_title_bar() -> tuple[ft.Row, ft.IconButton, ft.IconButton, ft.IconButton]:
    close_button = ft.IconButton(ft.Icons.CLOSE)
    info_button = ft.IconButton(ft.Icons.MENU)
    minimize_button = ft.IconButton(ft.Icons.REMOVE)
    drag_area = ft.WindowDragArea(ft.Container(height=50, width=1000), expand=True, maximizable=False)
    row = ft.Row(
        controls=[info_button, drag_area, minimize_button, close_button],
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return row, info_button, minimize_button, close_button


def build_header() -> ft.Column:
    img_path = res.files("urlcutter").joinpath("assets/img/icon scissors.png")
    image = ft.Image(  # путь оставлен как есть — при деплое проверь относительность
        src=str(img_path),
        width=150,
        height=150,
    )
    margin_img_txt = ft.Container(height=65, width=400)
    return ft.Column(
        controls=[
            image,
            margin_img_txt,
            ft.Text("URL CUTTER", font_family="Rubik", size=26, weight=ft.FontWeight.BOLD),
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=400,
        spacing=0,
    )


def build_inputs() -> tuple[ft.TextField, ft.TextField]:
    url_input_field = ft.TextField(
        label="Input long URL",
        label_style=ft.TextStyle(color="#EB244E"),
        height=50,
        width=350,
        suffix=ft.IconButton(icon=ft.Icons.CONTENT_PASTE),
        border_color="#EB244E",
    )
    short_url_field = ft.TextField(
        label="Short URL",
        label_style=ft.TextStyle(color="#EB244E"),
        read_only=True,
        height=60,
        width=350,
        border_color="#EB244E",
    )
    return url_input_field, short_url_field


def build_buttons() -> tuple[ft.Row, ft.ElevatedButton, ft.ElevatedButton, ft.ElevatedButton]:
    shorten_button = ft.ElevatedButton(
        "CUT",
        color=ft.Colors.WHITE,
        bgcolor="#EB244E",
        height=40,
        width=90,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            text_style=ft.TextStyle(font_family="Rubik", size=18),
        ),
    )
    copy_button = ft.ElevatedButton(
        content=ft.Icon(ft.Icons.CONTENT_COPY),
        color="#EB244E",
        height=40,
        width=80,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )
    clear_button = ft.ElevatedButton(
        "CLEAR",
        color="#EB244E",
        height=40,
        width=110,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            text_style=ft.TextStyle(font_family="Rubik", size=18),
        ),
    )
    left_container = ft.Column(controls=[shorten_button], width=90, alignment=ft.MainAxisAlignment.START)
    right_container = ft.Row(
        controls=[clear_button, copy_button],
        spacing=10,
        width=200,
        alignment=ft.MainAxisAlignment.END,
    )
    button_row = ft.Row(
        controls=[left_container, right_container],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=60,
        width=350,
    )
    return button_row, shorten_button, clear_button, copy_button


def build_footer() -> ft.Column:
    footer = ft.Text(
        "DEVELOPED BY CODEBIRD",
        color=ft.Colors.GREY_500,
        width=350,
        text_align=ft.TextAlign.CENTER,
    )
    return ft.Column(
        controls=[footer],
        alignment=ft.MainAxisAlignment.END,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


def compose_page(title_bar, header_col, url_input_field, short_url_field, button_row, footer_container) -> ft.Column:
    margin_top = ft.Container(height=100, width=400)
    margin_middle = ft.Container(height=25, width=400)
    margin_bottom = ft.Container(height=5, width=400)
    margin_bottom1 = ft.Container(height=5, width=400)

    content = ft.Column(
        controls=[
            title_bar,
            margin_top,
            header_col,
            margin_middle,
            url_input_field,
            short_url_field,
            button_row,
            margin_bottom,
            footer_container,
            margin_bottom1,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )
    return ft.Column(
        controls=[content],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
