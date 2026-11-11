"""Smoke-test the built portfolio without sending messages or opening external sites."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlsplit

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
                    reduced_motion='reduce', locale='en-US',
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
                    expect(page.locator('html')).to_have_attribute('lang', 'en')
                    require(page.locator('h1').count() == 1, 'Missing or duplicate main heading')
                    require(page.locator('vite-error-overlay').count() == 0, 'Framework error overlay')
                    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Homepage horizontal overflow')
                    require('Arial' in page.locator('body').evaluate('(el) => getComputedStyle(el).fontFamily'), 'Missing stylesheet')
                    page.screenshot(path=str(evidence / f'{width}-home.png'))
                    flows.append('homepage identity, content, stylesheet and overflow')

                    if width < 600:
                        trigger = page.get_by_role('button', name='Open menu', exact=True)
                        trigger.click()
                        expect(page.get_by_role('dialog')).to_be_visible()
                        box = page.get_by_role('dialog').bounding_box()
                        require(box is not None and box['x'] >= -1 and box['y'] >= -1
                                and box['x'] + box['width'] <= width + 1
                                and box['y'] + box['height'] <= height + 1,
                                'Mobile menu extends outside the viewport')
                        page.screenshot(path=str(evidence / f'{width}-menu.png'))
                        page.get_by_role('navigation', name='Mobile menu', exact=True).get_by_role('link', name='Projects').click()
                        expect(page.get_by_role('dialog')).to_have_count(0)
                        require(urlsplit(page.url).fragment == 'projetos', 'Mobile navigation did not reach projects')
                        trigger.click()
                        page.keyboard.press('Escape')
                        expect(page.get_by_role('dialog')).to_have_count(0)
                        flows.append('mobile menu: open, anchor navigation, close, Escape')
                    else:
                        page.get_by_role('navigation', name='Main navigation', exact=True).get_by_role('link', name='Projects', exact=True).click()
                        require(urlsplit(page.url).fragment == 'projetos', 'Desktop navigation did not reach projects')
                        flows.append('desktop anchor navigation')

                    if width < 600:
                        page.get_by_role('button',name='Open menu',exact=True).click()
                        page.get_by_role('navigation',name='Mobile menu',exact=True).get_by_role('link',name='Blog',exact=True).click()
                    else:
                        page.get_by_role('navigation',name='Main navigation',exact=True).get_by_role('link',name='Blog',exact=True).click()
                    require(urlsplit(page.url).path.rstrip('/').endswith('/blog'),'Menu Blog link failed')
                    expect(page.locator('html')).to_have_attribute('lang','en')
                    page.go_back(wait_until='networkidle')
                    expect(page.locator('.hero h1')).to_be_visible()
                    flows.append('English Blog entry in the main navigation')

                    first = page.locator('.skill-trigger').nth(0)
                    second = page.locator('.skill-trigger').nth(1)
                    second.click()
                    expect(second).to_have_attribute('aria-expanded', 'true')
                    expect(first).to_have_attribute('aria-expanded', 'false')
                    second.click()
                    expect(second).to_have_attribute('aria-expanded', 'false')
                    flows.append('expertise accordion: expand, mutual exclusion, collapse')

                    submit = page.get_by_role('button', name='Prepare message', exact=True)
                    submit.click()
                    expect(page.locator('.prepared-message')).to_have_count(0)
                    require(not page.locator('input[name="name"]').evaluate('(el) => el.checkValidity()'), 'Required field accepted empty input')
                    page.locator('input[name="name"]').fill('Demonstration Reader')
                    page.locator('input[name="email"]').fill('reader@example.invalid')
                    page.locator('textarea[name="message"]').fill('Synthetic message to verify the interface without external submission.')
                    page.get_by_role('combobox', name='Project type', exact=True).click()
                    page.get_by_role('option', name='Automation', exact=True).click()
                    submit.click()
                    prepared = page.get_by_role('textbox', name='Prepared message', exact=True)
                    expect(prepared).to_be_visible()
                    text = prepared.input_value()
                    for expected in ['Hello, Maurício! My name is Demonstration Reader.', 'I’d like to discuss automation.', 'reader@example.invalid', 'Synthetic message']:
                        require(expected in text, 'Prepared message lost a form value: ' + expected)
                    copy = page.get_by_role('button', name='Copy message', exact=True)
                    copy.click()
                    expect(page.get_by_role('button', name='Copied', exact=True)).to_be_visible()
                    require(page.evaluate('navigator.clipboard.readText()') == text, 'Clipboard differs from prepared message')
                    page.locator('textarea[name="message"]').fill('Updated synthetic message: the result must reflect the edit.')
                    submit.click()
                    require('Updated synthetic message' in prepared.input_value(), 'Prepared message is stale after editing')
                    expect(page.get_by_role('button', name='Copy message', exact=True)).to_be_visible()
                    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Form state horizontal overflow')
                    page.locator('.prepared-message').scroll_into_view_if_needed()
                    page.screenshot(path=str(evidence / f'{width}-local-message.png'))
                    flows.append('form: required fields, selection, local generation, clipboard, regeneration')

                    draft = urlsplit(page.get_by_role('link', name='Open email draft', exact=True).get_attribute('href'))
                    require(draft.scheme == 'mailto' and draft.path == 'mauricioryotoitataguchi@gmail.com', 'Wrong email draft recipient')
                    require(parse_qs(draft.query)['body'] == [prepared.input_value()], 'Email draft lost prepared text')
                    fragment = urlsplit(page.url).fragment
                    page.get_by_role('button', name='Português do Brasil', exact=True).click()
                    expect(page.locator('html')).to_have_attribute('lang', 'pt-BR')
                    require(parse_qs(urlsplit(page.url).query).get('lang') == ['pt'], 'Portuguese choice missing from URL')
                    require(urlsplit(page.url).fragment == fragment, 'Language choice lost the current anchor')
                    translated = page.get_by_role('textbox', name='Mensagem preparada', exact=True)
                    require('Gostaria de conversar sobre automação.' in translated.input_value(), 'Selected topic did not translate')
                    require('Updated synthetic message' in translated.input_value(), 'Language choice lost typed message')
                    expect(page.get_by_role('button', name='Copiar mensagem', exact=True)).to_be_visible()
                    draft = urlsplit(page.get_by_role('link', name='Abrir rascunho de e-mail', exact=True).get_attribute('href'))
                    require(parse_qs(draft.query)['body'] == [translated.input_value()], 'Portuguese email draft lost text')
                    page.goto(base, wait_until='networkidle')
                    expect(page.locator('html')).to_have_attribute('lang', 'pt-BR')
                    expect(page.locator('.hero h1')).to_have_text('Análisede dados& BI.')
                    expect(page.get_by_text('Disponível para projetos freelance remunerados', exact=True)).to_be_in_viewport()
                    expect(page.get_by_role('link', name='Converse sobre seu projeto', exact=True)).to_be_in_viewport()
                    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Portuguese horizontal overflow')
                    page.screenshot(path=str(evidence / f'{width}-home-pt.png'))
                    page.reload(wait_until='networkidle')
                    expect(page.locator('html')).to_have_attribute('lang', 'pt-BR')
                    if width < 600:
                        page.get_by_role('button', name='Abrir menu', exact=True).click()
                        page.get_by_role('navigation', name='Menu móvel', exact=True).get_by_role('link', name='Projetos').click()
                        expect(page.get_by_role('dialog')).to_have_count(0)
                        require(urlsplit(page.url).fragment == 'projetos', 'Portuguese mobile menu missed the section')
                    page.goto(base + '?lang=en', wait_until='networkidle')
                    if width < 600:
                        page.get_by_role('button', name='Open menu', exact=True).click()
                        page.get_by_role('navigation', name='Mobile menu', exact=True).get_by_role('link', name='Projects').click()
                    else:
                        page.get_by_role('navigation', name='Main navigation', exact=True).get_by_role('link', name='Projects', exact=True).click()
                    page.get_by_role('button', name='Português do Brasil', exact=True).click()
                    page.go_back()
                    expect(page.locator('html')).to_have_attribute('lang', 'en')
                    require(parse_qs(urlsplit(page.url).query).get('lang') == ['en'], 'Back did not restore the English URL')
                    page.go_forward()
                    expect(page.locator('html')).to_have_attribute('lang', 'pt-BR')
                    page.get_by_role('button', name='English', exact=True).click()
                    expect(page.locator('html')).to_have_attribute('lang', 'en')
                    flows.append('bilingual homepage, persistent language, preserved form/anchors, Portuguese mobile menu and exact mailto draft')

                    page.get_by_role('link', name='Explore the blog', exact=True).click()
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
                    page.screenshot(path=str(evidence / f'{width}-failure.png'), full_page=True)
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
        (args.evidence_dir / 'results.json').write_text(output + '\n', encoding='utf-8')
        print(output)
        return 0
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    raise SystemExit(main())
