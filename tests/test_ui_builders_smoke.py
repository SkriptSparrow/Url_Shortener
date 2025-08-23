import pytest

ui = pytest.importorskip("urlcutter.ui_builders")  # пропустить тест, если нет модуля

def test_builders_do_not_crash():
    header = ui.build_header()
    title_bar = ui.build_title_bar()
    inputs = ui.build_inputs()
    buttons = ui.build_buttons()
    footer = ui.build_footer()

    assert header is not None
    assert isinstance(title_bar, tuple) and len(title_bar) == 4
    assert isinstance(inputs, tuple) and len(inputs) == 2
    assert isinstance(buttons, tuple) and len(buttons) == 4
    assert footer is not None

def test_compose_page_smoke():
    title_bar, *_ = ui.build_title_bar()
    header = ui.build_header()
    url_inp, short_out = ui.build_inputs()
    row, btn1, btn2, btn3 = ui.build_buttons()
    footer = ui.build_footer()
    root = ui.compose_page(title_bar, header, url_inp, short_out, row, footer)
    assert root is not None
