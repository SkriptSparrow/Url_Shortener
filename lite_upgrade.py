# 1) Imports
from __future__ import annotations
import os
from concurrent.futures import ThreadPoolExecutor

# ядро
from urlcutter import normalize_url, _url_fingerprint
from urlcutter import (
    AppState,                       # класс состояния (важно для monkeypatch в тестах)
    internet_ok as _internet_ok_core,
    circuit_blocked, cooldown_left,
    record_failure, record_success,
    rate_limit_allow, _get_state, _reset_state,
    CLIENT_RPM_LIMIT, CB_FAIL_THRESHOLD, CB_COOLDOWN_SEC,
    CIRCUIT_FAIL_THRESHOLD, CIRCUIT_COOLDOWN_SEC, RATE_LIMIT_WINDOW_SEC,
)
from urlcutter import shorten_via_tinyurl_core as _shorten_core
from urlcutter.logging_utils import setup_logging


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

# shorten_via_tinyurl должен подставлять локальный ThreadPoolExecutor,
# чтобы его можно было monkeypatch'ить через lite_upgrade.ThreadPoolExecutor.
def shorten_via_tinyurl(
    url: str,
    timeout: float | None = None,
    *,
    _get=None,
    _shortener_factory=None,
    _pool_factory=None,
) -> str:
    pool_factory = _pool_factory or ThreadPoolExecutor
    return _shorten_core(
        url,
        timeout,
        _get=_get,
        _shortener_factory=_shortener_factory,
        _pool_factory=pool_factory,
    )


# 8) Точка входа (инициализация и «провода»)
def main(page):  # можно без аннотации, чтобы не держать Flet на импорте
    from urlcutter.handlers import Handlers
    from urlcutter.ui_builders import (
        configure_window_and_theme, build_header, build_title_bar, build_footer,
        build_inputs, build_buttons, compose_page
    )

    logger = setup_logging(enabled=LOG_ENABLED, debug=LOG_DEBUG)
    configure_window_and_theme(page)

    # UI — создаём контролы ОДИН раз, без обработчиков внутри билдеров
    header_col = build_header()
    title_bar, info_btn, minimize_btn, close_btn = build_title_bar()  # возвращаем row и кнопки
    url_input_field, short_url_field = build_inputs()  # suffix без on_click
    button_row, shorten_button, clear_button, copy_button = build_buttons()  # кнопки без on_click
    footer_container = build_footer()

    # Компонуем и добавляем на страницу
    root = compose_page(
        title_bar,
        header_col,
        url_input_field,
        short_url_field,
        button_row,  # <-- вместо dummy_button_row
        footer_container,
    )
    page.add(root)

    # Состояние + обработчики (получают ссылки на ТЕ ЖЕ контролы)
    state = AppState()
    handlers = Handlers(
        page, logger, state, url_input_field, short_url_field, shorten_button
    )  # <-- вместо dummy_cut_btn

    # Привязка событий к ТЕМ ЖЕ экземплярам контролов (без лямбд)
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
