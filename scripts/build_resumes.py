"""Publish consistent English and Portuguese résumés from supplied career facts."""
from __future__ import annotations
import html
import json
from pathlib import Path
from typing import Callable
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, KeepTogether

rl_config.invariant = 1
LABELS = {
    'en': ['PROFILE', 'TECHNICAL SKILLS', 'PROFESSIONAL EXPERIENCE', 'SELECTED PERSONAL PROJECTS', 'EDUCATION', 'SELECTED TRAINING', 'LANGUAGES'],
    'pt': ['PERFIL', 'COMPETÊNCIAS TÉCNICAS', 'EXPERIÊNCIA PROFISSIONAL', 'PROJETOS PESSOAIS SELECIONADOS', 'FORMAÇÃO', 'FORMAÇÃO COMPLEMENTAR', 'IDIOMAS'],
}

def build_resumes(root: Path, page: Callable) -> None:
    out = root / 'public/resume'
    out.mkdir(parents=True, exist_ok=True)
    for language, filename, source in [
        ('en', 'mauricio-taguchi-resume.pdf', 'resume.json'),
        ('pt', 'mauricio-taguchi-curriculo-pt.pdf', 'resume-pt.json'),
    ]:
        r = json.loads((root / 'content/hiring' / source).read_text(encoding='utf-8'))
        labels = LABELS[language]
        body = ParagraphStyle('body', fontName='Helvetica', fontSize=10, leading=12.7,
                              textColor=colors.HexColor('#212735'), spaceAfter=2.3)
        small = ParagraphStyle('small', parent=body, fontSize=9.2, leading=11.6, spaceAfter=2)
        heading = ParagraphStyle('heading', parent=body, fontName='Helvetica-Bold', fontSize=10,
                                 leading=12, spaceBefore=6, spaceAfter=3, textColor=colors.HexColor('#233de5'))
        name = ParagraphStyle('name', parent=body, fontName='Helvetica-Bold', fontSize=20,
                              leading=24, spaceAfter=2.3)
        escape = html.escape
        def para(text: str, style=body) -> Paragraph:
            return Paragraph(text, style)
        def link(label: str, url: str) -> str:
            return f'<link href="{escape(url, quote=True)}" color="#233de5">{escape(label)}</link>'
        story = [para(escape(r['name']), name), para('<b>' + escape(r['headline']) + '</b>'),
                 para(escape(r['location']), small),
                 para(link(r['email'], 'mailto:' + r['email']) + ' | ' + ' | '.join(link(k, v) for k, v in r['links'].items()), small)]
        story += [para(labels[0], heading), para(escape(r['summary']))]
        story.append(para(labels[1], heading))
        for label, text in r['skills']:
            story.append(para('<b>' + escape(label) + ':</b> ' + escape(text)))
        story.append(para(labels[2], heading))
        for ex in r['experience']:
            story.append(para('<b>' + escape(ex['role']) + '</b> | ' + escape(ex['organization'])))
            story.append(para(escape(ex['dates']), small))
            for text in ex['bullets']:
                story.append(para('• ' + escape(text)))
        story.append(para(labels[3], heading))
        def project_links(project):
            case = 'Case study' if language == 'en' else 'Estudo de caso'
            code = 'Source code' if language == 'en' else 'Código-fonte'
            if project['demo'].endswith('/income/'):
                demo = 'Interactive dashboard' if language == 'en' else 'Dashboard interativo'
            else:
                demo = 'Interactive demo' if language == 'en' else 'Demonstração interativa'
            return ' · '.join((link(case, project['url']), link(demo, project['demo']), link(code, project['repo'])))
        for project in r['projects']:
            story.append(KeepTogether([
                para('<b>' + escape(project['name']) + '</b>'),
                para(escape(project['text'])), para(project_links(project), small),
            ]))
        com = r['communication']
        story.append(para('<b>' + link(com['label'], com['url']) + ':</b> ' + escape(com['text']), small))
        story += [para(labels[4], heading), para(escape(r['education']))]
        story.append(para(labels[5], heading))
        for item in r['training']:
            story.append(para('• ' + escape(item), small))
        story += [para(labels[6], heading), para(escape(r['languages']))]
        doc = SimpleDocTemplate(str(out / filename), pagesize=A4, leftMargin=42, rightMargin=42,
                                topMargin=30, bottomMargin=31, title=('Maurício Taguchi - Data Analyst Résumé' if language == 'en' else 'Maurício Taguchi - Currículo de Analista de Dados'),
                                author=r['name'], creator='Maurício Taguchi', subject=r['headline'], pageCompression=1)
        def footer(canvas, document):
            canvas.setAuthor(r['name']); canvas.setCreator('Maurício Taguchi')
            canvas.setFillColor(colors.HexColor('#233de5')); canvas.setFont('Helvetica-Bold', 9)
            canvas.drawString(42, 18, 'TM.')
            canvas.setFillColor(colors.HexColor('#555b65')); canvas.setFont('Helvetica', 8)
            canvas.drawRightString(A4[0] - 42, 18, 'mauriciotaguchi.com.br')
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        if language != 'en':
            continue
        h = '<div class="eyebrow">DATA ANALYST / JUNIOR OPPORTUNITIES</div>'
        h += f'<h1>{escape(r["name"])}</h1><p class="lead">{escape(r["headline"])}</p><p>{escape(r["location"])}</p>'
        h += '<div class="actions"><a class="button" href="mauricio-taguchi-resume.pdf" download>Download résumé (PDF)</a><a class="button secondary" href="mauricio-taguchi-curriculo-pt.pdf" download>Portuguese résumé (PDF)</a>'
        h += f'<a class="button secondary" href="mailto:{escape(r["email"])}">Email me</a></div><p>{escape(r["summary"])}</p>'
        h += '<h2>Technical skills</h2>' + ''.join(f'<p><strong>{escape(k)}:</strong> {escape(v)}</p>' for k, v in r['skills'])
        h += '<h2>Professional experience</h2>'
        for ex in r['experience']:
            h += f'<h3>{escape(ex["role"])} | {escape(ex["organization"])}</h3><p>{escape(ex["dates"])}</p><ul>'
            h += ''.join('<li>' + escape(x) + '</li>' for x in ex['bullets']) + '</ul>'
        h += '<h2>Selected personal projects</h2>'
        for project in r['projects']:
            h += f'<h3><a href="{escape(project["url"], quote=True)}">{escape(project["name"])}</a></h3><p>{escape(project["text"])}</p><p><a href="{escape(project["repo"], quote=True)}">Source repository</a> · <a href="{escape(project["demo"], quote=True)}">Interactive demonstration</a></p>'
        h += f'<p><strong><a href="{escape(com["url"], quote=True)}">{escape(com["label"])}</a>:</strong> {escape(com["text"])}</p>'
        h += '<h2>Education</h2><p>' + escape(r['education']) + '</p><h2>Selected training</h2><ul>'
        h += ''.join('<li>' + escape(x) + '</li>' for x in r['training']) + '</ul>'
        h += '<p class="small">Listed as completed courses and modules, not as a Microsoft professional certification.</p>'
        h += '<h2>Languages</h2><p>' + escape(r['languages']) + '</p>'
        (out / 'index.html').write_text(page('Résumé', 'Data analysis experience, selected training, personal projects and English or Portuguese résumé downloads.', h, 'resume/'), encoding='utf-8')
    print('Built English and Portuguese résumés, with selected courses and consistent career facts.')
