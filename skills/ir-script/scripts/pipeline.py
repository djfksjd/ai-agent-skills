#!/usr/bin/env python3
"""Offline IR compiler. Research, factual verification and visual QA remain human/agent tasks."""
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
import unicodedata
from datetime import date
from pathlib import Path

STATUSES = {"verified", "user_provided", "hypothesis", "target", "calculation", "unverified"}
ACCESS = {"full_text", "partial", "metadata_only", "unavailable"}
VIDEO_ACCESS = {"video_and_transcript", "transcript_only", "selected_frames", "metadata_only", "unavailable"}
TITLE_END = re.compile(r"(?:합니다|됩니다|했습니다|하겠습니다|있습니다)[.!?。]?$")
LABELS = {"verified": "확인", "user_provided": "제공자료", "hypothesis": "가설", "target": "목표", "calculation": "계산", "unverified": "미확인"}


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


def save(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positive(value: object, allow_zero: bool = False) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and (value >= 0 if allow_zero else value > 0)


def display_units(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in {"W", "F"} else 1 for c in text)


def signature(data: dict) -> list[dict]:
    return [{k: s[k] for k in ("id", "kind", "title")} for s in data["slides"]]


def spoken_seconds(slide: dict, rate: float) -> float:
    # Whitespace-separated units: Korean eojeol / English words, NOT a measured speech rate.
    units = len((slide.get("speaker_text", "") + " " + slide.get("transition", "")).split())
    return round(units / rate * 60 + slide.get("pause_seconds", 0), 1)


def lint(data: dict, strict_style: bool = False) -> dict:
    errors, warnings = [], []
    for key in ("company", "audience", "purpose", "language", "font", "release_date"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key}: nonempty string required")
    try:
        date.fromisoformat(data.get("release_date", ""))
    except (ValueError, TypeError):
        errors.append("release_date: YYYY-MM-DD required")
    rate = data.get("speech_units_per_minute", 120)
    if not positive(rate):
        errors.append("speech_units_per_minute must be positive"); rate = 120
    duration = data.get("duration_seconds")
    if not positive(duration):
        errors.append("duration_seconds must be positive"); duration = 0
    collections = {}
    for key in ("sources", "claims", "slides", "qa"):
        items = data.get(key, [])
        if not isinstance(items, list) or any(not isinstance(x, dict) for x in items):
            errors.append(f"{key}: list of objects required"); items = []
        collections[key] = items
    sources, claims, slides, qa = (collections[k] for k in ("sources", "claims", "slides", "qa"))
    if not slides:
        errors.append("slides: at least one main slide required")
    maps = {}
    for key, items in (("sources", sources), ("claims", claims), ("slides", slides)):
        index = {}
        for item in items:
            ident = item.get("id")
            if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", ident):
                errors.append(f"{key}: invalid id {ident!r}"); continue
            if ident in index:
                errors.append(f"{key}: duplicate id {ident}")
            index[ident] = item
        maps[key] = index
    for src in sources:
        sid = src.get("id", "?")
        for k in ("title", "publisher", "locator"):
            if not isinstance(src.get(k), str) or not src[k].strip():
                errors.append(f"{sid}: {k} required")
        if src.get("access") not in ACCESS:
            errors.append(f"{sid}: invalid access")
        if "video_access" in src and src["video_access"] not in VIDEO_ACCESS:
            errors.append(f"{sid}: invalid video_access")
        try:
            date.fromisoformat(src.get("retrieved", ""))
        except (TypeError, ValueError):
            errors.append(f"{sid}: retrieved date required")
        url = src.get("url", "")
        if url and (not isinstance(url, str) or not re.match(r"https?://", url)):
            errors.append(f"{sid}: url must be HTTP(S) or empty for private input")
    for claim in claims:
        cid = claim.get("id", "?")
        if claim.get("status") not in STATUSES:
            errors.append(f"{cid}: invalid claim status")
        if not isinstance(claim.get("text"), str) or not claim["text"].strip():
            errors.append(f"{cid}: text required")
        links = claim.get("source_ids", [])
        if not isinstance(links, list) or any(not isinstance(x, str) for x in links):
            errors.append(f"{cid}: source_ids must be strings"); links = []
        if any(x not in maps["sources"] for x in links):
            errors.append(f"{cid}: unknown source")
        if claim.get("status") == "verified":
            if not links or not claim.get("locator"):
                errors.append(f"{cid}: verified claim requires sources and exact locator")
            for sid in links:
                src = maps["sources"].get(sid, {})
                if src.get("access") in {"metadata_only", "unavailable"} or src.get("video_access") in {"metadata_only", "unavailable"}:
                    errors.append(f"{cid}: unread source {sid} cannot verify a claim")
        if claim.get("status") == "calculation" and not claim.get("method"):
            errors.append(f"{cid}: calculation requires method and assumptions")
        if claim.get("status") == "unverified":
            warnings.append(f"{cid}: unresolved claim; keep visible qualification")
    seen_appendix, planned, estimated, main_count = False, 0.0, 0.0, 0
    for slide in slides:
        sid = slide.get("id", "?")
        for key in ("title", "role", "takeaway", "speaker_text"):
            if not isinstance(slide.get(key), str) or not slide[key].strip():
                errors.append(f"{sid}: {key} required")
        for key in ("cue", "transition"):
            if not isinstance(slide.get(key, ""), str):
                errors.append(f"{sid}: {key} must be string")
        points = slide.get("points")
        if not isinstance(points, list) or not 1 <= len(points) <= 5 or any(not isinstance(x, str) for x in points):
            errors.append(f"{sid}: 1-5 text points required")
        else:
            if any(display_units(x) > 82 or "\n" in x for x in points):
                errors.append(f"{sid}: baseline layout is too dense; split or use a custom renderer")
        title = slide.get("title", "")
        if isinstance(title, str):
            if display_units(title) > 104:
                errors.append(f"{sid}: title too long for baseline layout")
            if TITLE_END.search(title.strip()) and not slide.get("title_style_exception"):
                (errors if strict_style else warnings).append(f"{sid}: explanatory title ending; review copy")
        if slide.get("kind") not in {"main", "appendix"}:
            errors.append(f"{sid}: kind must be main or appendix")
        if slide.get("kind") == "appendix":
            seen_appendix = True
        elif slide.get("kind") == "main":
            main_count += 1
            if seen_appendix:
                errors.append(f"{sid}: main slide follows appendix")
        if isinstance(slide.get("takeaway"), str) and display_units(slide["takeaway"]) > 140:
            errors.append(f"{sid}: takeaway too long for baseline layout")
        links = slide.get("claim_ids", [])
        if not isinstance(links, list) or any(not isinstance(x, str) for x in links):
            errors.append(f"{sid}: claim_ids must be strings"); links = []
        if any(c not in maps["claims"] for c in links):
            errors.append(f"{sid}: unknown claim")
        secs, pause = slide.get("seconds"), slide.get("pause_seconds", 0)
        if not positive(secs) or not positive(pause, True):
            errors.append(f"{sid}: invalid seconds/pause_seconds"); continue
        if isinstance(slide.get("speaker_text"), str) and isinstance(slide.get("transition", ""), str):
            estimate = spoken_seconds(slide, rate)
            if estimate > secs * 1.25:
                warnings.append(f"{sid}: estimated speech {estimate}s exceeds planned {secs}s")
            if slide.get("kind") == "main":
                planned += secs; estimated += estimate
    if not main_count:
        errors.append("at least one main slide required")
    if planned > duration:
        errors.append(f"main slide budget {planned:g}s exceeds requested {duration:g}s")
    for q in qa:
        if not q.get("question") or not q.get("answer"):
            errors.append("Q&A requires question and answer")
        ref = maps["slides"].get(q.get("appendix_id", ""), {})
        if ref.get("kind") != "appendix":
            errors.append("Q&A must reference an existing appendix slide")
        if not isinstance(q.get("claim_ids", []), list) or any(c not in maps["claims"] for c in q.get("claim_ids", [])):
            errors.append("Q&A: unknown claim")
    return {"errors": errors, "warnings": warnings, "main_slides": main_count,
            "appendix_slides": len(slides) - main_count, "planned_main_seconds": planned,
            "estimated_main_seconds": round(estimated, 1), "speech_rate_assumption": rate,
            "visual_review": "pending", "factual_review": "not_performed_by_code", "rehearsal": "not_performed"}


def check_sync(data: dict, extracted: dict) -> None:
    if signature(data) != extracted.get("slides"):
        raise ValueError("Deck/script mismatch in count, IDs, titles, kind or order")


def claim_note(data: dict, slide: dict, full: bool = False) -> str:
    cm = {c["id"]: c for c in data.get("claims", [])}
    sm = {s["id"]: s for s in data.get("sources", [])}
    lines = []
    for cid in slide.get("claim_ids", []):
        c = cm[cid]
        lines.append(f"[{cid} {LABELS[c['status']]}]" + (f" {c['text']}" if full else ""))
        if full:
            if c.get("method"):
                lines.append("계산·가정: " + c["method"])
            for source_id in c.get("source_ids", []):
                s = sm[source_id]
                lines.append(f"{source_id}: {s['publisher']} | {s['title']} | {c.get('locator') or s['locator']} | {s.get('url', '')} | 확인 {s['retrieved']} ({s['access']})")
    return "\n".join(lines) if full else " · ".join(lines)


def make_pptx(data: dict, path: Path) -> None:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.oxml.xmlchemy import OxmlElement
    prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    prs.core_properties.title = data["company"] + " IR"; prs.core_properties.author = "IR & SCRIPT"
    def text(slide, name, value, x, y, w, h, size, bold=False, color="202320"):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); box.name = name
        tf = box.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = 0
        for i, line in enumerate(value.split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = line; p.font.name = data["font"]; p.font.size = Pt(size); p.font.bold = bold
            p.font.color.rgb = RGBColor.from_string(color); p.space_after = Pt(6)
            for r in p.runs:
                ea = OxmlElement("a:ea"); ea.set("typeface", data["font"]); r._r.get_or_add_rPr().append(ea)
        return box
    for number, s in enumerate(data["slides"], 1):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid(); slide.background.fill.fore_color.rgb = RGBColor.from_string("FAFAF7")
        text(slide, "META", f"{data['company']}  /  {s['id']}  /  {s['role']}", .7, .35, 12, .4, 11)
        text(slide, "TITLE", s["title"], .7, 1.0, 12, 1.35, 30, True)
        text(slide, "TAKEAWAY", s["takeaway"], .7, 2.42, 11.8, .8, 20, False, "525952")
        for i, point in enumerate(s["points"]):
            text(slide, f"POINT_{i}", point, .9, 3.42 + i * .49, 11.5, .48, 19)
        text(slide, "CLAIMS", claim_note(data, s), .7, 6.25, 11.8, .52, 10)
        text(slide, "FOOTER", f"{data['release_date']}   |   {'본문' if s['kind']=='main' else '부록'}   |   {number:02d}", .7, 6.95, 12, .3, 10)
        slide.notes_slide.notes_text_frame.text = (f"[IR_SCRIPT_ID:{s['id']}]\n발표\n{s['speaker_text']}\n\n전환\n{s.get('transition','')}\n\n진행 안내(낭독 제외)\n{s.get('cue','')}\n\n계획 {s['seconds']}초 / 추정 {spoken_seconds(s, data.get('speech_units_per_minute',120))}초\n\n" + claim_note(data, s, True))
    prs.save(path)


def script_files(data: dict, out: Path) -> None:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    doc = Document(); sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = Inches(.72)
    for style in ("Normal", "Title", "Heading 1", "Heading 2"):
        doc.styles[style].font.name = data["font"]
        doc.styles[style]._element.get_or_add_rPr().append(OxmlElement("w:rFonts"))
        doc.styles[style]._element.rPr.rFonts.set(qn("w:eastAsia"), data["font"])
    doc.styles["Normal"].font.size = Pt(11); doc.styles["Normal"].paragraph_format.line_spacing = 1.25
    sec.header.paragraphs[0].text = data["company"] + " / IR & SCRIPT"
    md = [f"# {data['company']} 발표대본", "", "본문만 발표 시간에 포함. 진행 안내·근거는 낭독하지 않습니다. 시간은 가정이며 리허설 결과가 아닙니다.", ""]
    for n, s in enumerate(data["slides"]):
        if n: doc.add_page_break()
        heading = f"[{s['id']}] {s['title']}"
        doc.add_heading(heading, 1)
        doc.add_paragraph(f"{'본문' if s['kind']=='main' else '질의응답 부록'} | 계획 {s['seconds']}초 | 휴지·시연 {s.get('pause_seconds',0)}초 포함")
        for paragraph in s["speaker_text"].split("\n"):
            doc.add_paragraph(paragraph)
        if s.get("transition"): doc.add_paragraph(s["transition"])
        doc.add_heading("진행 안내 · 낭독 제외", 2); doc.add_paragraph(s.get("cue", ""))
        doc.add_heading("근거와 확인 범위", 2); doc.add_paragraph(claim_note(data, s, True))
        md += ["## " + heading, f"<!-- IR_SCRIPT_ID:{s['id']} -->", f"{s['kind']} | 계획 {s['seconds']}초", "", s["speaker_text"], "", s.get("transition", ""), "", "진행: " + s.get("cue", ""), "", claim_note(data,s,True), ""]
    doc.save(out / "script.docx"); (out / "script.md").write_text("\n".join(md), encoding="utf-8")
    qlines = [f"# {data['company']} 예상 질문", ""]
    for q in data.get("qa", []):
        qlines += ["## " + q["question"], q["answer"], f"부록: {q['appendix_id']} | 근거: {', '.join(q.get('claim_ids',[]))}", "남은 확인: " + q.get("uncertainty", "별도 검토"), ""]
    (out / "qa.md").write_text("\n".join(qlines), encoding="utf-8")


def convert_pdf(source: Path, out: Path) -> Path:
    exe = shutil.which("libreoffice") or shutil.which("soffice")
    if not exe: raise RuntimeError("PDF conversion requires LibreOffice/soffice on PATH")
    with tempfile.TemporaryDirectory(prefix="ir-lo-") as profile:
        cmd = [exe, "-env:UserInstallation=" + Path(profile).as_uri(), "--headless", "--convert-to", "pdf", "--outdir", str(out.resolve()), str(source.resolve())]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
        target = out / (source.stem + ".pdf")
        if result.returncode or not target.exists() or target.stat().st_size < 100:
            raise RuntimeError("PDF conversion failed: " + (result.stderr or result.stdout)[-1500:])
        return target


def build(data: dict, out: Path, pdf: bool = False, strict_style: bool = False) -> dict:
    report = lint(data, strict_style)
    if report["errors"]: raise ValueError("\n".join(report["errors"]))
    if out.exists(): raise FileExistsError("Use a new output directory; refusing to overwrite " + str(out))
    out.mkdir(parents=True)
    save(out / "deck.json", data)
    make_pptx(data, out / "deck.pptx"); script_files(data, out)
    with (out / "claims.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle); writer.writerow(["id", "status", "claim", "sources", "locator", "method"])
        # Prevent spreadsheet formula execution when a user opens a research CSV.
        def cell(value):
            t = str(value); return "'" + t if t.lstrip().startswith(("=", "+", "-", "@")) else t
        for c in data.get("claims", []):
            writer.writerow([cell(v) for v in (c["id"], c["status"], c["text"], ",".join(c.get("source_ids",[])), c.get("locator",""), c.get("method",""))])
    if pdf:
        convert_pdf(out / "deck.pptx", out); convert_pdf(out / "script.docx", out)
    save(out / "qa-report.json", report)
    files = {p.name: digest(p) for p in out.iterdir() if p.is_file()}
    save(out / "manifest.json", {"schema_version": 1, "slides": signature(data), "files": files, "note": "Consistency hashes, not tamper-proof signatures."})
    verify(out)
    return report


def verify(out: Path) -> None:
    from pptx import Presentation
    from docx import Document
    manifest = load(out / "manifest.json"); data = load(out / "deck.json")
    required = {"deck.json", "deck.pptx", "script.docx", "script.md", "qa.md", "claims.csv", "qa-report.json"}
    if not required.issubset(manifest.get("files", {})):
        raise ValueError("Manifest is missing required output files")
    for name, expected in manifest["files"].items():
        if Path(name).name != name or not (out / name).is_file() or digest(out / name) != expected:
            raise ValueError("Output missing/changed or unsafe path: " + name)
    check_sync(data, {"slides": manifest["slides"]})
    prs = Presentation(out / "deck.pptx")
    found = []
    for slide in prs.slides:
        match = re.search(r"\[IR_SCRIPT_ID:([^\]]+)\]", slide.notes_slide.notes_text_frame.text)
        titles = [sh.text for sh in slide.shapes if sh.name == "TITLE"]
        found.append((match.group(1) if match else None, titles[0] if len(titles) == 1 else None))
    expected = [(s["id"], s["title"]) for s in data["slides"]]
    if found != expected: raise ValueError("PPTX slide identity/order mismatch")
    headings = [p.text for p in Document(out / "script.docx").paragraphs if p.style.name == "Heading 1"]
    if headings != [f"[{sid}] {title}" for sid, title in expected]:
        raise ValueError("DOCX heading/order mismatch")
    markers = re.findall(r"<!-- IR_SCRIPT_ID:([^>]+) -->", (out / "script.md").read_text(encoding="utf-8"))
    if markers != [sid for sid, _ in expected]: raise ValueError("Markdown order mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="cmd", required=True)
    for cmd in ("lint", "build"):
        p = sub.add_parser(cmd); p.add_argument("input", type=Path); p.add_argument("--strict-style", action="store_true")
        if cmd == "build": p.add_argument("--out", type=Path, required=True); p.add_argument("--pdf", action="store_true")
    p = sub.add_parser("verify"); p.add_argument("out", type=Path)
    p = sub.add_parser("check-sync"); p.add_argument("input", type=Path); p.add_argument("script_manifest", type=Path)
    args = parser.parse_args()
    try:
        if args.cmd == "verify": verify(args.out); print("Output consistency: PASS (not factual/visual verification)")
        elif args.cmd == "check-sync": check_sync(load(args.input), load(args.script_manifest)); print("Slide/script mapping: PASS")
        else:
            data = load(args.input)
            report = lint(data, args.strict_style) if args.cmd == "lint" else build(data, args.out, args.pdf, args.strict_style)
            print(json.dumps(report, ensure_ascii=False, indent=2)); return int(bool(report["errors"]))
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
