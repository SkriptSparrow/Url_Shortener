import logging
import webbrowser
from concurrent.futures import TimeoutError as FutTimeout
from urllib.parse import urlparse

import flet as ft
import pyperclip
import validators

from urlcutter import CLIENT_RPM_LIMIT, AppState, _url_fingerprint
from urlcutter.protection import internet_ok
from urlcutter.shorteners import shorten_via_tinyurl_core as shorten_via_tinyurl

REQUEST_TIMEOUT = 8.0
RETRIES = 1
DEFAULT_HTTP_TIMEOUT = 5


def _safe_fp(s: str) -> str:
    try:
        return _url_fingerprint(s)
    except Exception:
        # на пустых/мусорных входах логируем мягко
        return s or "<empty>"


class Handlers:
    def __init__(  # noqa: PLR0913
        self,
        page: ft.Page,
        logger: logging.Logger,
        state: AppState,
        url_input_field: ft.TextField,
        short_url_field: ft.TextField,
        shorten_button: ft.ElevatedButton,
    ):
        self.page = page
        self.logger = logger
        self.state = state
        self.url_input_field = url_input_field
        self.short_url_field = short_url_field
        self.shorten_button = shorten_button

    # UX-утилиты
    def toast(self, msg: str, ms: int = 1500):
        sb = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.BLACK, duration=ms)
        self.page.overlay.append(sb)
        sb.open = True
        self.page.update()

    def busy(self, on: bool):
        self.page.cursor = ft.MouseCursor.WAIT if on else ft.MouseCursor.BASIC
        self.shorten_button.disabled = on
        self.page.update()

    # Кнопки/поля
    def on_paste(self, _):
        self.toast("paste-click")
        self.logger.info("on_paste fired")
        pasted_text = pyperclip.paste()
        self.url_input_field.value = pasted_text
        self.page.update()

    def on_clear(self, _):
        if self.url_input_field.value:
            self.url_input_field.value = ""
            self.url_input_field.update()
            self.page.update()
        else:
            self.toast("Nothing to clear!", 1000)

    def on_copy(self, e):
        text = (self.short_url_field.value or "").strip()
        if text:
            self.page.set_clipboard(text)
            self.toast("Copied to clipboard!")
            self.logger.info("copy_to_clipboard ok")
        else:
            self.toast("Nothing to copy!")
            self.logger.info("copy_to_clipboard skipped reason=empty")

    def on_open_info(self, _):
        def open_link(url):
            webbrowser.open(url)

        dialog = ft.AlertDialog(
            title=ft.Text("My contacts", text_align=ft.TextAlign.CENTER),
            shape=ft.RoundedRectangleBorder(radius=8),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Hi! My name is Alexandra. I'm a Python developer. "
                        "It's one of my apps. If you like my work, "
                        "there are contacts below where you can contact me!",
                        size=18,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("My website:", expand=1, size=18),
                            ft.IconButton(
                                icon=ft.Icons.WEB,
                                tooltip="Website",
                                icon_size=30,
                                on_click=lambda e: open_link("https://mywebsite.com"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("My mail:", expand=1, size=18),
                            ft.IconButton(
                                icon=ft.Icons.EMAIL,
                                tooltip="Email",
                                icon_size=30,
                                on_click=lambda e: open_link("mailto:alexgicheva@gmail.com"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("My github:", expand=1, size=18),
                            ft.IconButton(
                                icon=ft.Icons.HUB,
                                tooltip="GitHub",
                                icon_size=30,
                                on_click=lambda e: open_link("https://github.com/SkriptSparrow"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=20,
            ),
            actions=[ft.TextButton("OK", on_click=lambda e: self.close_dialog(dialog))],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    def on_close(self, _):
        self.page.window.close()

    def on_minimize(self, _):
        self.page.window.minimized = True
        self.page.update()

    # Главный сценарий: валидация → защита → вызов сервиса → вывод
    def on_shorten(self, _):  # noqa: PLR0911, PLR0912, PLR0915
        long_url = self.url_input_field.value.strip()

        # безопасный лог, чтобы не падать на пустых строках
        self.logger.info("shorten_request url=%s", _safe_fp(long_url))

        # 0) Пусто
        if not long_url:
            self.toast("Enter the link.")
            self.logger.info("shorten_reject reason=empty_input")
            return

        # 0.5) Валидация URL (не даём validators.url уронить нас исключением)
        try:
            is_valid = bool(validators.url(long_url))
        except Exception:
            is_valid = False

        if not is_valid:
            self.toast("Incorrect URL. Check the link.")
            self.logger.info(
                "shorten_reject reason=invalid_url url=%s", _safe_fp(long_url)  # ← тоже безопасно логируем
            )
            return

        # 1) Уже tinyurl
        if long_url.startswith("https://tinyurl.com"):
            self.toast("This is already a short link.")
            self.logger.info("shorten_reject reason=already_shortened provider=tinyurl")
            return

        # 2) Защита
        if self.state.circuit_blocked():
            self.toast(f"Service cooling down {self.state.cooldown_left()}s after repeated errors.")
            self.logger.warning("shorten_blocked reason=circuit_open cooldown_left=%ds", self.state.cooldown_left())
            return
        if not self.state.rate_limit_allow(self.logger):
            self.toast(f"Local limit {CLIENT_RPM_LIMIT}/min to respect remote caps. Try later.")
            self.logger.warning("shorten_blocked reason=local_rate_limit rpm=%d", CLIENT_RPM_LIMIT)
            return
        if not internet_ok(self.logger):
            self.toast("No internet connection detected.")
            self.logger.warning("shorten_blocked reason=offline")
            return

        # 3) Запускаем с таймаутом + ретрай
        self.busy(True)
        last_err = None
        for attempt in range(1 + RETRIES):
            self.logger.info(
                "attempt_start provider=tinyurl attempt=%d timeout=%.1fs",
                attempt + 1,
                REQUEST_TIMEOUT,
            )
            try:
                short_url = shorten_via_tinyurl(long_url, REQUEST_TIMEOUT)
                self.short_url_field.value = short_url
                self.page.update()
                self.toast("Done! Link shortened.")
                self.busy(False)
                self.logger.info("attempt_success provider=tinyurl short_host=%s", urlparse(short_url).netloc)
                self.state.record_success()
                return

            except FutTimeout:
                last_err = "timeout"
                self.logger.error(
                    "attempt_error provider=tinyurl kind=timeout timeout=%.1fs attempt=%d",
                    REQUEST_TIMEOUT,
                    attempt + 1,
                )

            except Exception as e:
                msg = str(e)
                if "429" in msg or "Too Many Requests" in msg:
                    last_err = "rate"
                elif any(x in msg for x in ("502", "503", "504")):
                    last_err = "unavailable"
                else:
                    last_err = "unknown"
                if last_err == "unknown":
                    self.logger.exception(
                        "attempt_error provider=tinyurl kind=%s attempt=%d err=%s",
                        last_err,
                        attempt + 1,
                        msg,
                    )
                else:
                    self.logger.error(
                        "attempt_error provider=tinyurl kind=%s attempt=%d err=%s",
                        last_err,
                        attempt + 1,
                        msg,
                    )

        # 4) Все попытки исчерпаны
        self.busy(False)
        self.state.record_failure()
        self.logger.error("shorten_failed url=%s final_reason=%s", _url_fingerprint(long_url), last_err)
        if last_err == "timeout":
            self.toast("The service did not respond. Check the internet or try again later.")
        elif last_err == "rate":
            self.toast("Too many requests. Please wait a minute and try again.")
        elif last_err == "unavailable":
            self.toast("The service is temporarily unavailable. Please try again later.")
        else:
            self.toast("Failed to shorten the link. Details in the logs.")
