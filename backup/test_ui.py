import os
import uuid
import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:5000')


@pytest.mark.ui
def test_formular_adauga_senzor(page: Page):
    # Pentru acest test, serverul Flask trebuie sa ruleze separat.
    cod = 'UI' + uuid.uuid4().hex[:8].upper()
    page.goto(f'{BASE_URL}/senzori')
    expect(page.get_by_role('heading', name='Lista senzorilor')).to_be_visible()
    page.get_by_label('Cod').fill(cod)
    page.get_by_label('Locație').fill('Laborator UI')
    page.get_by_role('button', name='Adaugă senzor').click()
    expect(page.get_by_text(cod, exact=True)).to_be_visible()
