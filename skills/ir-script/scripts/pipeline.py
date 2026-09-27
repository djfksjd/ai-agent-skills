#!/usr/bin/env python3
"""Offline IR deck/script compiler. Research and visual review remain human/agent tasks."""
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
from typing import Any

VERSION = '1.0.0'
STATUSES = {'verified', 'user_provided', 'hypothesis', 'target', 'calculation', 'unverified'}
ACCESS = {'full_text', 'partial', 'metadata_only', 'unavailable'}
LABELS = {'verified':'확인', 'user_provided':'제공 자료', 'hypothesis':'가설', 'target':'목표', 'calculation':'계산', 'unverified':'미확인'}
ID_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,39}$')
STYLE_RE = re.compile(r'(합니다|됩니다|했습니다|하겠습니다|하고 있습니다)[.!?。]?$')


def load(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding='utf-8'), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f'Non-finite JSON: {x}')))
    if not isinstance(data, dict):
        raise ValueError('JSON root must be an object')
    return data


def dump(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value: Any, positive: bool = False) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and (value > 0 if positive else value >= 0)


def require_text(obj: dict, key: str, context: str, errors: list[str], limit: int | None = None) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f'{context}.{key}: nonempty text required')
        return ''
    if any(ord(c) < 32 and c not in '\n\t' for c in value):
        errors.append(f'{context}.{key}: unsupported control character')
    if limit and len(value) > limit:
        errors.append(f'{context}.{key}: exceeds baseline capacity {limit}; simplify or use a richer renderer')
    return value


def lint(data: dict, strict_style: bool = False) -> dict:
    errors, warnings = [], []
    if data.get('schema_version') != 1:
        errors.append('schema_version must be 1')
    for key in ('company', 'language', 'audience', 'purpose', 'version', 'font'):
        require_text(data, key, 'deck', errors, 120)
    if not number(data.get('talk_seconds'), True):
        errors.append('talk_seconds must be finite and positive')
    rate = data.get('speech_rate_per_minute', 300 if data.get('language') == 'ko' else 130)
    if not number(rate, True):
        errors.append('speech_rate_per_minute must be positive')
        rate = 300
    collections = {}
    for key in ('sources', 'claims', 'slides', 'qa'):
        rows = data.get(key)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            errors.append(f'{key}: expected a list of objects')
            rows = []
        collections[key] = rows
    sources, claims, slides, qa = (collections[k] for k in ('sources','claims','slides','qa'))
    maps = {}
    for key, rows in collections.items():
        mapping = {}
        for i, row in enumerate(rows):
            ident = row.get('id')
            if not isinstance(ident, str) or not ID_RE.fullmatch(ident):
                errors.append(f'{key}[{i}]: invalid id')
                continue
            if ident in mapping:
                errors.append(f'{key}: duplicate id {ident}')
            mapping[ident] = row
        maps[key] = mapping
    for source in sources:
        ctx = f'source {source.get("id", "?")}'
        for field in ('title','url','publisher','retrieved_at','scope'):
            require_text(source, field, ctx, errors)
        if not isinstance(source.get('access'),str) or source.get('access') not in ACCESS:
            errors.append(f'{ctx}: invalid access')
    for claim in claims:
        ctx = f'claim {claim.get("id", "?")}'
        require_text(claim, 'text', ctx, errors)
        if not isinstance(claim.get('status'),str) or claim.get('status') not in STATUSES:
            errors.append(f'{ctx}: invalid status')
        evidence = claim.get('evidence', [])
        if not isinstance(evidence, list) or any(not isinstance(e,dict) for e in evidence):
            errors.append(f'{ctx}: evidence must be an array of objects'); evidence=[]
        if claim.get('status') == 'verified' and not evidence:
            errors.append(f'{ctx}: verified requires evidence')
        for e in evidence:
            sid=e.get('source_id'); source=maps['sources'].get(sid) if isinstance(sid,str) else None
            if not source:
                errors.append(f'{ctx}: unknown source {sid}')
            require_text(e, 'locator', ctx, errors)
            if claim.get('status') == 'verified' and source and source.get('access') not in ('full_text','partial'):
                errors.append(f'{ctx}: metadata/unavailable source cannot verify a claim')
        if claim.get('status') == 'calculation':
            require_text(claim, 'method', ctx, errors)
        if claim.get('status') != 'verified':
            require_text(claim, 'qualifier', ctx, errors)
    def claim_ids(row: dict, ctx: str) -> list:
        ids=row.get('claim_ids')
        if not isinstance(ids,list) or any(not isinstance(x,str) for x in ids):
            errors.append(f'{ctx}: claim_ids must be a string list'); return []
        for ident in ids:
            if ident not in maps['claims']: errors.append(f'{ctx}: unknown claim {ident}')
        return ids
    planned=0; estimated=0.0; appendix_seen=False; main_count=0
    for s in slides:
        ctx=f'slide {s.get("id", "?")}'
        title=require_text(s,'title',ctx,errors,70)
        for key, limit in (('takeaway',120),('role',80),('speaker_text',6000)):
            require_text(s,key,ctx,errors,limit)
        for key in ('cue','transition'):
            if not isinstance(s.get(key),str): errors.append(f'{ctx}.{key}: text required (empty allowed)')
        if s.get('layout','content') not in ('cover','content'):
            errors.append(f'{ctx}: baseline layout must be cover or content')
        bullets=s.get('bullets')
        if not isinstance(bullets,list) or len(bullets)>4 or any(not isinstance(x,str) or not x.strip() or len(x)>110 for x in bullets):
            errors.append(f'{ctx}: use 0-4 nonempty bullets of at most 110 characters')
        ids=claim_ids(s,ctx)
        if not ids: warnings.append(f'{ctx}: no linked claims; review all factual copy manually')
        if len(ids)>4: errors.append(f'{ctx}: at most 4 claims in baseline footer')
        if STYLE_RE.search(title) and not s.get('allow_sentence_title',False):
            (errors if strict_style else warnings).append(f'{ctx}: explanatory Korean headline; rewrite or document an intentional exception')
        if any(w in title for w in ('혁신적','압도적','완벽한','구분했습니다')):
            warnings.append(f'{ctx}: generic or editorial title; manual copy review')
        if not number(s.get('seconds')): errors.append(f'{ctx}: seconds must be nonnegative')
        if not number(s.get('pause_seconds',0)): errors.append(f'{ctx}: pause_seconds must be nonnegative')
        if s.get('kind')=='appendix': appendix_seen=True
        elif s.get('kind')=='main':
            main_count+=1
            if appendix_seen: errors.append(f'{ctx}: main slide after appendix')
            if number(s.get('seconds')): planned+=s['seconds']
            text=str(s.get('speaker_text',''))+' '+str(s.get('transition',''))
            units=len(re.sub(r'\s','',text)) if data.get('language')=='ko' else len(text.split())
            estimated+=units/rate*60+(s.get('pause_seconds',0) if number(s.get('pause_seconds',0)) else 0)
        else: errors.append(f'{ctx}: kind must be main or appendix')
    if not main_count: errors.append('at least one main slide required')
    if number(data.get('talk_seconds'),True) and planned>data['talk_seconds']:
        errors.append('planned main-slide seconds exceed talk_seconds')
    if number(data.get('talk_seconds'),True) and estimated>data['talk_seconds']:
        warnings.append('estimated speech exceeds talk_seconds; estimate is not rehearsal')
    for q in qa:
        ctx=f'qa {q.get("id", "?")}'
        for key in ('question','answer','uncertainty'): require_text(q,key,ctx,errors)
        claim_ids(q,ctx)
        a=maps['slides'].get(q.get('appendix_id')) if isinstance(q.get('appendix_id'),str) else None
        if not a or a.get('kind')!='appendix': errors.append(f'{ctx}: appendix_id must reference an appendix slide')
    return {'errors':errors,'warnings':warnings,'main_count':main_count,'appendix_count':len(slides)-main_count,
            'planned_main_seconds':planned,'estimated_speech_seconds':round(estimated,1),
            'timing_basis':f'{rate} '+('nonspace characters/minute' if data.get('language')=='ko' else 'words/minute'),
            'visual_review':'pending','factual_verification':'manual review required','rehearsal':'not performed'}


def sequence(data: dict) -> list[dict]:
    return [{k:s[k] for k in ('id','kind','title')} for s in data['slides']]


def check_sync(data: dict, script_manifest: dict) -> None:
    if sequence(data) != script_manifest.get('slides'):
        raise ValueError('Slide/script mismatch: count, order, title or main/appendix boundary differs')


def references(data: dict, slide: dict) -> str:
    cs={c['id']:c for c in data['claims']}; ss={s['id']:s for s in data['sources']}; lines=[]
    for ident in slide['claim_ids']:
        c=cs[ident]
        lines.append(f'[{ident}] {LABELS[c["status"]]}: {c["text"]}')
        if c.get('qualifier'): lines.append('범위: '+c['qualifier'])
        if c.get('method'): lines.append('계산: '+c['method'])
        for e in c.get('evidence',[]):
            src=ss[e['source_id']]
            lines.append(f'{src["id"]} | {src["publisher"]} | {src["title"]} | {e["locator"]} | {src["url"]} | 조회 {src["retrieved_at"]}')
    return '\n'.join(lines)


def notes(data: dict, s: dict) -> str:
    return f'IR_SCRIPT_ID:{s["id"]}\n{ s["kind"] } | {s["seconds"]}s\n\n발표\n{s["speaker_text"]}\n\n전환\n{s["transition"]}\n\n진행 (읽지 않음)\n{s["cue"]}\n\n근거 (읽지 않음)\n{references(data,s)}'


def create_pptx(data: dict, path: Path) -> None:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.oxml.xmlchemy import OxmlElement
    prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
    font=data['font']; cs={c['id']:c for c in data['claims']}
    def box(slide,text,x,y,w,h,size,bold=False,gray=False):
        sh=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
        tf=sh.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=0
        tf.margin_top=tf.margin_bottom=0
        for i,line in enumerate(text.split('\n')):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.text=line
            p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string('606060' if gray else '171717')
            p.space_after=Pt(8)
            for run in p.runs:
                rpr=run._r.get_or_add_rPr();ea=OxmlElement('a:ea');ea.set('typeface',font);rpr.append(ea)
        return sh
    for i,s in enumerate(data['slides'],1):
        sl=prs.slides.add_slide(prs.slide_layouts[6]);cover=s.get('layout')=='cover'
        box(sl,f'{data["company"]}   /   {s["role"]}',.6,.35,11.8,.35,11,gray=True)
        box(sl,s['title'],.6,1.0,12.0,1.35,34 if cover else 30,True)
        box(sl,s['takeaway'],.63,2.45,11.6,.9,21,gray=True)
        for j,b in enumerate(s['bullets']):
            box(sl,f'{j+1:02d}',.65,3.55+j*.62,.55,.43,12,gray=True)
            box(sl,b,1.3,3.5+j*.62,11.15,.55,19)
        statuses=' · '.join(f'{cid} {LABELS[cs[cid]["status"]]}' for cid in s['claim_ids']) or '근거 검토 필요'
        box(sl,statuses,.65,6.35,11.5,.4,10,gray=True)
        box(sl,f'{s["id"]} | {s["kind"]}   ·   {i:02d}   ·   {data["version"]}',.65,6.94,11.5,.3,10,gray=True)
        sl.notes_slide.notes_text_frame.text=notes(data,s)
    prs.core_properties.title=data['company']+' IR';prs.core_properties.subject='IR & SCRIPT '+data['version'];prs.core_properties.author=''
    prs.save(path)


def create_docx(data: dict, path: Path) -> None:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    doc=Document();sec=doc.sections[0];sec.top_margin=sec.bottom_margin=Inches(.65)
    sec.left_margin=sec.right_margin=Inches(.75)
    for name,size in [('Normal',11),('Title',23),('Heading 1',18),('Heading 2',12)]:
        st=doc.styles[name];st.font.name=data['font'];st.font.size=Pt(size);st.font.color.rgb=RGBColor(25,25,25)
        st.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),data['font'])
    doc.styles['Normal'].paragraph_format.space_after=Pt(7)
    doc.styles['Normal'].paragraph_format.line_spacing=1.18
    for i,s in enumerate(data['slides']):
        if i: doc.add_page_break()
        doc.add_paragraph(data['company']+' / SPEAKER SCRIPT',style='Subtitle')
        doc.add_heading(f'{s["id"]} | {s["title"]}',level=1)
        doc.add_paragraph(f'{s["kind"]} · 계획 {s["seconds"]}초 · {data["version"]}')
        doc.add_paragraph(s['speaker_text'])
        if s['transition']:doc.add_paragraph(s['transition'])
        doc.add_heading('진행 안내 / 읽지 않음',level=2);doc.add_paragraph(s['cue'] or '없음')
        doc.add_heading('근거와 확인 범위 / 읽지 않음',level=2);doc.add_paragraph(references(data,s) or '연결된 주장 없음')
    footer=sec.footer.paragraphs[0];footer.text='IR & SCRIPT   |   '
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
    doc.core_properties.author='';doc.core_properties.title=data['company']+' 발표대본'
    doc.save(path)


def build(data: dict, out: Path, pdf: bool=False, strict_style: bool=False) -> dict:
    report=lint(data,strict_style)
    if report['errors']:raise ValueError('\n'.join(report['errors']))
    out=out.expanduser().absolute()
    if out.exists() or out.is_symlink():raise FileExistsError(f'Refusing existing output: {out}')
    exe=shutil.which('libreoffice') or shutil.which('soffice')
    if pdf and not exe:raise RuntimeError('PDF requested, but LibreOffice is not installed/on PATH')
    out.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.ir-stage-',dir=out.parent))
    try:
        dump(stage/'deck.json',data)
        create_pptx(data,stage/'deck.pptx');create_docx(data,stage/'script.docx')
        md=[f'# {data["company"]} 발표대본',f'버전: {data["version"]} / 시간은 추정이며 리허설과 다름']
        for s in data['slides']:
            md += [f'\n## {s["id"]} | {s["title"]}',f'{s["kind"]} · 계획 {s["seconds"]}초',s['speaker_text'],s['transition'],f'\n진행 (읽지 않음): {s["cue"]}',f'\n근거 (읽지 않음):\n{references(data,s)}']
        (stage/'script.md').write_text('\n\n'.join(md)+'\n',encoding='utf-8')
        qm=['# 예상 질문 · 답변']
        for q in data['qa']:
            qm += [f'## {q["id"]} {q["question"]}',q['answer'],f'부록 {q["appendix_id"]} / 근거 {", ".join(q["claim_ids"])}',f'남은 확인: {q["uncertainty"]}']
        (stage/'qa.md').write_text('\n\n'.join(qm)+'\n',encoding='utf-8')
        with (stage/'claims.csv').open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.writer(f);w.writerow(['id','status','claim','qualifier','method','evidence'])
            def safe_cell(x):
                t=str(x);return "'"+t if t.startswith(('=','+','-','@','\t','\r')) else t
            for c in data['claims']:
                w.writerow([safe_cell(x) for x in [c['id'],c['status'],c['text'],c.get('qualifier',''),c.get('method',''),json.dumps(c.get('evidence',[]),ensure_ascii=False)]])
        if pdf:
            with tempfile.TemporaryDirectory(prefix='ir-lo-') as profile:
                for name in ('deck.pptx','script.docx'):
                    proc=subprocess.run([exe,f'-env:UserInstallation={Path(profile).as_uri()}','--headless','--convert-to','pdf','--outdir',str(stage),str(stage/name)],capture_output=True,text=True,timeout=120)
                    output=stage/(Path(name).stem+'.pdf')
                    if proc.returncode or not output.exists() or output.stat().st_size<100:
                        raise RuntimeError(f'PDF conversion failed: {name}\n{proc.stderr}\n{proc.stdout}')
        report['compiler_version']=VERSION
        report['pdf_conversion']='completed' if pdf else 'not requested'
        dump(stage/'qa-report.json',report)
        manifest={'compiler_version':VERSION,'slides':sequence(data),'files':{p.name:digest(p) for p in sorted(stage.iterdir()) if p.is_file()}}
        dump(stage/'manifest.json',manifest)
        verify(stage)
        if out.exists():raise FileExistsError(f'Output appeared during build: {out}')
        stage.rename(out)
        return report
    except Exception:
        shutil.rmtree(stage,ignore_errors=True)
        raise


def verify(out: Path) -> dict:
    from pptx import Presentation
    from docx import Document
    out=out.resolve();m=load(out/'manifest.json');files=m.get('files')
    required={'deck.json','deck.pptx','script.docx','script.md','qa.md','claims.csv','qa-report.json'}
    if not isinstance(files,dict) or not required.issubset(files):raise ValueError('Manifest missing required files')
    for name,expected in files.items():
        if not isinstance(name,str) or Path(name).name!=name or name in {'.','..'} or (out/name).is_symlink():
            raise ValueError('Unsafe manifest path')
        p=out/name
        if not p.is_file() or digest(p)!=expected:raise ValueError(f'Hash mismatch or missing: {name}')
    data=load(out/'deck.json')
    if lint(data)['errors']:raise ValueError('Canonical JSON no longer valid')
    check_sync(data,m)
    ppt=Presentation(out/'deck.pptx')
    ids=[]
    for s in ppt.slides:
        matches=re.findall(r'^IR_SCRIPT_ID:(\S+)\s*$',s.notes_slide.notes_text_frame.text,re.M)
        if len(matches)!=1:raise ValueError('Missing/duplicate PPTX note ID')
        ids.extend(matches)
    if ids != [s['id'] for s in data['slides']]:raise ValueError('PPTX notes sequence mismatch')
    headings=[p.text for p in Document(out/'script.docx').paragraphs if p.style.name=='Heading 1']
    if headings != [f'{s["id"]} | {s["title"]}' for s in data['slides']]:raise ValueError('DOCX sequence mismatch')
    return {'ok':True,'slides':len(ids),'checked_files':len(files),'scope':'Hashes and structure, not factual or visual verification'}


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    l=sub.add_parser('lint');l.add_argument('input');l.add_argument('--strict-style',action='store_true')
    b=sub.add_parser('build');b.add_argument('input');b.add_argument('--out',required=True);b.add_argument('--pdf',action='store_true');b.add_argument('--strict-style',action='store_true')
    v=sub.add_parser('verify');v.add_argument('out')
    c=sub.add_parser('check-sync');c.add_argument('input');c.add_argument('script_manifest')
    args=ap.parse_args()
    try:
        if args.command=='lint':
            result=lint(load(args.input),args.strict_style);print(json.dumps(result,ensure_ascii=False,indent=2));return 1 if result['errors'] else 0
        if args.command=='build':result=build(load(args.input),Path(args.out),args.pdf,args.strict_style)
        elif args.command=='verify':result=verify(Path(args.out))
        else:check_sync(load(args.input),load(args.script_manifest));result={'ok':True}
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,RuntimeError,ImportError,subprocess.TimeoutExpired) as e:
        print(f'ERROR: {e}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
