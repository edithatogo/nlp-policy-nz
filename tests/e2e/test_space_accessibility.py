"""End-to-end accessibility checks for the Gradio Space."""

from __future__ import annotations

from contextlib import suppress

import pytest

from spaces.app import build_app

playwright = pytest.importorskip("playwright.sync_api")


def test_space_supports_keyboard_navigation_to_privacy_footer() -> None:
    """The public Space should allow keyboard focus to reach the privacy footer."""
    app = build_app()
    launch_result = app.launch(
        server_name="127.0.0.1",
        server_port=7863,
        prevent_thread_lock=True,
        quiet=True,
        share=False,
    )
    local_url = (
        launch_result[1]
        if isinstance(launch_result, tuple) and len(launch_result) > 1
        else getattr(launch_result, "local_url", "http://127.0.0.1:7863")
    )

    try:
        with playwright.sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            page.goto(local_url, wait_until="networkidle")
            page.keyboard.press("Tab")
            active_texts: list[str] = []
            for _ in range(12):
                page.keyboard.press("Tab")
                active_texts.append(page.evaluate("document.activeElement?.innerText || document.activeElement?.textContent || ''"))
            assert any("Privacy notice" in text or "Read the policy" in text for text in active_texts)
            assert page.locator("#privacy-footer").count() == 1
            with suppress(Exception):
                browser.close()
    finally:
        with suppress(Exception):
            close = getattr(launch_result, "close", None)
            if callable(close):
                close()
