# 1) Imports
from __future__ import annotations

import inspect
import os
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as _TimeoutError
from types import SimpleNamespace

import pyshorteners

from urlcutter import shorten_via_tinyurl_core as _shorten_core
from urlcutter.logging_utils import setup_logging
from urlcutter.normalization import _url_fingerprint, normalize_url
from urlcutter.protection import (
    CB_COOLDOWN_SEC,
    CB_FAIL_THRESHOLD,
    CIRCUIT_COOLDOWN_SEC,
    CIRCUIT_FAIL_THRESHOLD,
    CLIENT_RPM_LIMIT,
    RATE_LIMIT_WINDOW_SEC,
    AppState,
    _get_state,
    _reset_state,
    circuit_blocked,
    cooldown_left,
    rate_limit_allow,
    record_failure,
    record_success,
)
from urlcutter.protection import internet_ok as _internet_ok_core

# Публичные атрибуты для тестов:
FutTimeout = _TimeoutError


__all__ = [
    "normalize_url",
    "_url_fingerprint",
    "setup_logging",
    "shorten_via_tinyurl",
    "AppState",
    "_get_state",
    "_reset_state",
    "circuit_blocked",
    "cooldown_left",
    "rate_limit_allow",
    "record_failure",
    "record_success",
    "CB_COOLDOWN_SEC",
    "CB_FAIL_THRESHOLD",
    "CIRCUIT_COOLDOWN_SEC",
    "CIRCUIT_FAIL_THRESHOLD",
    "CLIENT_RPM_LIMIT",
    "RATE_LIMIT_WINDOW_SEC",
    "internet_ok",
]


# 2) Константы / Конфигурация
REQUEST_TIMEOUT = 8.0
RETRIES = 1

# ---- Ограничения и защита от капов удалённых сервисов ----
CONNECTIVITY_PROBE_URL = "https://www.google.com/generate_204"
CONNECTIVITY_TIMEOUT = 2.0  # короткий таймаут для проверки сети

# ---- Логирование ----
LOG_ENABLED = True
LOG_DEBUG = os.getenv("URLCUTTER_DEBUG") == "1"
LOG_FILE = "logs/app.log"
LOG_MAX_BYTES = 1_000_000
LOG_BACKUPS = 3


# публичная функция, которую дергают тесты
def internet_ok(logger):
    return _internet_ok_core(logger, AppState_cls=AppState)


def shorten_via_tinyurl(
    url: str,
    timeout: float | None = None,
    *,
    _get=None,
    _shortener_factory=None,
    _pool_factory=None,
) -> str:
    shortener_factory = _shortener_factory or pyshorteners.Shortener
    pool_factory = _pool_factory or ThreadPoolExecutor
    return _shorten_core(
        url,
        timeout,
        _get=_get,
        _shortener_factory=shortener_factory,
        _pool_factory=pool_factory,
    )


# 8) Точка входа (инициализация и «провода»)
def main(page):  # можно без аннотации, чтобы не держать Flet на импорте
    # локальные импорты — так тестовый monkeypatch перехватывает их корректно
    import urlcutter.ui_builders as U  # noqa: PLC0415
    from urlcutter.handlers import Handlers  # noqa: PLC0415

    logger = setup_logging(enabled=LOG_ENABLED, debug=LOG_DEBUG)
    U.configure_window_and_theme(page)

    header_col = U.build_header()
    title_bar, info_btn, minimize_btn, close_btn = U.build_title_bar()
    url_input_field, short_url_field = U.build_inputs()
    button_row, shorten_button, clear_button, copy_button = U.build_buttons()
    footer_container = U.build_footer()

    root = U.compose_page(
        title_bar,
        header_col,
        url_input_field,
        short_url_field,
        button_row,
        footer_container,
    )
    page.add(root)

    ui = SimpleNamespace(
        # даём оба алиаса для каждого поля — подойдут и боевому Handlers, и FakeHandlers
        url_input_field=url_input_field,
        url_inp=url_input_field,
        short_url_field=short_url_field,
        short_out=short_url_field,
        shorten_button=shorten_button,
        shorten_btn=shorten_button,
    )

    state = AppState()
    params = {
        "page": page,
        "logger": logger,
        "state": state,
        # имена на все случаи: боевой Handlers и тестовый FakeHandlers
        "url_input_field": url_input_field,
        "url_inp": url_input_field,
        "short_url_field": short_url_field,
        "short_out": short_url_field,
        "shorten_button": shorten_button,
        "shorten_btn": shorten_button,
        "ui": ui,
    }

    try:
        sig = inspect.signature(Handlers.__init__)
    except (TypeError, ValueError):
        sig = inspect.signature(Handlers)

    kwargs = {name: params[name] for name in sig.parameters if name != "self" and name in params}

    handlers = Handlers(**kwargs)

    url_input_field.suffix.on_click = handlers.on_paste
    shorten_button.on_click = handlers.on_shorten
    clear_button.on_click = handlers.on_clear
    copy_button.on_click = handlers.on_copy

    info_btn.on_click = handlers.on_open_info
    minimize_btn.on_click = handlers.on_minimize
    close_btn.on_click = handlers.on_close

    page.update()


if __name__ == "__main__":  # pragma: no cover
    import multiprocessing as mp

    mp.freeze_support()
    import flet as ft

    ft.app(target=main, view=ft.AppView.FLET_APP)
