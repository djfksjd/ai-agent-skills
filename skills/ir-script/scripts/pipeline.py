#!/usr/bin/env python3
"""Offline IR deck/script compiler. Research and visual QA belong to the host agent."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STATUSES = {'verified', 'user_provided', 'hypothesis', 'target', 'calculation', 'unverified'}
ACCESS = {'full_text', 'partial', 'metadata_only', 'unavailable'}
LABELS = {'verified': '확인', 'user_provided': '제공자료', 'hypothesis': '가설',
          'target': '목표', 'calculation': '계산', 'unverified': '미확인'}
ENDING = re.compile(r'(합니다|됩니다|했습니다|하겠습니다|있습니다|입니다)[.!?。]*$')
ID = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,31}$')


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    require(isinstance(data, dict), 'Root must be an object')
    return data


def dump(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value, field: str, maximum: int = 10000, empty: bool = False) -> str:
    require(isinstance(value, str), f'{field}: expected text')
    require((empty or bool(value.strip())) and len(value) <= maximum, f'{field}: empty or too long')
    require(not any(ord(c) < 32 and c not in '\n\t' for c in value), f'{field}: control character')
    return value


def number(value, field: str, minimum: float = 0) -> float:
    require(type(value) in (int, float) and math.isfinite(value) and value >= minimum,
            f'{field}: expected finite number >= {minimum}')
    return float(value)


def indexed(rows, field: str) -> dict:
    require(isinstance(rows, list), f'{field}: expected array')
    result = {}
    for row in rows:
        require(isinstance(row, dict), f'{field}: expected object')
        key = text(row.get('id'), field + '.id', 32)
        require(bool(ID.fullmatch(key)) and key not in result, f'{field}: invalid/duplicate ID {key}')
        result[key] = row
    return result


def refs(value, keys: dict, field: str) -> list:
    require(isinstance(value, list) and all(isinstance(v, str) for v in value), f'{field}: expected IDs')
    require(len(value) == len(set(value)), f'{field}: duplicate reference')
    require(all(v in keys for v in value), f'{field}: unknown reference')
    return value


def slide_map(data: dict) -> list:
    return [{k: s[k] for k in ('id', 'kind', 'title')} for s in data['slides']]


def timing(slide: dict, project: dict) -> float:
    spoken = slide['speaker_text'] + ' ' + slide['transition']
    units = len(re.sub(r'\s+', '', spoken)) if project['timing_unit'] == 'characters' else len(spoken.split())
    return round(units / project['timing_rate'] * 60 + slide['pause_seconds'], 1)


def validate(data: dict, strict_style: bool = False) -> dict:
    require(data.get('schema_version') == '1.0', 'schema_version must be 1.0')
    p = data.get('project')
    require(isinstance(p, dict), 'project required')
    for key in ('name', 'audience', 'stage', 'goal', 'language', 'font'):
        text(p.get(key), 'project.' + key, 200)
    number(p.get('duration_seconds'), 'duration_seconds', 1)
    number(p.get('timing_rate'), 'timing_rate', 1)
    require(p.get('timing_unit') in ('words', 'characters'), 'timing_unit must be words or characters')
    sources = indexed(data.get('sources'), 'sources')
    for s in sources.values():
        for key in ('title', 'publisher', 'url', 'retrieved', 'locator'):
            text(s.get(key), 'source.' + key, 2000)
        require(s.get('access') in ACCESS, 'Invalid source access')
        require(bool(re.match(r'^(https?://|local:)', s['url'])), 'Unsupported source URL')
        require(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', s['retrieved'])), 'retrieved: use YYYY-MM-DD')
    claims = indexed(data.get('claims'), 'claims')
    for c in claims.values():
        text(c.get('text'), 'claim.text', 2000)
        require(c.get('status') in STATUSES, 'Invalid claim status')
        ids = refs(c.get('source_ids'), sources, 'claim.source_ids')
        text(c.get('locator'), 'claim.locator', 2000)
        if c['status'] == 'verified':
            require(bool(ids), 'Verified claim requires evidence')
            require(all(sources[i]['access'] in ('full_text', 'partial') for i in ids),
                    'Metadata/unavailable evidence cannot verify a claim')
        if c['status'] == 'calculation':
            text(c.get('formula'), 'calculation.formula', 2000)
    slides = indexed(data.get('slides'), 'slides')
    require(0 < len(slides) <= 100, 'Expected 1..100 slides')
    appendix_started = False
    warnings, estimates = [], []
    for s in slides.values():
        require(s.get('kind') in ('main', 'appendix'), 'Invalid slide kind')
        appendix_started = appendix_started or s['kind'] == 'appendix'
        require(not (appendix_started and s['kind'] == 'main'), 'Main slide after appendix')
        for key, maximum in (('title', 55), ('role', 100), ('takeaway', 90), ('speaker_text', 7000)):
            text(s.get(key), s['id'] + '.' + key, maximum)
        for key in ('cue', 'transition'):
            text(s.get(key), s['id'] + '.' + key, 1000, empty=True)
        require(s.get('layout') in ('cover', 'columns', 'process'), 'Unsupported baseline layout')
        bullets = s.get('bullets')
        require(isinstance(bullets, list) and 1 <= len(bullets) <= 3, 'Baseline allows 1..3 body points')
        for item in bullets:
            text(item, 'body point', 70)
        require(all('\n' not in x for x in [s['title'], s['takeaway']] + bullets), 'Visible text: no manual line breaks')
        refs(s.get('claim_ids'), claims, 'slide.claim_ids')
        number(s.get('seconds'), 'slide.seconds', 1)
        number(s.get('pause_seconds'), 'pause_seconds')
        estimate = timing(s, p)
        estimates.append({'id': s['id'], 'planned': s['seconds'], 'estimated': estimate})
        if s['kind'] == 'main' and estimate > s['seconds'] * 1.2:
            warnings.append(s['id'] + ': script estimate exceeds planned time by >20%')
        if ENDING.search(s['title'].strip()):
            message = s['id'] + ': review report-like Korean headline ending'
            if strict_style and not s.get('allow_sentence_title', False):
                raise ValueError(message)
            warnings.append(message)
        if re.search(r'혁신적|압도적|세계 최초|유일한|완벽한', s['title']):
            warnings.append(s['id'] + ': substantiate or remove superlative')
    main = [s for s in slides.values() if s['kind'] == 'main']
    require(bool(main), 'At least one main slide required')
    require(sum(s['seconds'] for s in main) <= p['duration_seconds'], 'Main timing exceeds talk budget')
    qa = data.get('qa')
    require(isinstance(qa, list), 'qa must be an array')
    for q in qa:
        require(isinstance(q, dict), 'qa: expected object')
        for k in ('question', 'answer', 'uncertainty'):
            text(q.get(k), 'qa.' + k, 5000, empty=(k == 'uncertainty'))
        refs(q.get('claim_ids'), claims, 'qa.claim_ids')
        require(q.get('appendix_id') in slides and slides[q['appendix_id']]['kind'] == 'appendix',
                'Q&A requires a real appendix ID')
    return {'status': 'passed', 'warnings': warnings, 'timing': estimates,
            'timing_method': 'Adjustable estimate, not a measured rehearsal',
            'visual_review': 'pending', 'fact_verification': 'requires human/agent source review'}


def check_sync(deck: dict, script: dict) -> None:
    require(slide_map(deck) == script.get('slides'), 'Slide/script count, order, title or appendix mismatch')


def render_pptx(data: dict, out: Path) -> None:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.oxml.xmlchemy import OxmlElement
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    claims = {c['id']: c for c in data['claims']}
    sources = {s['id']: s for s in data['sources']}
    font = data['project']['font']
    def box(slide, value, x, y, w, h, size, bold=False, rgb='202020'):
        shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = 0
        tf.margin_top = tf.margin_bottom = 0
        paragraph = tf.paragraphs[0]
        paragraph.text = value
        paragraph.font.name, paragraph.font.size = font, Pt(size)
        paragraph.font.bold = bold
        paragraph.font.color.rgb = RGBColor.from_string(rgb)
        # Preserve East Asian font choice across Office/LibreOffice.
        for run in paragraph.runs:
            ea = OxmlElement('a:ea'); ea.set('typeface', font)
            run._r.get_or_add_rPr().append(ea)
        return shape
    for idx, s in enumerate(data['slides'], 1):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid(); slide.background.fill.fore_color.rgb = RGBColor(255, 255, 255)
        box(slide, data['project']['name'] + '  /  ' + s['role'], .65, .35, 12, .32, 11)
        box(slide, s['title'], .65, 1, 12, 1.1, 32, True)
        if s['layout'] == 'cover':
            box(slide, s['takeaway'], .65, 2.55, 11.4, 1.2, 25)
            for j, b in enumerate(s['bullets']):
                box(slide, b, .65, 4.15 + .56*j, 11.6, .45, 17)
        elif s['layout'] == 'columns':
            box(slide, s['takeaway'], .65, 2.65, 5.1, 2.4, 27, True)
            for j, b in enumerate(s['bullets']):
                box(slide, f'0{j+1}', 6.45, 2.65 + j*1.0, .5, .4, 14)
                box(slide, b, 7.05, 2.58 + j*1.0, 5.55, .88, 18)
        else:
            box(slide, s['takeaway'], .65, 2.4, 12, .8, 24)
            count = len(s['bullets']); width = 11.6/count
            for j, b in enumerate(s['bullets']):
                x = .65 + j*width
                rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(3.7), Inches(width-.25), Inches(1.8))
                rect.fill.solid(); rect.fill.fore_color.rgb = RGBColor(246, 246, 246)
                rect.line.fill.background()
                box(slide, f'0{j+1}', x+.15, 3.9, width-.5, .32, 12, True)
                box(slide, b, x+.15, 4.4, width-.55, .85, 18)
        foot = ' · '.join(c + ':' + LABELS[claims[c]['status']] for c in s['claim_ids'])
        box(slide, foot or '출처/상태: 별도 확인', .65, 6.63, 11.7, .55, 10, rgb='666666')
        box(slide, f'{s["id"]}  |  {idx:02d}', 11.7, 7.08, 1, .23, 9)
        note = [f'IR_SCRIPT_ID:{s["id"]}', f'KIND:{s["kind"]}', s['title'],
                'SPEAKER', s['speaker_text'], 'TRANSITION', s['transition'], 'CUE', s['cue']]
        for cid in s['claim_ids']:
            c = claims[cid]
            note.append(f'[{cid}] {c["status"]}: {c["text"]} / {c["locator"]}')
            for sid in c['source_ids']:
                src = sources[sid]
                note.append(f'[{sid}] {src["title"]} | {src["url"]} | {src["locator"]} | retrieved {src["retrieved"]}')
        slide.notes_slide.notes_text_frame.text = '\n'.join(note)
    prs.save(out)


def render_docx(data: dict, out: Path) -> None:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    doc = Document()
    sec = doc.sections[0]; sec.top_margin = sec.bottom_margin = Inches(.7)
    for style in ('Normal', 'Title', 'Heading 1', 'Heading 2'):
        st = doc.styles[style]; st.font.name = data['project']['font']
        st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), data['project']['font'])
    doc.styles['Normal'].font.size = Pt(11)
    doc.styles['Normal'].paragraph_format.space_after = Pt(8)
    doc.add_heading(data['project']['name'] + ' / 발표대본', 0)
    doc.add_paragraph('낭독문과 진행 안내를 구분. 계획 시간은 리허설 결과가 아닌 편집 기준.')
    for i, s in enumerate(data['slides']):
        if i: doc.add_page_break()
        doc.add_heading(f'[{s["id"]}] {s["title"]}', 1)
        doc.add_paragraph(f'{s["kind"]} | 계획 {s["seconds"]}초 | 추정 {timing(s, data["project"])}초')
        doc.add_paragraph(s['speaker_text'])
        doc.add_heading('다음 장 연결', 2); doc.add_paragraph(s['transition'] or '없음')
        doc.add_heading('진행 안내 · 읽지 않음', 2); doc.add_paragraph(s['cue'] or '없음')
        for c in data['claims']:
            if c['id'] in s['claim_ids']:
                doc.add_paragraph(f'[{c["id"]}] {LABELS[c["status"]]} | {c["text"]} | {c["locator"]}')
    footer = sec.footer.paragraphs[0]; footer.add_run('IR & SCRIPT  |  ')
    field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), 'PAGE'); footer._p.append(field)
    doc.save(out)


def convert_pdf(path: Path, out: Path) -> None:
    binary = shutil.which('libreoffice') or shutil.which('soffice')
    require(bool(binary), '--pdf requires LibreOffice/soffice on PATH')
    with tempfile.TemporaryDirectory(prefix='ir-lo-') as temp:
        profile = Path(temp).as_uri()
        result = subprocess.run([binary, '-env:UserInstallation=' + profile, '--headless',
                                 '--convert-to', 'pdf', '--outdir', str(out), str(path)],
                                capture_output=True, text=True, timeout=120)
    pdf = out / (path.stem + '.pdf')
    require(result.returncode == 0 and pdf.is_file() and pdf.stat().st_size > 100,
            'PDF conversion failed: ' + result.stderr[-500:])


def build(data: dict, out: Path, pdf: bool = False, strict_style: bool = False) -> dict:
    report = validate(data, strict_style)
    require(not out.exists(), 'Output directory already exists; choose a new version')
    out = out.absolute(); out.parent.mkdir(parents=True, exist_ok=True)
    if pdf:
        require(bool(shutil.which('libreoffice') or shutil.which('soffice')), 'LibreOffice required')
    with tempfile.TemporaryDirectory(prefix='.ir-stage-', dir=out.parent) as temp:
        stage = Path(temp)
        dump(stage/'deck.json', data)
        render_pptx(data, stage/'deck.pptx'); render_docx(data, stage/'script.docx')
        script = ['# ' + data['project']['name'] + ' / 발표대본', '']
        for s in data['slides']:
            script += [f'## [{s["id"]}] {s["title"]}', f'<!-- kind:{s["kind"]} -->',
                       s['speaker_text'], '', '**다음 장** ' + s['transition'],
                       '**진행** ' + s['cue'], '']
        (stage/'script.md').write_text('\n'.join(script), encoding='utf-8')
        qa = ['# Q&A', '']
        for q in data['qa']:
            qa += ['## '+q['question'], q['answer'], '\n부록: '+q['appendix_id'],
                   '근거: '+', '.join(q['claim_ids']), '남은 확인: '+q['uncertainty'], '']
        (stage/'qa.md').write_text('\n'.join(qa), encoding='utf-8')
        with (stage/'claims.csv').open('w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f); writer.writerow(['id','status','text','source_ids','locator','formula'])
            for c in data['claims']:
                cells = [c['id'],c['status'],c['text'],';'.join(c['source_ids']),c['locator'],c.get('formula','')]
                writer.writerow(["'"+x if x.startswith(('=', '+', '-', '@')) else x for x in cells])
        dump(stage/'qa-report.json', report)
        if pdf:
            convert_pdf(stage/'deck.pptx', stage); convert_pdf(stage/'script.docx', stage)
        manifest = {'version': '1.0', 'slides': slide_map(data),
                    'files': {p.name: digest(p) for p in sorted(stage.iterdir()) if p.is_file()},
                    'limits': 'Checksums detect changes; not digital signatures or visual verification.'}
        dump(stage/'manifest.json', manifest)
        verify(stage)
        shutil.copytree(stage, out)
    return report


def verify(out: Path) -> dict:
    from pptx import Presentation
    from docx import Document
    manifest = load(out/'manifest.json')
    require(isinstance(manifest.get('files'), dict), 'Invalid manifest')
    required = {'deck.json','deck.pptx','script.docx','script.md','qa.md','claims.csv','qa-report.json'}
    require(required <= set(manifest['files']), 'Manifest missing required outputs')
    for name, expected in manifest['files'].items():
        require(isinstance(name, str) and Path(name).name == name and name not in ('.', '..'), 'Unsafe manifest path')
        p = out/name
        require(p.is_file() and not p.is_symlink() and digest(p) == expected, 'Hash/missing file: ' + name)
    data = load(out/'deck.json'); validate(data); check_sync(data, manifest)
    ppt = Presentation(out/'deck.pptx')
    ids = [re.findall(r'^IR_SCRIPT_ID:(\S+)$', s.notes_slide.notes_text_frame.text, re.M) for s in ppt.slides]
    require(ids == [[s['id']] for s in data['slides']], 'PPTX note IDs/order mismatch')
    doc = Document(out/'script.docx')
    headings = [p.text for p in doc.paragraphs if p.style.name == 'Heading 1']
    require(headings == [f'[{s["id"]}] {s["title"]}' for s in data['slides']], 'DOCX heading mismatch')
    md = (out/'script.md').read_text(encoding='utf-8')
    require(re.findall(r'^## \[([^]]+)\]', md, re.M) == [s['id'] for s in data['slides']], 'Markdown ID mismatch')
    return {'status': 'passed', 'slides': len(data['slides']), 'files': len(manifest['files'])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for cmd in ('lint', 'build'):
        p = sub.add_parser(cmd); p.add_argument('input', type=Path)
        p.add_argument('--strict-style', action='store_true')
        if cmd == 'build':
            p.add_argument('--out', required=True, type=Path); p.add_argument('--pdf', action='store_true')
    p = sub.add_parser('verify'); p.add_argument('directory', type=Path)
    p = sub.add_parser('check-sync'); p.add_argument('deck', type=Path); p.add_argument('script_manifest', type=Path)
    a = parser.parse_args()
    try:
        if a.command == 'lint': result = validate(load(a.input), a.strict_style)
        elif a.command == 'build': result = build(load(a.input), a.out, a.pdf, a.strict_style)
        elif a.command == 'verify': result = verify(a.directory)
        else:
            check_sync(load(a.deck), load(a.script_manifest)); result = {'status':'passed'}
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr); return 2


if __name__ == '__main__':
    sys.exit(main())
