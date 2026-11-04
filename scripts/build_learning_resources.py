"""Build the public learning resources from reviewed English sources."""
from __future__ import annotations

from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import zipfile

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.lang import MSO_LANGUAGE_ID
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'public/blog/exemplos'
OUT = ROOT / 'public/blog/downloads'
STAMP = (2026, 11, 3, 0, 0, 0)


def zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            if name.startswith('/') or '..' in Path(name).parts:
                raise ValueError('Unsafe archive member')
            info = zipfile.ZipInfo(name, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    return buffer.getvalue()


def examples() -> bytes:
    # An explicit allowlist keeps correspondence, reports and unrelated files out.
    mapping = {
        'run_examples.py': 'run_examples.py',
        'csv-validation/validate_sales.py': 'validacao-csv/validate_sales.py',
        'csv-validation/test_validate_sales.py': 'validacao-csv/test_validate_sales.py',
        'csv-validation/test_output_safety.py': 'validacao-csv/test_output_safety.py',
        'csv-validation/sales_valid.csv': 'validacao-csv/sales_valid.csv',
        'csv-validation/sales_invalid.csv': 'validacao-csv/sales_invalid.csv',
        'csv-validation/README.md': 'validacao-csv/README.md',
        'revisions/revision_demo.py': 'revisoes/revision_demo.py',
        'revisions/test_revision_demo.py': 'revisoes/test_revision_demo.py',
        'revisions/README.md': 'revisoes/README.md',
    }
    files = {name: (SOURCE/path).read_bytes() for name, path in mapping.items()}
    files['run_examples.py'] = files['run_examples.py'].replace(b"ROOT / 'validacao-csv', ROOT / 'revisoes'", b"ROOT / 'csv-validation', ROOT / 'revisions'")
    files['README.md'] = (ROOT/'content/examples-readme.md').read_bytes()
    manifest = ''.join(f'{hashlib.sha256(data).hexdigest()}  {name}\n' for name, data in sorted(files.items()))
    files['SHA256SUMS.txt'] = manifest.encode()
    return zip_bytes(files)


def presentation() -> bytes:
    deck = Presentation()
    deck.slide_width, deck.slide_height = Inches(13.333333), Inches(7.5)
    props = deck.core_properties
    props.title = 'Is your CSV ready for analysis?'
    props.subject = 'Practical CSV validation with Python'
    props.author = props.last_modified_by = 'Maurício Taguchi'
    props.keywords = 'Python, CSV, data quality, reproducible examples'
    props.comments = ''
    props.created = props.modified = datetime(*STAMP)
    ink, blue, gray, paper = '161719', '3148F6', '65666A', 'F5F5F3'

    def text(slide, x, y, w, h, value, size=24, color=ink, bold=False, font='Arial'):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0)
        tf.margin_top = tf.margin_bottom = Inches(0)
        for i, line in enumerate(value.split('\n')):
            paragraph = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            paragraph.text = line
            paragraph.space_after = Pt(8)
            for run in paragraph.runs:
                run.font.name, run.font.size = font, Pt(size)
                run.font.bold = bold
                run.font.color.rgb = RGBColor.from_string(color)
                run.font.language_id = MSO_LANGUAGE_ID.ENGLISH_US
        return box

    def line(slide, x, y, w):
        shape = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(.012))
        shape.fill.solid(); shape.fill.fore_color.rgb = RGBColor.from_string('D8D8D4')
        shape.line.fill.background()

    slides = json.loads((ROOT/'content/slides.json').read_text(encoding='utf-8'))
    for number, content in enumerate(slides, 1):
        slide = deck.slides.add_slide(deck.slide_layouts[6])
        slide.background.fill.solid(); slide.background.fill.fore_color.rgb = RGBColor.from_string(paper)
        text(slide,.65,.35,1,.5,'MT.',27,blue,True)
        text(slide,10.2,.45,2.4,.3,'DATA / PYTHON',12,gray)
        text(slide,.65,1.2,12,1.55,content['title'],42 if content['kind']!='cover' else 50)
        kind=content['kind']
        if kind=='cover':
            text(slide,.65,3.55,11.8,.6,content['subtitle'],28,blue)
            text(slide,.65,4.45,11.8,1.1,'\n'.join(content['body']),24,gray)
        elif kind=='columns':
            for i,(label,detail) in enumerate(content['items']):
                x=.65+i*4.05
                line(slide,x,3.2,3.55)
                text(slide,x,3.55,3.7,.85,label,36 if len(label)<3 else 25,blue)
                text(slide,x,4.55,3.6,1.5,detail,23)
        elif kind=='rows':
            for i,(label,detail) in enumerate(content['items']):
                y=3.0+i*1.0
                line(slide,.65,y,12)
                text(slide,.65,y+.22,2.6,.55,label,24,blue)
                text(slide,3.5,y+.22,8.9,.75,detail,22)
        elif kind=='code':
            wide=number==5
            text(slide,.85,3.0,11.6 if wide else 8.5,3.0,content['code'],16 if wide else 20,ink,font='Consolas')
            if not wide:text(slide,10,3.1,2.5,2.4,content['aside'],24,blue)
            else:text(slide,9.2,5.65,3.1,.7,content['aside'].replace('\n',' · '),15,gray)
        elif kind=='number':
            text(slide,.65,2.85,3.7,1.8,content['number'],108,blue)
            text(slide,.65,4.8,3.7,.7,content['subtitle'],23)
            text(slide,5.0,3.05,7.5,3.1,'\n'.join(content['body']),23)
        elif kind=='closing':
            text(slide,.65,3.35,12,2.6,'\n'.join(content['body']),21,blue)
        if content.get('footnote'):text(slide,.65,6.28,12,.45,content['footnote'],15,gray)
        line(slide,.65,6.87,12)
        text(slide,.65,7.02,11,.25,'Maurício Taguchi · synthetic-data examples',11,gray)
        text(slide,12.05,6.98,.6,.35,f'{number:02d}',15,blue)
        slide.notes_slide.notes_text_frame.text=content['notes']
    raw=io.BytesIO();deck.save(raw)
    # Normalize archive times so unchanged English sources produce stable downloads.
    with zipfile.ZipFile(io.BytesIO(raw.getvalue())) as archive:
        return zip_bytes({name:archive.read(name) for name in archive.namelist()})


def main() -> None:
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'technical-examples.zip').write_bytes(examples())
    (OUT/'csv-validation-slides.pptx').write_bytes(presentation())
    for name in ['study-guide.md','presentation-script.md','learning-plan.md']:
        (OUT/name).write_bytes((ROOT/'content'/name).read_bytes())
    print('Built complete examples, ten English slides and three learning guides.')

if __name__ == '__main__':
    main()
