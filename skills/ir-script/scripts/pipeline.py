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
from datetime import date

VERSION = "1.0.0"
STATUSES = {"verified", "user_provided", "hypothesis", "target", "calculation", "unverified"}
ACCESS = {"full_text", "partial", "metadata_only", "unavailable"}
LABEL = dict(zip(sorted(STATUSES), ["계산", "가설", "목표", "미확인", "제공 자료", "출처 확인"]))
TITLE_END = re.compile(r"(합니다|됩니다|했습니다|하겠습니다|하고 있습니다)[.!?]?$")
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,39}$")


def read_json(path: Path) -> dict:
    def reject(value):
        raise ValueError(f"Non-finite JSON value: {value}")
    value = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def number(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def slide_manifest(deck: dict) -> list[dict]:
    return [{k: s[k] for k in ("id", "kind", "title")} for s in deck["slides"]]


def lint(deck: dict, strict_style: bool = False) -> dict:
    errors, warnings, timing = [], [], []
    def error(msg): errors.append(msg)
    for field in ("title", "language", "audience", "purpose", "font", "as_of"):
        if not text(deck.get(field)): error(f"Missing text: {field}")
    try: date.fromisoformat(deck.get("as_of", ""))
    except (ValueError, TypeError): error("as_of must be YYYY-MM-DD")
    if not number(deck.get("talk_seconds")) or deck.get("talk_seconds", 0) <= 0:
        error("talk_seconds must be positive; exclude Q&A")
    rate = deck.get("timing", {})
    if not isinstance(rate, dict):
        error("timing must be an object"); rate = {}
    cps, wpm = rate.get("ko_chars_per_second", 5), rate.get("en_words_per_minute", 130)
    if not number(cps) or cps <= 0: error("Invalid Korean timing rate"); cps = 5
    if not number(wpm) or wpm <= 0: error("Invalid English timing rate"); wpm = 130
    if not deck.get("timing"): warnings.append("Default timing rates are estimates, not rehearsal results")
    maps = {}
    for collection in ("sources", "claims", "slides", "qa"):
        items = deck.get(collection, [])
        if not isinstance(items, list) or len(items) > 500:
            error(f"{collection} must be a bounded list"); items = []
        maps[collection] = {}
        for item in items:
            if not isinstance(item, dict): error(f"{collection}: item must be object"); continue
            ident = item.get("id", "")
            if not isinstance(ident, str) or not ID.fullmatch(ident): error(f"{collection}: invalid ID"); continue
            if ident in maps[collection]: error(f"{collection}: duplicate ID {ident}")
            maps[collection][ident] = item
    sources, claims, slides, qa = (maps[k] for k in ("sources", "claims", "slides", "qa"))
    if not slides: error("At least one slide required")
    for ident, source in sources.items():
        for field in ("title", "url", "publisher", "retrieved_at", "observed_scope"):
            if not text(source.get(field)): error(f"{ident}: missing {field}")
        if source.get("access") not in ACCESS: error(f"{ident}: invalid access")
        if not re.match(r"^(https?://|user-file:)", str(source.get("url", ""))): error(f"{ident}: unsupported source URL")
        try: date.fromisoformat(source.get("retrieved_at", ""))
        except (ValueError, TypeError): error(f"{ident}: invalid retrieval date")
    def references(item, key, mapping):
        values = item.get(key, [])
        if not isinstance(values, list) or any(not isinstance(x, str) for x in values):
            error(f"{item['id']}: {key} must be string list"); return []
        for ref in values:
            if ref not in mapping: error(f"{item['id']}: unknown {key} {ref}")
        return values
    for ident, claim in claims.items():
        if not text(claim.get("text")): error(f"{ident}: missing claim text")
        if claim.get("status") not in STATUSES: error(f"{ident}: invalid claim status")
        refs = references(claim, "source_ids", sources)
        if claim.get("status") == "verified":
            if not refs or not text(claim.get("locator")): error(f"{ident}: verified claim needs source and locator")
            if any(sources.get(x, {}).get("access") in ("metadata_only", "unavailable") for x in refs):
                error(f"{ident}: metadata/unavailable source cannot verify a substantive claim")
        if claim.get("status") == "calculation":
            if not text(claim.get("formula")) or not text(claim.get("assumptions")):
                error(f"{ident}: calculation needs formula and assumptions")
    appendix_seen, planned, mains = False, 0, 0
    for ident, slide in slides.items():
        kind = slide.get("kind")
        if kind not in ("main", "appendix"): error(f"{ident}: invalid kind")
        if kind == "appendix": appendix_seen = True
        if kind == "main":
            mains += 1
            if appendix_seen: error(f"{ident}: main slide after appendix")
        for field in ("title", "role", "takeaway", "speaker_text", "cue", "transition"):
            if not isinstance(slide.get(field), str): error(f"{ident}: missing string {field}")
        title = slide.get("title", "")
        if not text(title): error(f"{ident}: empty title")
        if isinstance(title, str):
            if len(title) > 60: error(f"{ident}: title exceeds baseline layout limit of 60 characters")
            if TITLE_END.search(title) and not slide.get("allow_sentence_title", False):
                (errors if strict_style else warnings).append(f"{ident}: review explanatory headline ending")
            if any(x in title for x in ("혁신적", "압도적", "완벽한", "game-changing")):
                warnings.append(f"{ident}: substantiate or remove promotional wording")
        for field, limit in (("takeaway", 140), ("speaker_text", 3500), ("cue", 400), ("transition", 600)):
            if isinstance(slide.get(field), str) and len(slide[field]) > limit: error(f"{ident}: {field} too long for baseline")
        bullets = slide.get("bullets", [])
        if not isinstance(bullets, list) or len(bullets) > 4 or any(not text(b) or len(b) > 120 for b in bullets):
            error(f"{ident}: use at most four nonempty points, each <=120 characters")
        refs = references(slide, "claim_ids", claims)
        if len(refs) > 5: error(f"{ident}: at most five claims per baseline slide")
        if not refs: warnings.append(f"{ident}: no claim IDs; manually check factual statements")
        sec, pause = slide.get("seconds"), slide.get("pause_seconds", 0)
        if not number(sec) or not number(pause): error(f"{ident}: invalid duration"); continue
        if pause > sec: error(f"{ident}: pause exceeds allocated seconds")
        script = str(slide.get("speaker_text", "")) + " " + str(slide.get("transition", ""))
        units = len(re.sub(r"\s", "", script)) if deck.get("language", "").startswith("ko") else len(script.split())
        estimate = units / cps if deck.get("language", "").startswith("ko") else units / wpm * 60
        estimate += pause
        timing.append({"id": ident, "planned_seconds": sec, "estimated_seconds": round(estimate, 1)})
        if estimate > sec * 1.2: warnings.append(f"{ident}: estimated script longer than allocation; rehearse")
        if kind == "main": planned += sec
    if not mains: error("At least one main slide required")
    if number(deck.get("talk_seconds")) and planned > deck["talk_seconds"]:
        error("Main slide allocations exceed talk_seconds")
    for ident, item in qa.items():
        for field in ("question", "answer", "uncertainty"):
            if not isinstance(item.get(field), str): error(f"{ident}: missing {field}")
        references(item, "claim_ids", claims)
        for ref in references(item, "appendix_ids", slides):
            if slides.get(ref, {}).get("kind") != "appendix": error(f"{ident}: Q&A must reference appendix IDs")
    return {"version": VERSION, "errors": errors, "warnings": warnings, "main_count": mains,
            "appendix_count": len(slides) - mains, "planned_seconds": planned, "timing": timing,
            "visual_review": "pending", "factual_review": "not_performed_by_compiler"}


def evidence(deck: dict, slide: dict) -> str:
    claims = {c["id"]: c for c in deck.get("claims", [])}
    sources = {s["id"]: s for s in deck.get("sources", [])}
    out = []
    for ident in slide.get("claim_ids", []):
        c = claims[ident]
        out.append(f"[{ident} / {LABEL[c['status']]}] {c['text']}")
        if c.get("locator"): out.append("위치: " + c["locator"])
        if c.get("formula"): out.append("계산: " + c["formula"] + " | 가정: " + c["assumptions"])
        for sid in c.get("source_ids", []):
            s = sources[sid]
            out.append(f"[{sid}] {s['title']} | {s['url']} | {s['retrieved_at']} | {s['access']}")
    return "\n".join(out) or "연결된 주장 없음 / 내용별 근거 검토 필요"


def slide_notes(deck, s):
    return f"IR_SCRIPT_ID: {s['id']}\nKIND: {s['kind']}\nTITLE: {s['title']}\n\n[발표]\n{s['speaker_text']}\n\n[전환]\n{s['transition']}\n\n[진행 - 낭독 제외]\n{s['cue']}\n\n[근거 - 낭독 제외]\n{evidence(deck, s)}"


def make_pptx(deck: dict, path: Path) -> None:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333333), Inches(7.5)
    prs.core_properties.title = deck["title"]
    prs.core_properties.author = "IR & SCRIPT"
    def box(slide, content, x, y, w, h, size, bold=False, grey=32, name=None):
        shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        if name: shape.name = name
        tf = shape.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.text = content
        for p in tf.paragraphs:
            p.font.name = deck["font"]; p.font.size = Pt(size); p.font.bold = bold
            p.font.color.rgb = RGBColor(grey, grey, grey)
        return shape
    claims = {c["id"]: c for c in deck.get("claims", [])}
    for i, s in enumerate(deck["slides"], 1):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid(); slide.background.fill.fore_color.rgb = RGBColor(255, 255, 255)
        box(slide, f"{deck['title']}  /  {s['id']}  /  {s['kind']}", .65, .38, 12, .3, 11, grey=100)
        box(slide, s["title"], .65, 1.02, 12, 1.25, 31, True, name="IR_TITLE")
        box(slide, s["takeaway"], .65, 2.55, 11.9, 1.1, 22, name="IR_TAKEAWAY")
        for n, bullet in enumerate(s.get("bullets", [])):
            box(slide, f"{n+1:02d}  {bullet}", .68, 3.93 + n * .55, 11.9, .53, 16)
        status = " | ".join(f"{cid} {LABEL[claims[cid]['status']]}" for cid in s.get("claim_ids", []))
        box(slide, status or "근거 검토 필요", .65, 6.47, 12, .52, 10, grey=100)
        box(slide, f"{deck['as_of']}  |  근거·가정은 발표 노트 참조", .65, 7.04, 11, .2, 9, grey=110)
        box(slide, str(i), 12.1, 7.04, .5, .2, 9, grey=110)
        slide.notes_slide.notes_text_frame.text = slide_notes(deck, s)
    prs.save(str(path))


def make_docx(deck: dict, path: Path) -> None:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    doc = Document(); sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)
    sec.top_margin = sec.bottom_margin = Inches(.7)
    sec.left_margin = sec.right_margin = Inches(.8)
    for name in ("Normal", "Title", "Heading 1", "Heading 2"):
        st = doc.styles[name]; st.font.name = deck["font"]
        st.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), deck["font"])
    normal = doc.styles["Normal"]
    normal.font.size = Pt(11); normal.paragraph_format.line_spacing = 1.3
    normal.paragraph_format.space_after = Pt(8)
    doc.styles["Heading 1"].font.size = Pt(20)
    doc.styles["Heading 2"].font.size = Pt(12)
    for name in ("Title", "Heading 1", "Heading 2"):
        doc.styles[name].font.color.rgb = RGBColor(32, 32, 32)
    sec.header.paragraphs[0].text = f"IR & SCRIPT / {deck['title']} / {deck['as_of']}"
    footer = sec.footer.paragraphs[0]; footer.text = "발표대본  |  "
    field = OxmlElement("w:fldSimple"); field.set(qn("w:instr"), "PAGE"); footer._p.append(field)
    for i, s in enumerate(deck["slides"]):
        if i: doc.add_page_break()
        doc.add_heading(f"[{s['id']}] {s['title']}", 1)
        doc.add_paragraph(f"{s['kind']} · 배정 {s['seconds']}초 · 멈춤 {s.get('pause_seconds', 0)}초 포함")
        doc.add_heading("발표", 2)
        doc.add_paragraph(s["speaker_text"])
        doc.add_heading("전환", 2); doc.add_paragraph(s["transition"] or "전환 문장 없음")
        doc.add_heading("진행 안내 · 낭독 제외", 2); doc.add_paragraph(s["cue"] or "별도 안내 없음")
        doc.add_heading("근거와 확인 범위 · 낭독 제외", 2)
        p = doc.add_paragraph(evidence(deck, s))
        for r in p.runs: r.font.size = Pt(9); r.font.color.rgb = RGBColor(95, 95, 95)
    if deck.get("qa"):
        doc.add_page_break(); doc.add_heading("예상 질문", 1)
        for q in deck["qa"]:
            doc.add_heading(f"{q['id']} · {q['question']}", 2); doc.add_paragraph(q["answer"])
            doc.add_paragraph("연결 부록: " + ", ".join(q.get("appendix_ids", [])))
            doc.add_paragraph("확인할 점: " + q["uncertainty"])
    doc.core_properties.title = deck["title"] + " 발표대본"; doc.core_properties.author = "IR & SCRIPT"
    doc.save(str(path))


def markdowns(deck: dict, out: Path) -> None:
    parts = [f"# {deck['title']} 발표대본", "시간은 가정에 따른 추정이며 실제 리허설 결과가 아닙니다."]
    for s in deck["slides"]:
        parts += [f"## [{s['id']}] {s['title']}", f"{s['kind']} | {s['seconds']}초", s["speaker_text"],
                  "### 전환", s["transition"], "### 진행 - 낭독 제외", s["cue"], "### 근거 - 낭독 제외", evidence(deck, s)]
    (out / "script.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    parts = [f"# {deck['title']} 예상 질문"]
    for q in deck.get("qa", []):
        parts += [f"## {q['id']} {q['question']}", q["answer"], "부록: " + ", ".join(q.get("appendix_ids", [])),
                  "주장: " + ", ".join(q.get("claim_ids", [])), "확인할 점: " + q["uncertainty"]]
    (out / "qa.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    with (out / "claims.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle); writer.writerow(["id", "status", "text", "sources", "locator", "formula", "assumptions"])
        for c in deck.get("claims", []):
            values = [c["id"], c["status"], c["text"], ",".join(c.get("source_ids", [])), c.get("locator", ""), c.get("formula", ""), c.get("assumptions", "")]
            writer.writerow(["'" + v if v.lstrip().startswith(("=", "+", "-", "@")) else v for v in values])


def convert_pdf(out: Path) -> None:
    executable = shutil.which("libreoffice") or shutil.which("soffice")
    if not executable: raise RuntimeError("PDF requested but LibreOffice/soffice is not installed")
    with tempfile.TemporaryDirectory(prefix="ir-lo-") as profile:
        for name in ("deck.pptx", "script.docx"):
            cmd = [executable, "-env:UserInstallation=" + Path(profile).as_uri(), "--headless", "--convert-to", "pdf", "--outdir", str(out), str(out / name)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
            dest = out / (Path(name).stem + ".pdf")
            if result.returncode or not dest.exists() or not dest.read_bytes().startswith(b"%PDF"):
                raise RuntimeError(f"PDF conversion failed: {name}; {result.stderr[-1000:]}")


def build(deck: dict, out: Path, pdf=False, strict_style=False) -> dict:
    report = lint(deck, strict_style)
    if report["errors"]: raise ValueError("\n".join(report["errors"]))
    out = out.absolute()
    out.parent.mkdir(parents=True, exist_ok=True)
    # Reserve destination exclusively. Never remove/overwrite a pre-existing directory.
    out.mkdir(exist_ok=False)
    try:
        with tempfile.TemporaryDirectory(prefix=".ir-build-", dir=out.parent) as temp:
            work = Path(temp); dump(work / "deck.json", deck)
            make_pptx(deck, work / "deck.pptx"); make_docx(deck, work / "script.docx"); markdowns(deck, work)
            if pdf: convert_pdf(work)
            dump(work / "qa-report.json", report)
            files = {p.name: sha(p) for p in work.iterdir() if p.is_file()}
            dump(work / "manifest.json", {"schema_version": 1, "generator_version": VERSION, "slides": slide_manifest(deck), "files": files})
            for p in work.iterdir(): shutil.move(str(p), out / p.name)
    except Exception:
        # The exclusive directory belongs to this failed build, not to caller data.
        shutil.rmtree(out); raise
    return report


def verify(out: Path) -> dict:
    manifest = read_json(out / "manifest.json"); errors = []
    if manifest.get("schema_version") != 1: errors.append("Unknown manifest version")
    for name, expected in manifest.get("files", {}).items():
        if not isinstance(name, str) or Path(name).name != name or name in (".", "..") or "\\" in name:
            errors.append("Unsafe manifest path"); continue
        path = out / name
        if path.is_symlink() or not path.is_file() or sha(path) != expected: errors.append(f"Hash mismatch/missing: {name}")
    required = {"deck.json", "deck.pptx", "script.docx", "script.md", "qa.md", "claims.csv", "qa-report.json"}
    if not required.issubset(manifest.get("files", {})): errors.append("Missing required manifest entries")
    if errors: return {"errors": errors}
    deck = read_json(out / "deck.json")
    errors.extend(lint(deck)["errors"])
    if manifest.get("slides") != slide_manifest(deck): errors.append("Manifest slide mapping mismatch")
    from pptx import Presentation
    from docx import Document
    prs = Presentation(str(out / "deck.pptx"))
    if len(prs.slides) != len(deck["slides"]): errors.append("PPTX slide count mismatch")
    for actual, expected in zip(prs.slides, deck["slides"]):
        titles = [s.text for s in actual.shapes if s.name == "IR_TITLE"]
        if titles != [expected["title"]] or actual.notes_slide.notes_text_frame.text != slide_notes(deck, expected):
            errors.append(f"PPTX title/notes mismatch: {expected['id']}")
    doc = Document(str(out / "script.docx"))
    headers = [p.text for p in doc.paragraphs if re.match(r"^\[[A-Za-z][\w-]*\] ", p.text)]
    expected_headers = [f"[{s['id']}] {s['title']}" for s in deck["slides"]]
    if headers != expected_headers: errors.append("DOCX script order/title mismatch")
    return {"errors": errors, "slide_count": len(deck["slides"]), "visual_review": "not_established_by_hashes"}


def check_sync(deck: dict, script_manifest: dict) -> dict:
    expected, actual = slide_manifest(deck), script_manifest.get("slides")
    return {"errors": [] if expected == actual else ["Slide/script ID, order, title or main/appendix mismatch"],
            "expected": expected, "actual": actual}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("lint", "build"):
        p = sub.add_parser(name); p.add_argument("input", type=Path); p.add_argument("--strict-style", action="store_true")
        if name == "build": p.add_argument("--out", type=Path, required=True); p.add_argument("--pdf", action="store_true")
    p = sub.add_parser("verify"); p.add_argument("out", type=Path)
    p = sub.add_parser("check-sync"); p.add_argument("input", type=Path); p.add_argument("script_manifest", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "lint": result = lint(read_json(args.input), args.strict_style)
        elif args.command == "build": result = build(read_json(args.input), args.out, args.pdf, args.strict_style)
        elif args.command == "verify": result = verify(args.out)
        else: result = check_sync(read_json(args.input), read_json(args.script_manifest))
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 1 if result.get("errors") else 0
    except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
