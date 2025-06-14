import flet as ft
import pyshorteners
import pyshorteners.shorteners.tinyurl
import validators
import pyperclip
import webbrowser


def main(page: ft.Page):
    # Page Options (setting window size, alignment and theme)
    # Window center, size, and theme settings
    page.window.center()
    page.title = "URL CUTTER"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.resizable = False
    page.adaptive = True

    # Get the screen dimensions and set the window
    # based on the screen proportions
    page.window.width = 445
    page.window.height = 730
    page.window.title_bar_hidden = True
    page.window.frameless = False

    # Page design theme
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.RED,
            primary_container=ft.colors.RED_200
        ),
    )

    # Paste button handler
    def on_paste_click(e):
        pasted_text = pyperclip.paste()
        url_input_field.value = pasted_text
        page.update()

    # Function to shorten a long URL using pyshorteners
    # If a URL is entered, shorten it using the pyshorteners library
    def shorten_url():
        long_url = url_input_field.value
        if long_url.startswith("https://tinyurl.com"):
            snack_bar = ft.SnackBar(ft.Text("This is already a shortened URL."),
                                    bgcolor=ft.colors.BLACK,
                                    duration=1000)
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()
            return

        if long_url and validators.url(long_url):
            s = pyshorteners.Shortener()
            short_url = s.tinyurl.short(long_url)
            short_url_field.value = short_url
            page.update()
        else:
            # Display an error message or show the SnackBar
            snack_bar = ft.SnackBar(ft.Text("Incorrect URL, try again."),
                                    bgcolor=ft.colors.BLACK,
                                    duration=1000)
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()

    def clear_text(url):
        if url_input_field.value:
            url_input_field.value = ""
            url_input_field.update()
            page.update()
        else:
            snack_bar = ft.SnackBar(ft.Text("Nothing to clear!"),
                                    bgcolor=ft.colors.BLACK,
                                    duration=1000)
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()


    # Copy function to clipboard, displays a copy message
    def copy_to_clipboard(url):
        if short_url_field.value:
            page.set_clipboard(url)
            snack_bar = ft.SnackBar(ft.Text("Copied to clipboard!"),
                                    bgcolor=ft.colors.BLACK,
                                    duration=1000)
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()
        else:
            page.set_clipboard(url)
            snack_bar = ft.SnackBar(ft.Text("Nothing to copy!"),
                                    bgcolor=ft.colors.BLACK,
                                    duration=1000)
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()

    # Event handler to close the window
    def close_window(e):
        page.window.close()

    # Event handler to maximize/restore the window
    def open_nfo_window(e):
        # function to open a link in the browser
        def open_link(url):
            webbrowser.open(url)

        dialog = ft.AlertDialog(
            title=ft.Text("My contacts:", text_align=ft.TextAlign.CENTER),
            shape=ft.RoundedRectangleBorder(radius=8),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.icons.EMAIL,
                        tooltip="Email",
                        height=30,
                        width=30,
                        on_click=lambda e: open_link("mailto:alexgicheva@gmail.com")
                    ),
                    ft.IconButton(
                        icon=ft.icons.SEND,
                        tooltip="Telegram",
                        height=30,
                        width=30,
                        on_click=lambda e: open_link("https://t.me/Alex_Gicheva")
                    ),
                    ft.IconButton(
                        icon=ft.icons.CODE,
                        tooltip="GitHub",
                        height=30,
                        width=30,
                        on_click=lambda e: open_link("https://github.com/SkriptSparrow")
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            ),
            actions=[
                ft.TextButton("OK", on_click=lambda e: close_dialog(dialog))
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Function for closing the dialog box
    def close_dialog(dialog):
        dialog.open = False
        page.update()

    # Event handler to minimize the window
    def minimize_window(e):
        page.window.minimized = True
        page.update()

    # Custom buttons for close, maximize, and minimize
    close_button = ft.IconButton(ft.icons.CLOSE, on_click=close_window)
    maximize_button = ft.IconButton(ft.icons.MENU, on_click=open_nfo_window)
    minimize_button = ft.IconButton(ft.icons.REMOVE, on_click=minimize_window)

    # Drag area for window
    drag_area = ft.WindowDragArea(
        ft.Container(height=50, width=1000),
        expand=True,
        maximizable=False
    )

    # Custom title bar (you can style it as you like)
    title_bar = ft.Row(
        controls=[
            maximize_button,
            drag_area,
            minimize_button,
            close_button
        ],
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Indents for separating interface elements
    margin_top = ft.Container(height=100, width=400)
    margin_img_txt = ft.Container(height=65, width=400)
    margin_middle = ft.Container(height=25, width=400)
    margin_botton = ft.Container(height=5, width=400)
    margin_botton1 = ft.Container(height=5, width=400)

    # Scissors icon for the header
    image = ft.Image(src="C:\\Users\\Asus\\PycharmProjects\\URLshortener\\img\\icon scissors.png",
                     width=150,
                     height=150)

    # Download Rubik font
    page.fonts = {"Rubik": "../fonts/rubik/Rubik-Medium.ttf"}

    # Container with icon and title (center alignment)
    header_col = ft.Column(
        controls=[image, margin_img_txt, ft.Text(
            "URL CUTTER",
            font_family="Rubik",
            size=26,
            weight=ft.FontWeight.BOLD)
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=400,
        spacing=0
    )

    # Field for entering a long URL
    url_input_field = ft.TextField(
        label="Input long URL",
        height=60,
        width=350,
        suffix=ft.IconButton(
            icon=ft.icons.CONTENT_PASTE,
            on_click=on_paste_click)
    )

    # Field for outputting a short URL
    short_url_field = ft.TextField(
        label="Short URL",
        read_only=True,
        width=350
    )

    # URL shortening button with a slight rounding effect
    shorten_button = ft.ElevatedButton(
        "CUT",
        color=ft.colors.WHITE,
        bgcolor='#EB244E',
        on_click=lambda e: shorten_url(),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            text_style=ft.TextStyle(
                font_family="Rubik",
                size=18
            )
        )
    )

    # Button to copy a short URL
    copy_button = ft.ElevatedButton(
        content=ft.Icon(ft.icons.CONTENT_COPY),
        color='#EB244E',
        on_click=lambda e: copy_to_clipboard(short_url_field.value),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    # Button to clear a long URL
    clear_button = ft.ElevatedButton(
        "CLEAR",
        color= '#EB244E',
        on_click=lambda e: clear_text(url_input_field.value),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8),
                             text_style=ft.TextStyle(
                                 font_family="Rubik",
                                 size=18)
                             )
    )

    # Container for buttons (arranged in a row with a certain distance)
    button_row = ft.Row(
        controls=[shorten_button, clear_button, copy_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=44,
        width=350
    )

    # Signature with text, center alignment
    footer = ft.Text(
        "DEVELOPED BY CODEBIRD",
        color=ft.colors.GREY_500,
        width=350,
        text_align=ft.TextAlign.CENTER,
    )

    # Container for the footer text
    footer_container = ft.Column(
        controls=[footer],
        alignment=ft.MainAxisAlignment.END,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # A common container containing all the elements of a page
    content = ft.Column(
        controls=[title_bar, margin_top, header_col, margin_middle,
                  url_input_field, short_url_field, button_row,
                  margin_botton, footer_container, margin_botton1],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    # Adding a container to a page with vertical alignment
    page.add(
        ft.Column(
            controls=[content],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            height=page.window.height
        )
    )

    page.update()


ft.app(target=main)
