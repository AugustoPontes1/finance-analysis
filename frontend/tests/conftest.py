import pytest
from playwright.sync_api import sync_playwright

import os

BASE_URL_FRONT = os.getenv("BASE_URL_FRONT")


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page()
    page.goto(BASE_URL_FRONT)
    page.wait_for_load_state("networkidle")
    yield page
    page.close()


