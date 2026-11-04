"""Smoke-test the built portfolio without sending messages or opening external sites."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
        pass


def exercise(base: str, evidence: Path) -> dict:
    evidence.mkdir(parents=True, exist_ok=True)
    checks = []
    with sync_playwright() as runtime:
        options = {'headless': True}
        if os.environ.get('BROWSER_EXECUTABLE'):
            options['executable_path'] = os.environ['BROWSER_EXECUTABLE']
        browser = runtime.chromium.launch(**options)
        try:
            for width, height in [(1440, 1000), (390, 844)]:
                context = browser.new_context(
                    viewport={'width': width, 'height': height},
                    reduced_motion='reduce', locale='pt-BR',
                    permissions=['clipboard-read', 'clipboard-write'],
                )
                page = context.new_page()
                page.set_default_timeout(15000)
                errors, mutations = [], []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)

                def read_only(route):
                    if route.request.method not in ('GET', 'HEAD', 'OPTIONS'):
                        mutations.append(route.request.method + ' ' + route.request.url)
                        route.abort()
                    else:
                        route.continue_()

                context.route('**/*', read_only)
                flows = []
                try:
                    response = page.goto(base, wait_until='networkidle', timeout=30000)
                    require(response is not None and response.status == 200, 'Homepage HTTP failure')
                    require('Taguchi' in page.title(), 'Unexpected page title')
                    expect(page.locator('.hero h1')).to_be_visible()
                    require(page.locator('h1').count() == 1, 'Missing or duplicate main heading')
                    require(page.locator('vite-error-overlay').count() == 0, 'Framework error overlay')
                    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Homepage horizontal overflow')
                    require('Arial' in page.locator('body').evaluate('(el) => getComputedStyle(el).fontFamily'), 'Missing stylesheet')
                    page.screenshot(path=str(evidence / f'{width}-inicio.png'))
                    flows.append('homepage identity, content, stylesheet and overflow')

                    if width < 600:
                        trigger = page.get_by_role('button', name='Abrir menu', exact=True)
                        trigger.click()
                        expect(page.get_by_role('dialog')).to_be_visible()
                        page.get_by_role('navigation', name='Menu móvel', exact=True).get_by_role('link', name='Projetos').click()
                        expect(page.get_by_role('dialog')).to_have_count(0)
                        require(urlsplit(page.url).fragment == 'projetos', 'Mobile navigation did not reach projects')
                        trigger.click()
                        page.keyboard.press('Escape')
                        expect(page.get_by_role('dialog')).to_have_count(0)
                        flows.append('mobile menu: open, anchor navigation, close, Escape')
                    else:
                        page.get_by_role('navigation', name='Navegação principal', exact=True).get_by_role('link', name='Projetos', exact=True).click()
                        require(urlsplit(page.url).fragment == 'projetos', 'Desktop navigation did not reach projects')
                        flows.append('desktop anchor navigation')

                    first = page.locator('.skill-trigger').nth(0)
                    second = page.locator('.skill-trigger').nth(1)
                    second.click()
                    expect(second).to_have_attribute('aria-expanded', 'true')
                    expect(first).to_have_attribute('aria-expanded', 'false')
                    second.click()
                    expect(second).to_have_attribute('aria-expanded', 'false')
                    flows.append('expertise accordion: expand, mutual exclusion, collapse')

                    submit = page.get_by_role('button', name='Preparar mensagem', exact=True)
                    submit.click()
                    expect(page.locator('.prepared-message')).to_have_count(0)
                    require(not page.locator('input[name="name"]').evaluate('(el) => el.checkValidity()'), 'Required field accepted empty input')
                    page.locator('input[name="name"]').fill('Pessoa de demonstração')
                    page.locator('input[name="email"]').fill('demonstracao@example.invalid')
                    page.locator('textarea[name="message"]').fill('Mensagem sintética para verificar a interface, sem envio externo.')
                    page.get_by_role('combobox', name='Tipo de projeto', exact=True).click()
                    page.get_by_role('option', name='Automação', exact=True).click()
                    submit.click()
                    prepared = page.get_by_role('textbox', name='Mensagem preparada', exact=True)
                    expect(prepared).to_be_visible()
                    text = prepared.input_value()
                    for expected in ['Pessoa de demonstração', 'Automação', 'demonstracao@example.invalid', 'Mensagem sintética']:
                        require(expected in text, 'Prepared message lost a form value: ' + expected)
                    copy = page.get_by_role('button', name='Copiar mensagem', exact=True)
                    copy.click()
                    expect(page.get_by_role('button', name='Copiada', exact=True)).to_be_visible()
                    require(page.evaluate('navigator.clipboard.readText()') == text, 'Clipboard differs from prepared message')
                    page.locator('textarea[name="message"]').fill('Segunda mensagem sintética: o resultado precisa acompanhar a edição.')
                    submit.click()
                    require('Segunda mensagem sintética' in prepared.input_value(), 'Prepared message is stale after editing')
                    expect(page.get_by_role('button', name='Copiar mensagem', exact=True)).to_be_visible()
                    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Form state horizontal overflow')
                    page.locator('.prepared-message').scroll_into_view_if_needed()
                    page.screenshot(path=str(evidence / f'{width}-mensagem-local.png'))
                    flows.append('form: required fields, selection, local generation, clipboard, regeneration')

                    page.get_by_role('link', name='Explorar o blog', exact=True).click()
                    require(urlsplit(page.url).path.rstrip('/').endswith('/blog'), 'Homepage blog link failed')
                    expect(page.locator('h1')).to_be_visible()
                    page.go_back(wait_until='networkidle')
                    expect(page.locator('.hero h1')).to_be_visible()
                    require(not errors, 'Browser errors: ' + '; '.join(errors))
                    require(not mutations, 'Unexpected request that could send data: ' + '; '.join(mutations))
                    flows.append('homepage to blog and browser back')
                    checks.append({'viewport': f'{width}x{height}', 'status': 'passed', 'flows': flows,
                                   'runtime_errors': errors, 'outbound_mutations': mutations})
                except Exception:
                    page.screenshot(path=str(evidence / f'{width}-falha.png'), full_page=True)
                    raise
                finally:
                    context.close()
        finally:
            browser.close()
    return {'status': 'passed', 'scope': 'principal portfolio interactions after a clean build',
            'synthetic_data_only': True, 'viewports': checks,
            'limits': 'Chromium smoke coverage; not every browser, accessibility rule or animation state.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT / 'docs')))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        result = exercise(f'http://127.0.0.1:{server.server_port}/', args.evidence_dir)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        (args.evidence_dir / 'resultado.json').write_text(output + '\n', encoding='utf-8')
        print(output)
        return 0
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    raise SystemExit(main())
