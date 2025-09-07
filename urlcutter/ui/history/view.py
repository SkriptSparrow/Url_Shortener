"""History screen (pure layout, no data/logic yet).

- Без запросов к БД и сервисам.
- Только разметка и заглушки обработчиков (print).
- I18n: принимает функцию `t(key: str) -> str`, по умолчанию возвращает ключ.
"""

from __future__ import annotations

import contextlib
import math
from datetime import datetime, timedelta

import flet as ft


def make_history_screen(  # noqa: PLR0915
    t=lambda k: k,
    *,
    items: list[dict] | None = None,
    on_back: callable | None = None,
) -> ft.Container:
    # ---- Compact constants for narrow window ----
    HEADING_H = 36
    ROW_H = 40
    COL_SPACING = 8
    PAD = 12
    FS_BASE = 12
    FS_URL = 12
    TAB_H = 344

    page_idx = 1
    page_size_val = 7

    label_pages_ref = ft.Ref[ft.Text]()
    btn_prev_ref = ft.Ref[ft.IconButton]()
    btn_next_ref = ft.Ref[ft.IconButton]()
    page_size_ref = ft.Ref[ft.Dropdown]()

    raw_items = list(items or [])
    filtered_items = list(raw_items)

    # Refs к контролам
    table_ref = ft.Ref[ft.DataTable]()
    empty_hint_ref = ft.Ref[ft.Text]()

    search_ref = ft.Ref[ft.TextField]()
    date_from_ref = ft.Ref[ft.TextField]()
    date_to_ref = ft.Ref[ft.TextField]()
    service_ref = ft.Ref[ft.Dropdown]()

    btn_back = ft.IconButton(
        ft.Icons.ARROW_BACK,
        tooltip="Back",
        icon_size=24,
    )

    # ВЕШАЕМ ХЭНДЛЕР НАПРЯМУЮ, если передан
    if on_back is not None:
        btn_back.on_click = on_back
    else:
        # чтобы видеть, что клик вообще срабатывает
        btn_back.on_click = lambda e: print("[History] Back clicked (no on_back)")

    btn_export_ref = ft.Ref[ft.ElevatedButton]()

    # ---- Filters (kept minimal; English labels) ----
    search = ft.TextField(
        label="Search",
        content_padding=ft.padding.only(left=PAD, right=PAD, top=17, bottom=17),
        dense=True,
        expand=True,
        ref=search_ref,
        on_submit=lambda e: apply_filters(e),
    )
    date_from = ft.TextField(
        label="Date from",
        dense=True,
        width=120,
        content_padding=ft.padding.only(left=PAD, right=PAD, top=17, bottom=17),
        ref=date_from_ref,
        on_submit=lambda e: apply_filters(e),
    )
    date_to = ft.TextField(
        label="Date to",
        dense=True,
        width=120,
        content_padding=ft.padding.only(left=PAD, right=PAD, top=17, bottom=17),
        ref=date_to_ref,
        on_submit=lambda e: apply_filters(e),
    )

    def _build_service_options():
        services = sorted({it.get("service", "") for it in raw_items if it.get("service")})
        return [ft.dropdown.Option("ALL", "ALL")] + [ft.dropdown.Option(s, s) for s in services]

    service = ft.Dropdown(
        label="Service",
        dense=True,
        width=140,
        options=_build_service_options(),
        value="ALL",
        ref=service_ref,
    )
    btn_apply = ft.ElevatedButton("Apply", height=42, width=80, on_click=lambda e: apply_filters(e))
    btn_reset = ft.ElevatedButton("Reset", height=42, width=80, on_click=lambda e: reset_filters(e))
    btn_export = ft.ElevatedButton(
        "Export CSV",
        ref=btn_export_ref,
        on_click=lambda e: on_export(e),
        tooltip="Export current selection",
        color=ft.Colors.WHITE,
        bgcolor="#EB244E",
        height=42,
        width=110,
    )

    filters_row = ft.ResponsiveRow(
        controls=[
            ft.Container(search, col={"xs": 12, "md": 6}),
            ft.Container(date_from, col={"xs": 6, "md": 3}),
            ft.Container(date_to, col={"xs": 6, "md": 3}),
            ft.Container(service, col={"xs": 12, "md": 4}),
            ft.Container(
                ft.Row([btn_apply, btn_reset, btn_export], spacing=COL_SPACING, wrap=False),
                col=12,
                padding=ft.padding.only(top=4),
            ),
        ],
        spacing=COL_SPACING,
        run_spacing=COL_SPACING,
    )

    # ---- Table rows (compact, English headers) ----
    def _txt(v: str, size=FS_BASE):
        return ft.Text(v, size=size)

    def _url_cell(v: str):
        return ft.Text(
            v or "—",
            size=FS_URL,
            font_family="monospace",
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            tooltip=v or "",
            selectable=True,
        )

    def _copy(e, s: str):  # quick copy helper
        p = e.control.page
        p.set_clipboard(s)
        p.snack_bar = ft.SnackBar(ft.Text("Copied"), open=True)
        p.update()

    def _open(e, url: str):
        e.control.page.launch_url(url)

    snack = ft.SnackBar(content=ft.Text(""), open=False)

    def _toast(page: ft.Page, msg: str):
        snack.content.value = msg
        snack.open = True
        page.overlay.append(snack)  # если ещё не добавлен
        page.update()

    def make_row(it: dict) -> ft.DataRow:
        short_url = it.get("short_url", "")
        return ft.DataRow(
            cells=[
                ft.DataCell(_txt(it.get("created_at_local", "—"))),  # Date
                ft.DataCell(_txt(it.get("service", "—"))),  # Service
                ft.DataCell(_url_cell(it.get("short_url", ""))),  # Short URL
                ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.CONTENT_COPY,
                                tooltip="Copy",
                                icon_size=16,
                                on_click=lambda e, s=short_url: _copy(e, s),
                            ),
                            ft.IconButton(
                                ft.Icons.OPEN_IN_NEW,
                                tooltip="Open",
                                icon_size=16,
                                on_click=lambda e, u=short_url: _open(e, u),
                            ),
                        ],
                        spacing=2,
                    )
                ),
            ]
        )

    def _parse_ymd(s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            return datetime.strptime(s.strip(), "%Y-%m-%d")
        except Exception:
            return None

    def render_table():  # noqa: PLR0912
        # считаем страницы
        total = len(filtered_items)
        total_pages = max(1, math.ceil(total / page_size_val)) if total > 0 else 1

        # приводим page_idx к допустимому диапазону
        nonlocal page_idx
        if total == 0:
            page_idx = 1
        else:
            if page_idx < 1:
                page_idx = 1
            if page_idx > total_pages:
                page_idx = total_pages

        # слайс видимых строк
        start = 0 if total == 0 else (page_idx - 1) * page_size_val
        end = start + page_size_val
        visible = filtered_items[start:end] if total > 0 else []

        # таблица
        table_ref.current.rows = [make_row(it) for it in visible]
        table_ref.current.update()

        # пустое состояние
        empty_hint_ref.current.value = (
            "" if visible else ("No results. Click Reset to clear filters." if total == 0 else "No data on this page")
        )
        empty_hint_ref.current.update()

        # навигатор: "X / Y" и доступность стрелок
        if total == 0:
            label_pages_ref.current.value = "0 / 0"
            if btn_prev_ref.current:
                btn_prev_ref.current.disabled = True
            if btn_next_ref.current:
                btn_next_ref.current.disabled = True
        else:
            label_pages_ref.current.value = f"{page_idx} / {total_pages}"
            if btn_prev_ref.current:
                btn_prev_ref.current.disabled = page_idx <= 1
            if btn_next_ref.current:
                btn_next_ref.current.disabled = page_idx >= total_pages

        label_pages_ref.current.update()
        if btn_prev_ref.current:
            btn_prev_ref.current.update()
        if btn_next_ref.current:
            btn_next_ref.current.update()

        if btn_export_ref.current:
            btn_export_ref.current.tooltip = f"Export {total} rows"
            btn_export_ref.current.update()

    def on_export(e: ft.ControlEvent):
        data = filtered_items
        if not data:
            _toast(e.page, "Nothing to export")
            return

        def handle_save_result(ev: ft.FilePickerResultEvent):
            # путь выбран пользователем?
            if getattr(ev, "path", None):
                try:
                    import csv

                    with open(ev.path, "w", newline="", encoding="utf-8-sig") as f:
                        w = csv.writer(f, delimiter=";")
                        w.writerow(["Date", "Service", "Short URL"])
                        for it in data:
                            w.writerow(
                                [
                                    it.get("created_at_local", ""),
                                    it.get("service", ""),
                                    it.get("short_url", ""),
                                ]
                            )
                    _toast(e.page, f"Exported lines: {len(data)}")
                except Exception as ex:
                    _toast(e.page, f"Export error: {ex}")
            # аккуратно удаляем пикер с overlay
            with contextlib.suppress(Exception):
                e.page.overlay.remove(fp)
            e.page.update()

        # создаём FilePicker на лету и добавляем его в overlay страницы
        fp = ft.FilePicker(on_result=handle_save_result)
        e.page.overlay.append(fp)
        e.page.update()
        # открываем диалог "Сохранить как"
        from datetime import datetime

        fp.save_file(
            file_name=f"history_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv",
            allowed_extensions=["csv"],
        )

    def apply_filters(e: ft.ControlEvent | None = None):
        nonlocal filtered_items

        date_from_ref.current.border_color = None
        date_to_ref.current.border_color = None
        date_from_ref.current.update()
        date_to_ref.current.update()

        q = (search_ref.current.value or "").strip().lower()
        svc = service_ref.current.value or "ALL"
        d_from = _parse_ymd(date_from_ref.current.value)
        d_to = _parse_ymd(date_to_ref.current.value)

        if d_from and d_to and d_from > d_to:
            _toast(date_from_ref.current.page, "Incorrect dates'")
            date_from_ref.current.border_color = "red"
            date_to_ref.current.border_color = "red"
            date_from_ref.current.update()
            date_to_ref.current.update()
            return

        # inclusive end: до конца дня
        if d_to:
            d_to = d_to + timedelta(days=1)

        def ok(it: dict) -> bool:
            # search по нескольким полям
            if q:
                hay = " ".join(
                    [
                        it.get("short_url", ""),
                        it.get("service", ""),
                        it.get("created_at_local", ""),
                    ]
                ).lower()
                if q not in hay:
                    return False

            # service
            if svc and svc != "ALL" and it.get("service") != svc:
                return False

            # дата
            ts = it.get("created_at_local")
            dt = None
            if ts:
                try:
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M")
                except Exception:
                    dt = None
            if d_from and (not dt or dt < d_from):
                return False
            return not (d_to and (not dt or dt >= d_to))

        filtered_items = [it for it in raw_items if ok(it)]
        render_table()

    def reset_filters(e: ft.ControlEvent | None = None):
        nonlocal filtered_items
        search_ref.current.value = ""
        date_from_ref.current.value = ""
        date_to_ref.current.value = ""
        service_ref.current.options = _build_service_options()
        service_ref.current.value = "ALL"
        filtered_items = list(raw_items)
        # обновим поля и таблицу
        search_ref.current.update()
        date_from_ref.current.update()
        date_to_ref.current.update()
        service_ref.current.update()
        render_table()

    def _recalc_and_render():
        # пересчёт ограничений и рендер таблицы + навигатора (см. обновлённый render_table ниже)
        render_table()

    def on_change_page_size(e: ft.ControlEvent):
        nonlocal page_size_val, page_idx
        try:
            page_size_val = int(e.control.value)
        except Exception:
            page_size_val = 7
        page_idx = 1
        _recalc_and_render()

    def on_prev(e: ft.ControlEvent):
        nonlocal page_idx
        page_idx -= 1
        _recalc_and_render()
        if table_column_ref.current:
            table_column_ref.current.scroll_to(offset=0, duration=100)

    def on_next(e: ft.ControlEvent):
        nonlocal page_idx
        page_idx += 1
        _recalc_and_render()
        if table_column_ref.current:
            table_column_ref.current.scroll_to(offset=0, duration=100)

    # Первичная выборка для UI до первых update()
    # page_idx и page_size_val уже заданы выше
    initial_total = len(filtered_items)
    initial_total_pages = max(1, math.ceil(initial_total / page_size_val)) if initial_total > 0 else 1

    # какие строки видны на старте
    _initial_start = 0 if initial_total == 0 else (page_idx - 1) * page_size_val
    _initial_end = _initial_start + page_size_val
    initial_visible = filtered_items[_initial_start:_initial_end] if initial_total > 0 else []

    # что положить в таблицу и хинт
    initial_rows = [make_row(it) for it in initial_visible]
    initial_empty_text = (
        ""
        if initial_rows
        else ("No results. Click Reset to clear filters." if initial_total == 0 else "No data on this page")
    )

    # подпись страниц и состояние стрелок
    initial_pages_label = "0 / 0" if initial_total == 0 else f"{page_idx} / {initial_total_pages}"
    initial_prev_disabled = page_idx <= 1  # на старте всегда True
    initial_next_disabled = initial_total_pages <= 1  # активна, если страниц > 1

    table = ft.DataTable(
        ref=table_ref,
        columns=[
            ft.DataColumn(_txt("Date")),
            ft.DataColumn(_txt("Service")),
            ft.DataColumn(_txt("Short URL")),
            ft.DataColumn(ft.Text("")),
        ],
        rows=initial_rows,
        column_spacing=COL_SPACING,
        heading_row_height=HEADING_H,
        data_row_max_height=ROW_H,
        horizontal_margin=0,
    )

    # ---- Pagination (static stub; English) ----
    page_size = ft.Dropdown(
        width=88,
        value=str(page_size_val),
        options=[ft.dropdown.Option(str(x)) for x in (7, 10, 20, 50)],
        on_change=on_change_page_size,
        ref=page_size_ref,
    )

    pagination = ft.Row(
        controls=[
            ft.Text("Rows/page:"),
            page_size,
            ft.Container(expand=True),
            ft.Text(initial_pages_label, ref=label_pages_ref),
            ft.IconButton(
                ft.Icons.CHEVRON_LEFT,
                tooltip="Prev",
                icon_size=18,
                ref=btn_prev_ref,
                on_click=on_prev,
                disabled=initial_prev_disabled,
            ),
            ft.IconButton(
                ft.Icons.CHEVRON_RIGHT,
                tooltip="Next",
                icon_size=18,
                ref=btn_next_ref,
                on_click=on_next,
                disabled=initial_next_disabled,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    empty_hint = ft.Text(initial_empty_text, ref=empty_hint_ref)

    # Обертка для таблицы с прокруткой, которая растягивается
    table_column_ref = ft.Ref[ft.Column]()

    table_scroll = ft.Container(
        content=ft.Column(
            [table, empty_hint],
            spacing=COL_SPACING,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            ref=table_column_ref,  # 👈 добавляем ref
        ),
        height=TAB_H,
    )

    # 3) Основной контент прижат к верху окна:
    main_content = ft.Column(
        controls=[
            filters_row,
            table_scroll,  # ← наша прокручиваемая середина
            # убери нижний Divider, он визуально отталкивает пагинацию
        ],
        spacing=COL_SPACING,
        expand=True,
        alignment=ft.MainAxisAlignment.START,  # ← прижать вверх
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,  # ← тянуть по ширине
    )

    # 4) Низ: пагинация прижата к низу
    layout = ft.Column(
        controls=[
            main_content,  # ← растягивается
            pagination,  # ← всегда внизу
        ],
        spacing=0,
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # ← первый элемент к верху, второй к низу
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    # render_table()

    # 5) Корневой контейнер — тянем на весь экран, но НЕ центрируем контент:
    return ft.Container(
        layout,
        padding=ft.padding.only(left=PAD, right=PAD, top=COL_SPACING, bottom=PAD),
        expand=True,
        # alignment не задаём, чтобы не центрировать дочерний Column
    )
